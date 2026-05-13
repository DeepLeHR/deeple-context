# 도서 상품 주문/배송 API 설계

## 1. 설계 요약

도서 상품은 기존 주문 도메인과 동일하게 `Order`를 공통 주문/결제 루트로 사용한다.

도서 전용 데이터는 멘토링 구조와 유사하게 별도 도메인 테이블로 분리한다.

```text
Order
 └── Book
      └── BookOrderItem
            └── BookItem
```

### 역할

| 테이블 | 역할 |
| --- | --- |
| `order` | 공통 주문/결제 루트 |
| `book` | 도서 주문의 배송, 송장, 배송비, 배송 상태 |
| `book_item` | 판매 도서 상품 마스터 및 서지 메타데이터 |
| `book_item_image` | 도서 상품 상세/목록 이미지 |
| `book_order_item` | 주문에 포함된 도서 상품 라인 및 주문 당시 상품 스냅샷 |
| `book_digital_benefit` | 도서 구매 후 지급되는 가이드북 열람권 |
| `book_digital_benefit_access_log` | 가이드북 열람 로그 |
| `book_return_request` | 반품/환불 요청 |
| `book_return_evidence_image` | 파손/오배송 증빙 이미지 |
| `book_logistics_deposit` | 김영북스 선입금 예치금 |
| `book_logistics_deposit_history` | 예치금 충전/차감 이력 |

---

## 2. 비즈니스 정책

### 2.1 상품 정책

- `BookItem`은 도서 상품 마스터다.
- 도서 상세 화면에 노출되는 서지 메타데이터는 `book_item`에 저장한다.
- 도서 상품은 목록/상세 노출을 위한 이미지를 여러 개 가질 수 있다.
- 대표 이미지는 상품별 1개만 설정할 수 있다.
- 상품 상세 조회 시 상품 기본 정보와 이미지 목록을 함께 내려준다.
- `price`는 정가다.
- `supply_price`는 기본적으로 정가의 70%다.
- `enabled = false`인 상품은 판매 목록에서 제외한다.
- 재고가 0 이하인 상품은 주문할 수 없다.
- 주문 생성 시 상품명, 정가, 공급가는 `book_order_item`에 스냅샷으로 저장한다.

### 2.2 주문 정책

- 도서 주문 생성 시 기존 `Order`를 생성한다.
- 도서 주문 상세 정보는 `Book`에 저장한다.
- 도서 주문 상품 라인은 `BookOrderItem`에 저장한다.
- 결제 완료 전에는 재고를 확정 차감하지 않는다.
- 결제 완료 시 재고를 차감한다.
- 결제 완료 시 `Order.status = DONE`, `Book.shipping_status = PAYMENT_COMPLETED`로 처리한다.
- 도서 주문명은 단일 상품이면 상품명, 복수 상품이면 `대표상품명 외 N건`으로 저장한다.

### 2.3 배송비 정책

- 배송비는 상품 라인이 아닌 `book`에 저장한다.
- 기본 배송비는 3,000원이다.
- 제주 추가 배송비는 3,000원이다.
- 도서산간 추가 배송비는 5,000원이다.
- 최종 배송비는 `base_shipping_fee + additional_shipping_fee`다.
- 배송비는 전액 유저가 부담한다.
- 추가 배송비는 우편번호 기준으로 계산한다.

### 2.4 배송 정책

- 김영북스 계정은 도서 주문 조회, 운송장 입력, 배송 상태 변경만 가능하다.
- 운송장 번호 입력 시 `shipping_status = SHIPPING`으로 변경한다.
- 배송 시작 시 가이드북 열람권 3개를 자동 지급한다.
- 배송 시작 시 유저에게 앱푸시를 발송한다.
- 배송 완료 처리 시 `shipping_status = DELIVERED`로 변경한다.

### 2.5 취소/환불/반품 정책

- 출고 전 주문만 즉시 취소 가능하다.
- 유저 안내 기준 취소 가능 시간은 오전 09:30까지다.
- 내부 출고 기준 시간은 오전 10:00이다.
- `SHIPPING` 이후에는 주문 취소가 아니라 반품 절차로 처리한다.
- 반품 요청은 수령 후 20일 이내 가능하다.
- 단순변심은 미사용 신조 상태일 때만 환불 가능하다.
- 반품 배송비는 고객 부담이며 선불 원칙이다.
- 착불 반송 시 환불 금액에서 5,000원을 차감한다.
- 파손/오배송/누락은 증빙 이미지 확인 후 재발송 또는 환불 처리한다.
- 파손 증빙 이미지는 표지, 파손 부위, 택배박스 3종이 필수다.

### 2.6 디지털 혜택 정책

- 모든 도서 구매자는 한 결제/배송 건당 가이드북 열람권 3개를 지급받는다.
- 가이드북 열람권은 기존 `guidebook_access` 데이터 3건 생성으로 지급한다.
- 지급 수량은 현재 3개 기준이지만 추후 변경될 수 있다.
- 지급 시점은 배송 시작 시점이다.
- 유효기간은 지급 시점부터 7일이다.
- 열람권 상태는 `ACTIVE`, `REVOKED`로 관리한다.
- 콘텐츠 클릭/조회 시 열람 로그를 저장한다.
- 현재 정책상 콘텐츠 열람 여부는 환불 제한 조건으로 사용하지 않는다.

### 2.7 정산 정책

- 김영북스 정산은 선입금 예치금 차감 방식이다.
- 차감액은 `공급가 합계 + 실제 배송 원가`다.
- 실제 배송 원가는 포장비/VAT 포함 금액을 저장한다.
- 정산 처리 시 예치금 차감 이력을 저장한다.

---

## 3. DDL

### 3.1 기존 ProductType 수정

```java
public enum ProductType {
    CAMPAIGN,
    HUMAN_POOL,
    SPEC_REPORT,
    SPEC_REPORT_V2,
    MENTORING,
    BOOK,
}
```

### 3.2 도서 상품 마스터

```sql
CREATE TABLE book_item (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    subtitle VARCHAR(500),
    description TEXT,
    table_of_contents TEXT,
    keyword VARCHAR(1000),
    publisher VARCHAR(100),
    author VARCHAR(100),
    category VARCHAR(500),
    publication_date DATE,
    isbn VARCHAR(30),
    book_size VARCHAR(50),
    page_count INT,
    preview_url VARCHAR(1000),
    price INT NOT NULL,
    supply_price INT NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    code VARCHAR(100),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_time DATETIME NOT NULL,
    updated_time DATETIME NOT NULL
);
```

#### book_item 컬럼 설명

| 컬럼 | 설명 |
| --- | --- |
| `name` | 도서명 |
| `subtitle` | 부제 또는 홍보 문구 |
| `description` | 책 소개 |
| `table_of_contents` | 목차 |
| `keyword` | 검색/노출 키워드 |
| `publisher` | 출판사 |
| `author` | 저자/편저자 |
| `category` | 도서 카테고리 |
| `publication_date` | 출간일 |
| `isbn` | ISBN |
| `book_size` | 판형/크기 |
| `page_count` | 쪽수 |
| `preview_url` | 미리보기 PDF 또는 파일 URL |
| `price` | 정가 |
| `supply_price` | 공급가 |
| `stock_quantity` | 판매 가능 재고 |

### 3.3 도서 상품 이미지

```sql
CREATE TABLE book_item_image (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    book_item_id BIGINT NOT NULL,
    image_url VARCHAR(1000) NOT NULL,
    display_order INT NOT NULL DEFAULT 0,
    representative BOOLEAN NOT NULL DEFAULT FALSE,
    created_time DATETIME NOT NULL,
    updated_time DATETIME NOT NULL,

    CONSTRAINT fk_book_item_image_book_item
        FOREIGN KEY (book_item_id) REFERENCES book_item(id)
);
```

### 3.4 도서 주문

```sql
CREATE TABLE book (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    recipient_name VARCHAR(100) NOT NULL,
    recipient_phone VARCHAR(30) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    address_detail VARCHAR(255) NOT NULL,

    base_shipping_fee INT NOT NULL DEFAULT 3000,
    additional_shipping_fee INT NOT NULL DEFAULT 0,
    total_shipping_fee INT NOT NULL,

    tracking_number VARCHAR(100),
    shipping_status VARCHAR(30) NOT NULL,

    shipped_time DATETIME,
    delivered_time DATETIME,

    created_time DATETIME NOT NULL,
    updated_time DATETIME NOT NULL,

    CONSTRAINT fk_book_order
        FOREIGN KEY (order_id) REFERENCES `order`(id),

    CONSTRAINT fk_book_user
        FOREIGN KEY (user_id) REFERENCES user(id)
);
```

### 3.5 도서 주문 상품 라인

```sql
CREATE TABLE book_order_item (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    book_id BIGINT NOT NULL,
    book_item_id BIGINT NOT NULL,

    product_name VARCHAR(255) NOT NULL,
    product_price INT NOT NULL,
    supply_price INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,

    created_time DATETIME NOT NULL,
    updated_time DATETIME NOT NULL,

    CONSTRAINT fk_book_order_item_book
        FOREIGN KEY (book_id) REFERENCES book(id),

    CONSTRAINT fk_book_order_item_book_item
        FOREIGN KEY (book_item_id) REFERENCES book_item(id)
);
```

### 3.6 디지털 혜택

가이드북 열람권은 신규 `book_digital_benefit` 테이블이 아니라 기존 `guidebook_access`에 3건 생성하는 방식으로 지급한다.

아래 테이블은 도서 주문과 가이드북 지급 이력을 명시적으로 연결해야 할 경우에만 추가 검토한다.

```sql
CREATE TABLE book_digital_benefit (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    book_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    guidebook_id BIGINT NOT NULL,
    benefit_status VARCHAR(30) NOT NULL,
    expires_time DATETIME NOT NULL,
    granted_time DATETIME NOT NULL,
    revoked_time DATETIME,

    CONSTRAINT fk_book_digital_benefit_book
        FOREIGN KEY (book_id) REFERENCES book(id),

    CONSTRAINT fk_book_digital_benefit_user
        FOREIGN KEY (user_id) REFERENCES user(id)
);
```

```sql
CREATE TABLE book_digital_benefit_access_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    book_digital_benefit_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    guidebook_id BIGINT NOT NULL,
    accessed_time DATETIME NOT NULL,

    CONSTRAINT fk_book_digital_benefit_access_log_benefit
        FOREIGN KEY (book_digital_benefit_id) REFERENCES book_digital_benefit(id),

    CONSTRAINT fk_book_digital_benefit_access_log_user
        FOREIGN KEY (user_id) REFERENCES user(id)
);
```

### 3.7 반품/환불

```sql
CREATE TABLE book_return_request (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    book_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    return_reason VARCHAR(30) NOT NULL,
    return_status VARCHAR(30) NOT NULL,
    user_memo VARCHAR(1000),
    admin_memo VARCHAR(1000),

    prepaid_shipping BOOLEAN,
    collect_shipping_deduct_amount INT NOT NULL DEFAULT 0,
    refund_amount INT,

    requested_time DATETIME NOT NULL,
    approved_time DATETIME,
    rejected_time DATETIME,
    completed_time DATETIME,

    CONSTRAINT fk_book_return_request_book
        FOREIGN KEY (book_id) REFERENCES book(id),

    CONSTRAINT fk_book_return_request_user
        FOREIGN KEY (user_id) REFERENCES user(id)
);
```

```sql
CREATE TABLE book_return_evidence_image (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    book_return_request_id BIGINT NOT NULL,
    image_type VARCHAR(30) NOT NULL,
    image_url VARCHAR(1000) NOT NULL,
    created_time DATETIME NOT NULL,

    CONSTRAINT fk_book_return_evidence_image_return_request
        FOREIGN KEY (book_return_request_id) REFERENCES book_return_request(id)
);
```

### 3.8 정산/예치금

```sql
CREATE TABLE book_logistics_deposit (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    partner_name VARCHAR(100) NOT NULL,
    initial_balance INT NOT NULL DEFAULT 0,
    current_balance INT NOT NULL DEFAULT 0,
    created_time DATETIME NOT NULL,
    updated_time DATETIME NOT NULL
);
```

```sql
CREATE TABLE book_logistics_deposit_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    book_logistics_deposit_id BIGINT NOT NULL,
    book_id BIGINT,
    transaction_type VARCHAR(30) NOT NULL,
    amount INT NOT NULL,
    balance_after INT NOT NULL,
    actual_shipping_cost INT,
    description VARCHAR(500),
    settled_time DATETIME NOT NULL,

    CONSTRAINT fk_book_logistics_deposit_history_deposit
        FOREIGN KEY (book_logistics_deposit_id) REFERENCES book_logistics_deposit(id),

    CONSTRAINT fk_book_logistics_deposit_history_book
        FOREIGN KEY (book_id) REFERENCES book(id)
);
```

---

## 4. Enum

### 4.1 BookShippingStatus

```java
public enum BookShippingStatus {
    PAYMENT_COMPLETED("결제완료"),
    PREPARING_SHIPMENT("배송준비"),
    SHIPPING("배송중"),
    DELIVERED("배송완료"),
    REFUND_REQUESTED("환불요청"),
    REFUNDED("환불완료"),
    CANCELED("취소");
}
```

### 4.2 BookBenefitStatus

```java
public enum BookBenefitStatus {
    ACTIVE("활성"),
    REVOKED("회수");
}
```

### 4.3 BookReturnReason

```java
public enum BookReturnReason {
    CHANGE_OF_MIND("단순변심"),
    DAMAGED("파손"),
    WRONG_DELIVERY("오배송"),
    MISSING_ITEM("누락"),
    ETC("기타");
}
```

### 4.4 BookReturnStatus

```java
public enum BookReturnStatus {
    REQUESTED("요청"),
    APPROVED("승인"),
    REJECTED("거절"),
    RETURN_SHIPPING("반송중"),
    RETURN_RECEIVED("반송완료"),
    REFUNDED("환불완료");
}
```

### 4.5 BookEvidenceImageType

```java
public enum BookEvidenceImageType {
    COVER("표지"),
    DAMAGED_PART("파손부위"),
    SHIPPING_BOX("택배박스");
}
```

### 4.6 BookDepositTransactionType

```java
public enum BookDepositTransactionType {
    CHARGE("충전"),
    DEDUCT("차감"),
    REFUND("환급"),
    ADJUSTMENT("조정");
}
```

---

## 5. API 리스트

### 5.1 도서 상품 API

| Method | Endpoint | 설명 | 권한 |
| --- | --- | --- | --- |
| `GET` | `/api/v4/book-items` | 도서 상품 목록 조회 | User |
| `GET` | `/api/v4/book-items/{bookItemId}` | 도서 상품 상세 조회 | User |
| `POST` | `/api/v4/admin/book-items` | 도서 상품 등록 | Admin |
| `PATCH` | `/api/v4/admin/book-items/{bookItemId}` | 도서 상품 수정 | Admin |
| `PATCH` | `/api/v4/admin/book-items/{bookItemId}/stock` | 도서 재고 수정 | Admin |
| `PATCH` | `/api/v4/admin/book-items/{bookItemId}/enable` | 도서 판매 활성화 | Admin |
| `PATCH` | `/api/v4/admin/book-items/{bookItemId}/disable` | 도서 판매 비활성화 | Admin |
| `GET` | `/api/v4/admin/book-items/{bookItemId}/images` | 도서 상품 이미지 목록 조회 | Admin |
| `POST` | `/api/v4/admin/book-items/{bookItemId}/images` | 도서 상품 이미지 등록 | Admin |
| `PATCH` | `/api/v4/admin/book-item-images/{bookItemImageId}` | 도서 상품 이미지 수정 | Admin |
| `DELETE` | `/api/v4/admin/book-item-images/{bookItemImageId}` | 도서 상품 이미지 삭제 | Admin |

### 5.2 도서 주문 API

| Method | Endpoint | 설명 | 권한 |
| --- | --- | --- | --- |
| `POST` | `/api/v4/books/shipping-fee` | 우편번호 기준 배송비 계산 | User |
| `POST` | `/api/v4/orders/books` | 도서 바로구매 주문 생성 | User |
| `GET` | `/api/v4/books` | 내 도서 주문 목록 조회 | User |
| `GET` | `/api/v4/books/{bookId}` | 도서 주문 상세 조회 | User |
| `GET` | `/api/v4/book-payments` | 내 도서 결제 목록 조회 | User |
| `GET` | `/api/v4/book-payments/{orderId}` | 내 도서 결제 상세 조회 | User |
| `POST` | `/api/v4/books/{bookId}/cancel` | 출고 전 주문 취소 | User |

### 5.3 물류 API

| Method | Endpoint | 설명 | 권한 |
| --- | --- | --- | --- |
| `GET` | `/api/v4/logistics/books` | 김영북스 출고 대상 주문 목록 조회 | Logistics |
| `GET` | `/api/v4/logistics/books/{bookId}` | 김영북스 주문 상세 조회 | Logistics |
| `PATCH` | `/api/v4/logistics/books/{bookId}/tracking-number` | 운송장 번호 입력 | Logistics |
| `PATCH` | `/api/v4/logistics/books/{bookId}/shipping-status` | 배송 상태 변경 | Logistics |

### 5.4 관리자 주문/CS API

| Method | Endpoint | 설명 | 권한 |
| --- | --- | --- | --- |
| `GET` | `/api/v4/admin/books` | 도서 주문 목록 조회 | Admin |
| `GET` | `/api/v4/admin/books/{bookId}` | 도서 주문 상세 조회 | Admin |
| `PATCH` | `/api/v4/admin/books/{bookId}/shipping-status` | 배송 상태 변경 | Admin |
| `POST` | `/api/v4/books/{bookId}/return-requests` | 반품/환불 요청 | User |
| `GET` | `/api/v4/admin/book-return-requests` | 반품/환불 요청 목록 조회 | Admin |
| `GET` | `/api/v4/admin/book-return-requests/{returnRequestId}` | 반품/환불 상세 조회 | Admin |
| `PATCH` | `/api/v4/admin/book-return-requests/{returnRequestId}/approve` | 반품 승인 | Admin |
| `PATCH` | `/api/v4/admin/book-return-requests/{returnRequestId}/reject` | 반품 거절 | Admin |
| `PATCH` | `/api/v4/admin/book-return-requests/{returnRequestId}/complete` | 환불 완료 | Admin |
| `POST` | `/api/v4/book-return-requests/{returnRequestId}/evidence-images` | 증빙 이미지 등록 | User |

### 5.5 디지털 혜택 API

| Method | Endpoint | 설명 | 권한 |
| --- | --- | --- | --- |
| `GET` | `/api/v4/books/{bookId}/benefits` | 지급된 가이드북 혜택 조회 | User |
| `POST` | `/api/v4/admin/books/{bookId}/benefits/grant` | 가이드북 혜택 수동 지급 | Admin |
| `PATCH` | `/api/v4/admin/book-benefits/{benefitId}/revoke` | 가이드북 혜택 회수 | Admin |
| `POST` | `/api/v4/guidebooks/{guidebookId}/access-log` | 가이드북 열람 로그 저장 | User |
| `GET` | `/api/v4/admin/book-benefits` | 도서 혜택 지급 내역 조회 | Admin |

### 5.6 앱푸시 API

| Method | Endpoint | 설명 | 권한 |
| --- | --- | --- | --- |
| `POST` | `/api/v4/admin/books/{bookId}/shipping-push` | 배송 시작 앱푸시 수동 재발송 | Admin |

### 5.7 정산 API

| Method | Endpoint | 설명 | 권한 |
| --- | --- | --- | --- |
| `GET` | `/api/v4/admin/book-settlements/deposit` | 김영북스 예치금 조회 | Admin |
| `POST` | `/api/v4/admin/book-settlements/deposit/charge` | 예치금 충전 | Admin |
| `GET` | `/api/v4/admin/book-settlements/histories` | 정산 이력 조회 | Admin |
| `POST` | `/api/v4/admin/books/{bookId}/settle` | 도서 주문 정산 처리 | Admin |

---

## 6. API 상세 스펙

### 6.1 도서 상품 목록 조회

```http
GET /api/v4/book-items
```

#### Query

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `enabled` | Boolean | N | 판매 활성 여부 |
| `page` | Integer | N | 페이지 번호 |
| `size` | Integer | N | 페이지 크기 |

#### Response

```json
{
  "items": [
    {
      "bookItemId": 1,
      "name": "직8딴 교재",
      "subtitle": "15개년치 기출중복문제 소거 정리",
      "price": 30000,
      "publisher": "김영북스",
      "author": "김진태",
      "publicationDate": "2026-03-01",
      "isbn": "979-11-7349-137-5",
      "stockQuantity": 100,
      "code": "BOOK-JIK8",
      "enabled": true,
      "representativeImageUrl": "https://example.com/images/book-main.jpg"
    }
  ],
  "page": 0,
  "size": 20,
  "totalCount": 1
}
```

### 6.2 도서 상품 상세 조회

```http
GET /api/v4/book-items/{bookItemId}
```

#### Response

```json
{
  "bookItemId": 1,
  "name": "직8딴 교재",
  "subtitle": "15개년치 기출중복문제 소거 정리",
  "description": "불필요한 내용은 줄이고 핵심 학습 로드맵으로 구성한 실전형 수험서입니다.",
  "tableOfContents": "00. 필독\n01. 기출 중복문제 소거 정리\n02. 필답형 기출문제",
  "keyword": "산업안전기사, 기사, 자격증, 김영북스",
  "publisher": "김영북스",
  "author": "김진태",
  "category": "국내도서 > 수험서 자격증 > 한국산업인력공단 > 안전관리분야",
  "publicationDate": "2026-03-01",
  "isbn": "979-11-7349-137-5",
  "bookSize": "188*257",
  "pageCount": 456,
  "previewUrl": "https://example.com/previews/book-preview.pdf",
  "price": 30000,
  "stockQuantity": 100,
  "code": "BOOK-JIK8",
  "enabled": true,
  "images": [
    {
      "bookItemImageId": 1,
      "imageUrl": "https://example.com/images/book-main.jpg",
      "displayOrder": 1,
      "representative": true
    },
    {
      "bookItemImageId": 2,
      "imageUrl": "https://example.com/images/book-detail.jpg",
      "displayOrder": 2,
      "representative": false
    }
  ]
}
```

### 6.3 도서 상품 등록

```http
POST /api/v4/admin/book-items
```

#### Request

```json
{
  "name": "직8딴 교재",
  "subtitle": "15개년치 기출중복문제 소거 정리",
  "description": "불필요한 내용은 줄이고 핵심 학습 로드맵으로 구성한 실전형 수험서입니다.",
  "tableOfContents": "00. 필독\n01. 기출 중복문제 소거 정리\n02. 필답형 기출문제",
  "keyword": "산업안전기사, 기사, 자격증, 김영북스",
  "publisher": "김영북스",
  "author": "김진태",
  "category": "국내도서 > 수험서 자격증 > 한국산업인력공단 > 안전관리분야",
  "publicationDate": "2026-03-01",
  "isbn": "979-11-7349-137-5",
  "bookSize": "188*257",
  "pageCount": 456,
  "previewUrl": "https://example.com/previews/book-preview.pdf",
  "price": 30000,
  "stockQuantity": 100,
  "code": "BOOK-JIK8",
  "enabled": true
}
```

#### Rules

- `supplyPrice = price * 0.7`로 계산한다.
- `price`는 0보다 커야 한다.
- `stockQuantity`는 0 이상이어야 한다.

#### Response

```json
{
  "bookItemId": 1
}
```

### 6.4 도서 상품 이미지 목록 조회

```http
GET /api/v4/admin/book-items/{bookItemId}/images
```

#### Response

```json
{
  "items": [
    {
      "bookItemImageId": 1,
      "imageUrl": "https://example.com/images/book-main.jpg",
      "displayOrder": 1,
      "representative": true
    },
    {
      "bookItemImageId": 2,
      "imageUrl": "https://example.com/images/book-detail.jpg",
      "displayOrder": 2,
      "representative": false
    }
  ]
}
```

### 6.5 도서 상품 이미지 등록

```http
POST /api/v4/admin/book-items/{bookItemId}/images
```

#### Request

```json
{
  "imageUrl": "https://example.com/images/book-main.jpg",
  "displayOrder": 1,
  "representative": true
}
```

#### Rules

- `imageUrl`은 필수다.
- `displayOrder`가 낮을수록 먼저 노출한다.
- `representative = true`로 등록하면 기존 대표 이미지는 `false`로 변경한다.
- 상품별 대표 이미지는 1개만 허용한다.

#### Response

```json
{
  "bookItemImageId": 1
}
```

### 6.6 도서 상품 이미지 수정

```http
PATCH /api/v4/admin/book-item-images/{bookItemImageId}
```

#### Request

```json
{
  "imageUrl": "https://example.com/images/book-main-updated.jpg",
  "displayOrder": 1,
  "representative": true
}
```

#### Rules

- `representative = true`로 수정하면 같은 상품의 기존 대표 이미지는 `false`로 변경한다.
- 이미지 삭제 없이 노출 순서만 변경할 수 있다.

#### Response

```json
{
  "bookItemImageId": 1,
  "imageUrl": "https://example.com/images/book-main-updated.jpg",
  "displayOrder": 1,
  "representative": true
}
```

### 6.7 도서 상품 이미지 삭제

```http
DELETE /api/v4/admin/book-item-images/{bookItemImageId}
```

#### Rules

- 대표 이미지를 삭제할 수 있다.
- 대표 이미지 삭제 후 자동 대표 이미지 지정 여부는 정책 확정이 필요하다.
- DB 레코드 삭제 방식 또는 soft delete 방식은 기존 이미지 관리 정책을 따른다.

#### Response

```json
{
  "bookItemImageId": 1,
  "deleted": true
}
```

### 6.8 도서 상품 수정

```http
PATCH /api/v4/admin/book-items/{bookItemId}
```

#### Request

```json
{
  "name": "직8딴 교재 개정판",
  "subtitle": "15개년치 기출중복문제 소거 정리",
  "description": "개정판 소개 문구입니다.",
  "tableOfContents": "00. 필독\n01. 기출 중복문제 소거 정리",
  "keyword": "산업안전기사, 기사, 자격증, 김영북스",
  "publisher": "김영북스",
  "author": "김진태",
  "category": "국내도서 > 수험서 자격증 > 한국산업인력공단 > 안전관리분야",
  "publicationDate": "2026-03-01",
  "isbn": "979-11-7349-137-5",
  "bookSize": "188*257",
  "pageCount": 456,
  "previewUrl": "https://example.com/previews/book-preview.pdf",
  "price": 32000,
  "code": "BOOK-JIK8-REV",
  "enabled": true
}
```

#### Rules

- 상품 가격 변경은 기존 주문의 `book_order_item` 스냅샷에 영향을 주지 않는다.
- 가격 변경 시 `supplyPrice = price * 0.7`로 재계산한다.

### 6.9 재고 수정

```http
PATCH /api/v4/admin/book-items/{bookItemId}/stock
```

#### Request

```json
{
  "stockQuantity": 120
}
```

### 6.10 배송비 계산

```http
POST /api/v4/books/shipping-fee
```

#### Request

```json
{
  "zipCode": "63243"
}
```

#### Response

```json
{
  "baseShippingFee": 3000,
  "additionalShippingFee": 3000,
  "totalShippingFee": 6000,
  "shippingAreaType": "JEJU"
}
```

#### shippingAreaType

| 값 | 설명 | 추가 배송비 |
| --- | --- | --- |
| `NORMAL` | 일반 지역 | 0 |
| `JEJU` | 제주 | 3,000 |
| `REMOTE_AREA` | 도서산간 | 5,000 |

### 6.11 도서 주문 생성

```http
POST /api/v4/orders/books
```

#### Request

```json
{
  "items": [
    {
      "bookItemId": 1,
      "quantity": 2
    }
  ],
  "shippingAddress": {
    "recipientName": "홍길동",
    "recipientPhone": "01012345678",
    "zipCode": "06234",
    "address": "서울특별시 강남구 테헤란로 1",
    "addressDetail": "101동 1001호"
  }
}
```

#### Rules

- 상품은 1개 이상이어야 한다.
- 각 상품의 수량은 1 이상이어야 한다.
- `enabled = false`인 상품은 주문할 수 없다.
- 재고가 부족한 상품은 주문할 수 없다.
- 배송비는 서버에서 우편번호 기준으로 재계산한다.
- 주문 생성 시 `Order`, `Book`, `BookOrderItem`을 함께 생성한다.
- 결제 완료 시 재고를 차감한다.

#### Response

```json
{
  "orderId": 500,
  "bookId": 1000,
  "orderName": "직8딴 교재",
  "productAmount": 60000,
  "baseShippingFee": 3000,
  "additionalShippingFee": 0,
  "totalShippingFee": 3000,
  "totalPaymentAmount": 63000,
  "shippingStatus": "PAYMENT_COMPLETED"
}
```

### 6.12 내 도서 주문 목록 조회

```http
GET /api/v4/books
```

#### Query

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `shippingStatus` | String | N | 배송 상태 |
| `page` | Integer | N | 페이지 번호 |
| `size` | Integer | N | 페이지 크기 |

#### Response

```json
{
  "items": [
    {
      "bookId": 1000,
      "orderId": 500,
      "orderName": "직8딴 교재",
      "shippingStatus": "PAYMENT_COMPLETED",
      "totalPaymentAmount": 63000,
      "createdTime": "2026-05-12T10:00:00"
    }
  ],
  "page": 0,
  "size": 20,
  "totalCount": 1
}
```

### 6.13 도서 주문 상세 조회

```http
GET /api/v4/books/{bookId}
```

#### Response

```json
{
  "bookId": 1000,
  "orderId": 500,
  "orderName": "직8딴 교재",
  "orderStatus": "DONE",
  "shippingStatus": "PAYMENT_COMPLETED",
  "items": [
    {
      "bookItemId": 1,
      "productName": "직8딴 교재",
      "productPrice": 30000,
      "quantity": 2,
      "totalPrice": 60000
    }
  ],
  "shippingAddress": {
    "recipientName": "홍길동",
    "recipientPhone": "01012345678",
    "zipCode": "06234",
    "address": "서울특별시 강남구 테헤란로 1",
    "addressDetail": "101동 1001호"
  },
  "shippingFee": {
    "baseShippingFee": 3000,
    "additionalShippingFee": 0,
    "totalShippingFee": 3000
  },
  "trackingNumber": null,
  "shippedTime": null,
  "deliveredTime": null
}
```

### 6.14 내 도서 결제 목록 조회

```http
GET /api/v4/book-payments
```

#### Query

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `paymentStatus` | String | N | 결제 상태 |
| `fromDate` | String | N | 결제 시작일 |
| `toDate` | String | N | 결제 종료일 |
| `page` | Integer | N | 페이지 번호 |
| `size` | Integer | N | 페이지 크기 |

#### Response

```json
{
  "items": [
    {
      "orderId": 500,
      "bookId": 1000,
      "orderName": "직8딴 교재",
      "paymentStatus": "DONE",
      "paymentMethod": "CARD",
      "productAmount": 60000,
      "shippingFee": 3000,
      "discountAmount": 0,
      "totalPaymentAmount": 63000,
      "paidTime": "2026-05-12T10:00:00",
      "shippingStatus": "PAYMENT_COMPLETED"
    }
  ],
  "page": 0,
  "size": 20,
  "totalCount": 1
}
```

### 6.15 내 도서 결제 상세 조회

```http
GET /api/v4/book-payments/{orderId}
```

#### Response

```json
{
  "orderId": 500,
  "bookId": 1000,
  "orderName": "직8딴 교재",
  "orderStatus": "DONE",
  "payment": {
    "paymentId": 900,
    "paymentStatus": "DONE",
    "paymentMethod": "CARD",
    "productAmount": 60000,
    "shippingFee": 3000,
    "discountAmount": 0,
    "totalPaymentAmount": 63000,
    "paidTime": "2026-05-12T10:00:00"
  },
  "items": [
    {
      "bookItemId": 1,
      "productName": "직8딴 교재",
      "productPrice": 30000,
      "quantity": 2,
      "totalPrice": 60000
    }
  ],
  "shipping": {
    "shippingStatus": "PAYMENT_COMPLETED",
    "trackingNumber": null,
    "shippedTime": null,
    "deliveredTime": null
  }
}
```

#### Rules

- 본인의 도서 주문 결제 건만 조회할 수 있다.
- 결제 금액은 기존 `OrderPayment` 기준으로 내려준다.
- 배송비는 `Book.total_shipping_fee` 기준으로 내려준다.

### 6.16 주문 취소

```http
POST /api/v4/books/{bookId}/cancel
```

#### Rules

- `shipping_status`가 `PAYMENT_COMPLETED` 또는 `PREPARING_SHIPMENT`일 때만 취소 가능하다.
- `SHIPPING` 이후에는 취소할 수 없다.
- 취소 성공 시 `Order.status = CANCELED`, `Book.shipping_status = CANCELED`로 변경한다.
- 결제 완료 후 취소라면 재고를 복구한다.

#### Response

```json
{
  "bookId": 1000,
  "orderId": 500,
  "shippingStatus": "CANCELED"
}
```

### 6.17 물류 주문 목록 조회

```http
GET /api/v4/logistics/books
```

#### Query

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `shippingStatus` | String | N | 배송 상태 |
| `fromDate` | String | N | 주문 시작일 |
| `toDate` | String | N | 주문 종료일 |
| `page` | Integer | N | 페이지 번호 |
| `size` | Integer | N | 페이지 크기 |

#### Response

```json
{
  "items": [
    {
      "bookId": 1000,
      "orderId": 500,
      "orderName": "직8딴 교재",
      "recipientName": "홍길동",
      "recipientPhone": "01012345678",
      "zipCode": "06234",
      "address": "서울특별시 강남구 테헤란로 1",
      "addressDetail": "101동 1001호",
      "shippingStatus": "PAYMENT_COMPLETED",
      "trackingNumber": null
    }
  ],
  "page": 0,
  "size": 20,
  "totalCount": 1
}
```

### 6.18 운송장 번호 입력

```http
PATCH /api/v4/logistics/books/{bookId}/tracking-number
```

#### Request

```json
{
  "trackingNumber": "1234567890"
}
```

#### Rules

- 운송장 번호 입력 시 `shipping_status = SHIPPING`으로 변경한다.
- `shipped_time`을 현재 시각으로 저장한다.
- 배송 시작 시 가이드북 열람권 3개를 지급한다.
- 배송 시작 시 유저에게 앱푸시를 발송한다.
- 이미 열람권이 지급된 주문에는 중복 지급하지 않는다.
- 이미 배송 시작 앱푸시가 발송된 주문에는 중복 발송하지 않는다.

#### Response

```json
{
  "bookId": 1000,
  "trackingNumber": "1234567890",
  "shippingStatus": "SHIPPING",
  "shippedTime": "2026-05-12T10:30:00"
}
```

### 6.19 배송 시작 앱푸시 발송 로직

배송 시작 앱푸시는 별도 외부 공개 API라기보다, 운송장 입력 또는 배송 상태 변경 트랜잭션 안에서 호출되는 내부 로직이다.

#### Trigger

```text
Book.shippingStatus: PAYMENT_COMPLETED 또는 PREPARING_SHIPMENT
-> SHIPPING 변경 시
```

#### Push Payload

```json
{
  "userId": 10,
  "title": "도서 배송이 시작됐어요",
  "body": "주문하신 직8딴 교재가 배송 중입니다.",
  "targetType": "BOOK",
  "targetId": 1000,
  "metadata": {
    "bookId": 1000,
    "orderId": 500,
    "trackingNumber": "1234567890"
  }
}
```

#### Rules

- 운송장 번호 입력 완료 후 발송한다.
- `SHIPPING` 상태로 최초 변경되는 시점에만 발송한다.
- 푸시 발송 실패가 배송 상태 변경을 롤백시키지 않도록 분리 처리를 권장한다.
- 실패한 푸시는 재시도 또는 관리자 수동 재발송 대상으로 남긴다.
- 푸시 발송 이력 테이블이 이미 있다면 기존 이력 구조를 사용한다.

#### Manual Resend API

```http
POST /api/v4/admin/books/{bookId}/shipping-push
```

#### Response

```json
{
  "bookId": 1000,
  "sent": true,
  "sentTime": "2026-05-12T10:31:00"
}
```

### 6.20 배송 상태 변경

```http
PATCH /api/v4/logistics/books/{bookId}/shipping-status
```

#### Request

```json
{
  "shippingStatus": "DELIVERED"
}
```

#### Rules

- `DELIVERED` 변경 시 `delivered_time`을 현재 시각으로 저장한다.
- 김영북스는 배송 관련 상태만 변경할 수 있다.
- `SHIPPING`으로 변경되면서 운송장 번호가 이미 존재하면 배송 시작 앱푸시를 발송한다.

### 6.21 반품/환불 요청

```http
POST /api/v4/books/{bookId}/return-requests
```

#### Request

```json
{
  "returnReason": "DAMAGED",
  "userMemo": "택배 수령 시 표지가 파손되어 있었습니다.",
  "prepaidShipping": true
}
```

#### Rules

- 배송 완료 후 20일 이내 요청 가능하다.
- 파손/오배송/누락은 증빙 이미지가 필요하다.
- 반품 요청 시 `Book.shipping_status = REFUND_REQUESTED`로 변경한다.

#### Response

```json
{
  "returnRequestId": 10,
  "bookId": 1000,
  "returnStatus": "REQUESTED"
}
```

### 6.22 증빙 이미지 등록

```http
POST /api/v4/book-return-requests/{returnRequestId}/evidence-images
```

#### Request

```json
{
  "images": [
    {
      "imageType": "COVER",
      "imageUrl": "https://example.com/images/cover.jpg"
    },
    {
      "imageType": "DAMAGED_PART",
      "imageUrl": "https://example.com/images/damaged.jpg"
    },
    {
      "imageType": "SHIPPING_BOX",
      "imageUrl": "https://example.com/images/box.jpg"
    }
  ]
}
```

#### Rules

- 파손 사유는 `COVER`, `DAMAGED_PART`, `SHIPPING_BOX` 3종이 필수다.

### 6.23 반품 승인

```http
PATCH /api/v4/admin/book-return-requests/{returnRequestId}/approve
```

#### Request

```json
{
  "adminMemo": "증빙 확인 완료. 반품 승인합니다."
}
```

#### Response

```json
{
  "returnRequestId": 10,
  "returnStatus": "APPROVED"
}
```

### 6.24 반품 거절

```http
PATCH /api/v4/admin/book-return-requests/{returnRequestId}/reject
```

#### Request

```json
{
  "adminMemo": "수령 후 20일이 지나 반품이 어렵습니다."
}
```

#### Response

```json
{
  "returnRequestId": 10,
  "returnStatus": "REJECTED"
}
```

### 6.25 환불 완료

```http
PATCH /api/v4/admin/book-return-requests/{returnRequestId}/complete
```

#### Request

```json
{
  "refundAmount": 58000,
  "collectShippingDeductAmount": 5000,
  "adminMemo": "착불 배송비 5,000원 차감 후 환불 완료"
}
```

#### Rules

- 착불 반송이면 `collectShippingDeductAmount = 5000`을 기록한다.
- 환불 완료 시 `Book.shipping_status = REFUNDED`로 변경한다.
- 필요 시 도서 열람권을 `REVOKED` 처리한다.

### 6.26 지급 혜택 조회

```http
GET /api/v4/books/{bookId}/benefits
```

#### Response

```json
{
  "items": [
    {
      "benefitId": 1,
      "guidebookId": 101,
      "benefitStatus": "ACTIVE",
      "grantedTime": "2026-05-12T10:30:00",
      "expiresTime": "2026-05-19T10:30:00",
      "accessed": false
    }
  ]
}
```

### 6.27 가이드북 혜택 수동 지급

```http
POST /api/v4/admin/books/{bookId}/benefits/grant
```

#### Request

```json
{
  "guidebookIds": [101, 102, 103]
}
```

#### Rules

- 동일 주문에 동일 가이드북 혜택을 중복 지급하지 않는다.
- 만료일은 지급 시점부터 7일로 계산한다.

### 6.28 가이드북 혜택 회수

```http
PATCH /api/v4/admin/book-benefits/{benefitId}/revoke
```

#### Response

```json
{
  "benefitId": 1,
  "benefitStatus": "REVOKED",
  "revokedTime": "2026-05-12T12:00:00"
}
```

### 6.29 가이드북 열람 로그 저장

```http
POST /api/v4/guidebooks/{guidebookId}/access-log
```

#### Request

```json
{
  "benefitId": 1
}
```

#### Rules

- 혜택 상태가 `ACTIVE`여야 한다.
- 만료 시간이 지나면 열람할 수 없다.
- 열람 시 access log를 저장한다.

### 6.30 예치금 조회

```http
GET /api/v4/admin/book-settlements/deposit
```

#### Response

```json
{
  "depositId": 1,
  "partnerName": "김영북스",
  "initialBalance": 10000000,
  "currentBalance": 9500000
}
```

### 6.31 예치금 충전

```http
POST /api/v4/admin/book-settlements/deposit/charge
```

#### Request

```json
{
  "amount": 1000000,
  "description": "5월 예치금 충전"
}
```

#### Response

```json
{
  "depositId": 1,
  "currentBalance": 10500000
}
```

### 6.32 도서 주문 정산 처리

```http
POST /api/v4/admin/books/{bookId}/settle
```

#### Request

```json
{
  "actualShippingCost": 3080,
  "description": "직8딴 교재 출고 정산"
}
```

#### Rules

- 차감액은 `공급가 합계 + actualShippingCost`다.
- 공급가 합계는 `SUM(book_order_item.supply_price * quantity)`로 계산한다.
- 정산 완료 후 `book_logistics_deposit.current_balance`를 차감한다.
- 정산 이력은 `book_logistics_deposit_history`에 저장한다.

#### Response

```json
{
  "bookId": 1000,
  "deductAmount": 45080,
  "actualShippingCost": 3080,
  "balanceAfter": 9454920,
  "settledTime": "2026-05-12T13:00:00"
}
```

### 6.33 정산 이력 조회

```http
GET /api/v4/admin/book-settlements/histories
```

#### Query

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `transactionType` | String | N | `CHARGE`, `DEDUCT`, `REFUND`, `ADJUSTMENT` |
| `fromDate` | String | N | 조회 시작일 |
| `toDate` | String | N | 조회 종료일 |
| `page` | Integer | N | 페이지 번호 |
| `size` | Integer | N | 페이지 크기 |

#### Response

```json
{
  "items": [
    {
      "historyId": 1,
      "bookId": 1000,
      "transactionType": "DEDUCT",
      "amount": 45080,
      "balanceAfter": 9454920,
      "actualShippingCost": 3080,
      "description": "직8딴 교재 출고 정산",
      "settledTime": "2026-05-12T13:00:00"
    }
  ],
  "page": 0,
  "size": 20,
  "totalCount": 1
}
```

---

## 7. 주문 저장 예시

### 7.1 상품 마스터

| book_item.id | name | price | supply_price | stock_quantity |
| --- | --- | ---: | ---: | ---: |
| 1 | 직8딴 교재 | 30000 | 21000 | 100 |
| 2 | 면접 교재 | 25000 | 17500 | 50 |

### 7.2 단일 상품 주문

| order.id | user_id | status | name |
| --- | ---: | --- | --- |
| 500 | 10 | DONE | 직8딴 교재 |

| book.id | order_id | user_id | shipping_status | total_shipping_fee |
| --- | ---: | ---: | --- | ---: |
| 1000 | 500 | 10 | PAYMENT_COMPLETED | 3000 |

| book_order_item.id | book_id | book_item_id | product_name | product_price | supply_price | quantity |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 1000 | 1 | 직8딴 교재 | 30000 | 21000 | 2 |

### 7.3 복수 상품 주문

| order.id | user_id | status | name |
| --- | ---: | --- | --- |
| 501 | 10 | DONE | 직8딴 교재 외 1건 |

| book.id | order_id | user_id | shipping_status | total_shipping_fee |
| --- | ---: | ---: | --- | ---: |
| 1001 | 501 | 10 | PAYMENT_COMPLETED | 3000 |

| book_order_item.id | book_id | book_item_id | product_name | product_price | supply_price | quantity |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| 2 | 1001 | 1 | 직8딴 교재 | 30000 | 21000 | 1 |
| 3 | 1001 | 2 | 면접 교재 | 25000 | 17500 | 1 |

---

## 8. 확인 필요 사항

1. 가이드북 3개는 모든 도서 공통 고정 ID인지, 도서 상품별 매핑인지 확인이 필요하다.
2. 정산 차감 시점은 운송장 입력 시점, 배송 완료 시점, 관리자 수동 정산 중 하나로 확정이 필요하다.
3. 예치금 부족 시 정산을 막을지, 마이너스 잔액을 허용할지 확정이 필요하다.
4. 환불 완료 시 `Order.status`를 `CANCELED`로 변경할지, `DONE`을 유지하고 `Book.shipping_status = REFUNDED`만 사용할지 확정이 필요하다.
5. 대표 이미지 삭제 시 자동으로 다음 순서 이미지를 대표 이미지로 지정할지, 대표 이미지 없음 상태를 허용할지 확정이 필요하다.
