# 멤버십 프로모션 API 스펙

## 응답 원칙

멤버십 API는 기본 멤버십 상품 목록과 현재 유저에게 적용 가능한 프로모션을 함께 내려준다.

백엔드는 프로모션의 활성 여부, 기간, 대상 조건, 가격, 우선순위를 평가한 뒤 최종적으로 노출 가능한 `activePromotion`만 응답한다. 프론트는 프로모션 대상 여부를 다시 계산하지 않고, 응답에 포함된 `activePromotion` 존재 여부에 따라 화면을 선택한다.

## 응답 예시

```json
{
  "membership": {
    "defaultPlans": [
      {
        "id": 1,
        "name": "BASIC",
        "price": 9900
      },
      {
        "id": 2,
        "name": "PRO",
        "price": 14900
      }
    ],
    "activePromotion": {
      "id": "first_month_2026_spring",
      "type": "FIRST_PURCHASE_DISCOUNT",
      "startsAt": "2026-05-01T00:00:00+09:00",
      "endsAt": "2026-06-30T23:59:59+09:00",
      "plans": [
        {
          "id": 1,
          "name": "BASIC",
          "price": 5900,
          "originalPrice": 9900
        },
        {
          "id": 2,
          "name": "PRO",
          "price": 7900,
          "originalPrice": 14900
        }
      ],
      "content": {
        "title": "첫 달 멤버십 특가",
        "subtitle": "지금만 이 가격으로 시작하세요",
        "badgeText": "기간 한정",
        "ctaText": "특가로 시작하기",
        "noticeText": "프로모션 가격은 대상 유저에게만 적용됩니다.",
        "imageUrl": "https://example.com/membership/first-purchase-2026-spring.png"
      },
      "priority": 100
    }
  }
}
```

프로모션이 없으면 `activePromotion`은 `null`로 내려준다.

```json
{
  "membership": {
    "defaultPlans": [],
    "activePromotion": null
  }
}
```

## 필드 정의

### MembershipPromotion

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `id` | string | 프로모션 식별자 |
| `type` | string | 프론트 렌더링 템플릿 선택에 사용하는 프로모션 타입 |
| `startsAt` | string | 프로모션 시작 시각 |
| `endsAt` | string | 프로모션 종료 시각 |
| `plans` | array | 프로모션에 적용되는 멤버십 plan 목록 |
| `content` | object | 화면에 주입할 짧은 문구 및 이미지 |
| `priority` | number | 여러 프로모션이 동시에 적용 가능할 때의 노출 우선순위 |

### PromotionContent

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `title` | string | 프로모션 제목 |
| `subtitle` | string | 프로모션 부제목 |
| `badgeText` | string | 배지 문구 |
| `ctaText` | string | CTA 버튼 문구 |
| `noticeText` | string | 약관, 유의사항 등 보조 문구 |
| `imageUrl` | string | 프로모션 이미지 URL |

### PromotionPlan

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `id` | number | 정가 plan 식별자 |
| `name` | string | plan 이름 |
| `price` | number | 프로모션 적용 시 첫 결제 가격 |
| `originalPrice` | number | 정가 또는 비교 기준 가격 |

통화는 원화 기준이므로 응답 필드로 내려주지 않는다.

`productId`는 App Store 또는 외부 결제 시스템의 상품 식별자다. 현재 멤버십 화면과 주문 API의 기본 계약에는 포함하지 않는다. iOS 결제 검증처럼 결제 시스템 상품 식별자가 필요한 내부 흐름에서는 서버가 plan과 결제 시스템 상품 식별자를 매핑해 검증한다.

## 프로모션 타입

| 타입 | 설명 | 프론트 fallback |
| --- | --- | --- |
| `FIRST_PURCHASE_DISCOUNT` | 멤버십 구매 이력이 없는 유저 대상 첫 구매 특가 | 기본 멤버십 화면 |
| `WINBACK` | 과거 구매 이력이 있으나 현재 멤버십이 없는 유저 대상 재구매 프로모션 | 기본 멤버십 화면 |

프론트 앱이 알 수 없는 `type`을 받으면 프로모션 화면을 렌더링하지 않고 기본 멤버십 화면으로 fallback한다.

## 프론트 렌더링 계약

프론트는 `activePromotion.type`에 따라 앱에 구현된 템플릿을 선택하고, 백엔드가 내려준 `content`, `plans`, `startsAt`, `endsAt` 값을 주입한다.

```dart
switch (promotion.type) {
  case MembershipPromotionType.firstPurchaseDiscount:
    return FirstPurchasePromotionMembershipView(promotion: promotion);
  case MembershipPromotionType.winback:
    return WinbackPromotionMembershipView(promotion: promotion);
  default:
    return DefaultMembershipView();
}
```

프론트는 가격, 대상 조건, 혜택 적용 여부를 독자적으로 재판정하지 않는다. 결제 요청 시에도 백엔드가 유저와 상품의 프로모션 적용 가능 여부를 다시 검증해야 한다.

## 프론트 사용 계약

프론트는 `defaultPlans`와 `activePromotion`을 직접 병합하거나 대상 여부를 계산하지 않는다. 백엔드 응답에 `activePromotion`이 있으면 프로모션 화면을 렌더링하고, 없으면 기본 멤버십 화면을 렌더링한다.

### 화면 표시

`activePromotion`이 없는 경우:

- `defaultPlans`를 그대로 표시한다.
- `defaultPlans[].price`를 결제 금액으로 표시한다.

`activePromotion`이 있는 경우:

- `activePromotion.type`에 맞는 프로모션 템플릿을 사용한다.
- `activePromotion.plans`를 표시한다.
- `activePromotion.plans[].originalPrice`는 정가로 표시한다.
- `activePromotion.plans[].price`는 첫 결제 할인가로 표시한다.
- `activePromotion.content`의 문구를 화면에 주입한다.

예를 들어 베이직 첫 달 할인 대상 유저에게는 다음처럼 표시한다.

- 멤버십: `BASIC`
- 정가: `9900`
- 첫 결제 가격: `5900`

### 주문 요청

프론트는 주문 생성 시 정가 plan ID를 보낸다. 프로모션용 별도 plan ID나 `promotionKey`를 보내지 않는다.

예를 들어 `activePromotion.plans`에서 베이직을 선택한 경우:

```json
{
  "planId": 1,
  "totalAmount": 5900
}
```

여기서 `planId`는 베이직 정가 plan ID다. `totalAmount`는 화면에 표시된 첫 결제 금액이다.

백엔드는 주문 생성 시 다음을 다시 검증한다.

- 요청된 plan ID가 구매 가능한 정가 plan인지
- 현재 유저에게 적용 가능한 프로모션이 있는지
- 유료 멤버십 결제 이력이 없는지
- 요청 금액이 서버가 계산한 기대 결제 금액과 같은지

할인 대상 유저가 아니거나 이벤트 기간이 종료된 경우, 같은 `planId`라도 기대 결제 금액은 정가가 된다. 이때 프론트가 할인 금액으로 주문을 요청하면 백엔드는 주문 생성을 거부한다.

## 첫 달 할인 주문 계약

첫 달 할인 프로모션은 별도 할인 plan을 구매하는 방식이 아니다. 프론트는 `activePromotion.plans[].id`에 포함된 정가 plan ID로 주문을 요청하고, 백엔드는 현재 유저에게 적용 가능한 프로모션을 다시 검증한 뒤 첫 결제 금액을 확정한다.

예를 들어 베이직 첫 달 할인 대상 유저가 주문을 생성하면 서버 저장 결과는 다음과 같다.

- `order.plan_id`: 베이직 정가 plan ID
- `order_payment.total_amount`: 5900
- `subscription.plan_id`: 베이직 정가 plan ID
- `subscription_order_promotion.promotion_key`: `first_month_2026_spring`
- `subscription_order_promotion.original_price`: 9900
- `subscription_order_promotion.discount_price`: 5900

첫 달 할인 대상이 아닌 유저가 할인 금액으로 주문을 시도하거나, 대상 유저가 아닌데 프로모션 가격을 요청하면 백엔드는 주문 생성을 거부한다.
