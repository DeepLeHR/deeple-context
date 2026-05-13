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
        "id": "membership_monthly",
        "name": "월간 멤버십",
        "price": 29000,
        "currency": "KRW",
        "productId": "membership_monthly"
      }
    ],
    "activePromotion": {
      "id": "first_purchase_2026_spring",
      "type": "FIRST_PURCHASE_DISCOUNT",
      "startsAt": "2026-05-01T00:00:00+09:00",
      "endsAt": "2026-06-30T23:59:59+09:00",
      "plans": [
        {
          "id": "membership_first_purchase_monthly",
          "name": "첫 멤버십 특가",
          "price": 9900,
          "originalPrice": 29000,
          "currency": "KRW",
          "productId": "membership_first_purchase_monthly"
        }
      ],
      "content": {
        "title": "첫 멤버십 특가",
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
| `id` | string | plan 식별자 |
| `name` | string | plan 이름 |
| `price` | number | 실제 결제 가격 |
| `originalPrice` | number | 정가 또는 비교 기준 가격 |
| `currency` | string | 통화 코드 |
| `productId` | string | 결제 시스템 상품 id |

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

