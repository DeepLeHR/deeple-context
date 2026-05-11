# Dmand Design System

> Figma 원본: [Dmand Design System](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System)

Dmand 프로덕트의 디자인 언어를 정의하는 시스템입니다.
Foundation 토큰 위에 컴포넌트를 구성하며, PC·Tablet·Mobile 세 가지 브레이크포인트를 지원합니다.

---

## 목차

1. [Foundation](#1-foundation)
   - [Color](#color)
   - [Typography](#typography)
   - [Spacing & Grid](#spacing--grid)
   - [Border & Radius](#border--radius)
   - [Elevation & Shadow](#elevation--shadow)
   - [Motion & Easing](#motion--easing)
   - [Iconography](#iconography)
2. [Component](#2-component)
3. [네이밍 규칙](#3-네이밍-규칙)
4. [개발 적용 가이드](#4-개발-적용-가이드-development-guide)
   - [폰트 설정](#폰트-설정)
   - [색상 토큰 CSS 변수](#색상-토큰-css-변수)
   - [컴포넌트 Props 레퍼런스](#컴포넌트-props-레퍼런스)
   - [반응형 그리드](#반응형-그리드)
   - [아이콘 사용](#아이콘-사용)

---

## 1. Foundation

### Color

> Figma: [ㄴColor](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=5-2)

**2계층 구조**: Primitive Palette → Semantic Token

#### Primitive Palette

| Scale | 팔레트 | 용도 |
|-------|--------|------|
| Blue | 50 · 100 · 200 · 300 · **400(기본)** · 500 · 600 · 700 · 800 · 900 | 브랜드 메인 |
| Gray | 50 · 100 · 200 · 300 · 400 · **500** · 600 · 700 · 800 · 900 | 중립 |
| Red | 50 – 900 | 위험·오류 |
| Yellow | 50 – 900 | 경고 |
| Green | 50 – 900 | 성공 |
| Blue-line | 50 – 900 | 보조 파란 계열 |
| Purple | 50 – 900 | 보조 |
| Pink | 50 – 900 | 보조 |
| Common | Black `#000000` · White `#FFFFFF` | |

#### Semantic Tokens

컴포넌트는 Primitive 값을 직접 참조하지 않고 Semantic Token을 통해 색상을 적용합니다.

| 카테고리 | 토큰 예시 | 설명 |
|----------|-----------|------|
| **Background** | `color/bg/primary` `color/bg/secondary` `color/bg/inverse` | 배경 레이어 |
| **Text** | `color/text/primary` `color/text/secondary` `color/text/tertiary` `color/text/disabled` `color/text/inverse` `color/text/on-color` | 텍스트 |
| **Border** | `color/border/default` `color/border/strong` `color/border/focus` | 테두리 |
| **Action / Primary** | `color/action/primary/bg` `color/action/primary/bg-hover` `color/action/primary/bg-pressed` `color/action/primary/bg-disabled` | 주요 액션 |
| **Action / Secondary** | `color/action/secondary/bg` `color/action/secondary/bg-hover` `color/action/secondary/bg-disabled` | 보조 액션 |
| **Action / Danger** | `color/action/danger/bg` `color/action/danger/focus` `color/action/danger/disabled` | 위험 액션 |
| **Feedback / Error** | `color/feedback/error/…` | 오류 |
| **Feedback / Warning** | `color/feedback/warning/…` | 경고 |
| **Feedback / Success** | `color/feedback/success/…` | 성공 |
| **Feedback / Info** | `color/feedback/info/…` | 정보 |

---

### Typography

> Figma: [ㄴTypography](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=5-3)

**기본 폰트**: `Pretendard Variable` (가변 폰트) / 폴백: `Pretendard`

#### 타입 스케일

| 카테고리 | 스텝 | Font Size | Line Height | Weight | 용도 |
|----------|------|-----------|-------------|--------|------|
| **Display** | lg | 40px | 56px | Bold | 최상위 헤드라인 |
| | md | 32px | 44px | Bold | |
| | sm | 28px | 40px | Bold | |
| **Title** | lg | 24px | 36px | Bold | 페이지 타이틀 |
| | md | 20px | 32px | Bold | |
| | sm | 18px | 28px | Bold | |
| | xs | 16px | 24px | Bold | |
| **Heading** | lg | 18px | 28px | Semi Bold | 섹션 헤더 |
| | md | 16px | 24px | Semi Bold | |
| | sm | 14px | 20px | Semi Bold | |
| | xs | 12px | 18px | Semi Bold | |
| | 2xs | 11px | 16px | Semi Bold | |
| **Body** | lg | 16px | 28px | Regular | 본문 |
| | md | 14px | 24px | Regular | |
| | sm | 13px | 22px | Regular | |
| | xs | 12px | 20px | Regular | |
| **Label** | lg | 16px | 24px | Medium | 버튼·레이블 |
| | md | 14px | 20px | Medium | |
| | sm | 12px | 18px | Medium | |
| **Label2** | lg | 16px | 24px | Semi Bold | 강조 레이블 |
| | md | 14px | 20px | Semi Bold | |
| | sm | 12px | 18px | Semi Bold | |
| **Caption** | lg | 12px | 18px | Regular | 보조 텍스트 |
| | md | 11px | 16px | Regular | |

---

### Spacing & Grid

> Figma: [ㄴSpacing & Grid](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=5-4)

**기준 단위**: 4px — padding · gap · margin 모두 4px의 배수를 따릅니다.

#### Spacing Tokens

| Token | Value |
|-------|-------|
| `spacing/2px` | 2px |
| `spacing/4px` | 4px |
| `spacing/6px` | 6px |
| `spacing/8px` | 8px |
| `spacing/12px` | 12px |
| `spacing/16px` | 16px |
| `spacing/20px` | 20px |
| `spacing/24px` | 24px |
| `spacing/28px` | 28px |
| `spacing/32px` | 32px |
| `spacing/36px` | 36px |
| `spacing/40px` | 40px |
| `spacing/48px` | 48px |
| `spacing/56px` | 56px |
| `spacing/64px` | 64px |
| `spacing/80px` | 80px |
| `spacing/96px` | 96px |
| `spacing/128px` | 128px |

#### Grid System

| 브레이크포인트 | Width | Columns | Gutter | Margin |
|--------------|-------|---------|--------|--------|
| **Desktop** | 1440px | 12 | 24px | 80px |
| **Tablet** | 768px | 8 | 16px | 40px |
| **Mobile** | 375px | 4 | 16px | 16px |

Grid Variables 예시:
```
grid/desktop/columns → 12
grid/desktop/gutter-24px → 24px
grid/desktop/margin-80px → 80px
grid/desktop/width-1440px → 1440px
```

---

### Border & Radius

> Figma: [ㄴBorder & Radius](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=5-6)

#### Border Radius

| Token | Value | 사용 위치 |
|-------|-------|----------|
| `radius-none` | 0px | 테이블 셀, 구분선 |
| `radius-sm` | 4px | 인풋, 태그, 배지 |
| `radius-md` | 8px | 버튼, 카드 (기본) |
| `radius-lg` | 12px | 모달, 드롭다운 |
| `radius-xl` | 16px | 대형 카드, 시트 |
| `radius-2xl` | 24px | 바텀 시트, 패널 |
| `radius-full` | 9999px | 아바타, 토글, 칩 |

#### Border Width

| Token | Value | 사용 위치 |
|-------|-------|----------|
| `border-0` | 0px | 투명 버튼 등 테두리 제거 시 |
| `border-1` | 1px | 카드, 인풋, 구분선 (가장 많이 사용) |

---

### Elevation & Shadow

> Figma: [ㄴElevation & Shadow](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=5-5)

레이어 높이에 따른 그림자 토큰 시스템입니다.

---

### Motion & Easing

> Figma: [ㄴMotion & Easing](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=5-7)

인터랙션 애니메이션의 이징 곡선 및 지속 시간 토큰입니다.

---

### Iconography

> Figma: [ㄴIconography](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=5-8)

109개의 아이콘 셋. 컴포넌트 내부에서 `Icon/Icons` 컴포넌트를 통해 교체하여 사용합니다.
기존 색상을 유지한 채 아이콘을 교체할 수 있는 구조입니다.

---

## 2. Component

> Figma: [Component(Asset)](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=4-23)

모든 컴포넌트는 **Element** 카테고리 아래에 있으며, PC · Mobile 모두 지원합니다.

| 컴포넌트 | Figma 페이지 | Props 요약 |
|----------|-------------|-----------|
| **Decorate** | [┗ Decorate](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=99-1086) | 인터랙션 오버레이 등 보조 시각 요소 |
| **Button** | [┗ Button](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=0-1) | Type(Solid·Outline·Text) · Hierarchy(Primary·Secondary·Assistive·Normal) · Size(S·M·L) · Disabled |
| **Input fields** | [┗ Input fields](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1567) | Type(text input·password·long input) · Style(solide·underline) · Status(enabled·typing·filled·success·error·disabled) · Size(small·medium) |
| **Badge** | [┗ Badge](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1569) | 숫자·상태 표시 뱃지 |
| **Toggle** | [┗ Toggle](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1570) | On/Off 스위치 |
| **Searchbar** | [┗ Searchbar](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1571) | 검색 입력 필드 |
| **Checkbox** | [┗ Checkbox](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1572) | 다중 선택 체크박스 |
| **Avatar** | [┗ Avartar](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1573) | 사용자 이미지·이니셜 표시 |
| **Pagination** | [┗ Pagination](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1574) | 페이지 탐색 |
| **Loading** | [┗ Loading](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1575) | 로딩 인디케이터 |
| **Divider** | [┗ Divider](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1576) | 수평·수직 구분선 |
| **Chip** | [┗ Chip](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1577) | 필터·태그 선택 칩 |
| **Logo** | [┗ Logo](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1578) | 브랜드 로고 에셋 |
| **Tooltip** | [┗ Tooltip](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1579) | 호버 설명 말풍선 |
| **Toast** | [┗ Toast](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1580) | 일시적 알림 메시지 |
| **Tab** | [┗ Tab](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1581) | 탭 내비게이션 |
| **Menu** | [┗ Menu](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1582) | 드롭다운·컨텍스트 메뉴 |

---

## 3. 네이밍 규칙

### Variant Props

컴포넌트 Variant는 `Key=Value` 형식으로 정의합니다.

```
Type=Solid, Hierarchy=Primary, Size=Medium, Disabled=off
```

### 토큰 네이밍

```
{category}/{subcategory}/{role}/{state}

예시:
color/action/primary/bg
color/action/primary/bg-hover
spacing/16px
radius-md
```

### 파일 구조 (Figma 페이지 계층)


```
Dmand Design System
├── Overview
├── ──────────
├── Foundation
│   ├── ㄴColor
│   ├── ㄴTypography
│   ├── ㄴSpacing & Grid
│   ├── ㄴElevation & Shadow
│   ├── ㄴBorder & Radius
│   ├── ㄴMotion & Easing
│   └── ㄴIconography
├── ──────────
├── Component(Asset)
├── ──────────
├── Element
│   ├── ┗ Decorate
│   ├── ┗ Button
│   ├── ┗ Input fields
│   ├── ┗ Badge
│   ├── ┗ Toggle
│   ├── ┗ Searchbar
│   ├── ┗ Checkbox
│   ├── ┗ Avatar
│   ├── ┗ Pagination
│   ├── ┗ Loading
│   ├── ┗ Divider
│   ├── ┗ Chip
│   ├── ┗ Logo
│   ├── ┗ Tooltip
│   ├── ┗ Toast
│   ├── ┗ Tab
│   └── ┗ Menu
└── Thumbnail
```

---

## 4. 개발 적용 가이드 (Development Guide)

> Figma: [Component(Asset)](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=4-23)
> 아래 내용을 참고해 디자인 토큰을 코드에 정확히 매핑하세요.

---

### 폰트 설정

**기본 폰트**: `Pretendard Variable` (가변 폰트) · 폴백: `Pretendard` → `system-ui` → `sans-serif`

```css
/* globals.css */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/variable/pretendardvariable.css');

body {
  font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont,
    system-ui, sans-serif;
}
```

```css
/* 타입 스케일 유틸리티 클래스 예시 */
.display-lg  { font-size: 40px; line-height: 56px; font-weight: 700; }
.display-md  { font-size: 32px; line-height: 44px; font-weight: 700; }
.display-sm  { font-size: 28px; line-height: 40px; font-weight: 700; }

.title-lg    { font-size: 24px; line-height: 36px; font-weight: 700; }
.title-md    { font-size: 20px; line-height: 32px; font-weight: 700; }
.title-sm    { font-size: 18px; line-height: 28px; font-weight: 700; }
.title-xs    { font-size: 16px; line-height: 24px; font-weight: 700; }

.heading-lg  { font-size: 18px; line-height: 28px; font-weight: 600; }
.heading-md  { font-size: 16px; line-height: 24px; font-weight: 600; }
.heading-sm  { font-size: 14px; line-height: 20px; font-weight: 600; }
.heading-xs  { font-size: 12px; line-height: 18px; font-weight: 600; }
.heading-2xs { font-size: 11px; line-height: 16px; font-weight: 600; }

.body-lg     { font-size: 16px; line-height: 28px; font-weight: 400; }
.body-md     { font-size: 14px; line-height: 24px; font-weight: 400; }
.body-sm     { font-size: 13px; line-height: 22px; font-weight: 400; }
.body-xs     { font-size: 12px; line-height: 20px; font-weight: 400; }

.label-lg    { font-size: 16px; line-height: 24px; font-weight: 500; }
.label-md    { font-size: 14px; line-height: 20px; font-weight: 500; }
.label-sm    { font-size: 12px; line-height: 18px; font-weight: 500; }

.label2-lg   { font-size: 16px; line-height: 24px; font-weight: 600; }
.label2-md   { font-size: 14px; line-height: 20px; font-weight: 600; }
.label2-sm   { font-size: 12px; line-height: 18px; font-weight: 600; }

.caption-lg  { font-size: 12px; line-height: 18px; font-weight: 400; }
.caption-md  { font-size: 11px; line-height: 16px; font-weight: 400; }
```

---

### 색상 토큰 CSS 변수

Primitive 값을 직접 사용하지 않고 Semantic Token CSS 변수를 통해 참조합니다.

```css
:root {
  /* ── Brand Primitive ─────────────────────────── */
  --blue-400: #3A5DFE;   /* Primary brand */
  --gray-900: #101828;
  --gray-700: #344054;
  --gray-500: #667085;
  --gray-400: #98A2B3;
  --gray-200: #EAECF0;
  --gray-100: #F2F4F7;
  --gray-50:  #F9FAFB;

  /* ── Background ──────────────────────────────── */
  --color-bg-primary:   #FFFFFF;
  --color-bg-secondary: #F9FAFB;
  --color-bg-inverse:   #101828;

  /* ── Text ────────────────────────────────────── */
  --color-text-primary:   #101828;
  --color-text-secondary: #344054;
  --color-text-tertiary:  #667085;
  --color-text-disabled:  #98A2B3;
  --color-text-inverse:   #FFFFFF;
  --color-text-on-color:  #FFFFFF;
  --color-text-placeholder: #98A2B3;

  /* ── Border ──────────────────────────────────── */
  --color-border-default: #EAECF0;
  --color-border-strong:  #D0D5DD;
  --color-border-focus:   #3A5DFE;

  /* ── Action / Primary ────────────────────────── */
  --color-action-primary-bg:          #3A5DFE;
  --color-action-primary-bg-hover:    #2847E8;
  --color-action-primary-bg-pressed:  #1E38CC;
  --color-action-primary-bg-disabled: #B2BEF9;

  /* ── Action / Secondary ──────────────────────── */
  --color-action-secondary-bg:          #344054;
  --color-action-secondary-bg-hover:    #1D2939;
  --color-action-secondary-bg-disabled: #98A2B3;

  /* ── Action / Danger ─────────────────────────── */
  --color-action-danger-bg:       #D92D20;
  --color-action-danger-focus:    #F97066;
  --color-action-danger-disabled: #FDA29B;

  /* ── Feedback / Error ────────────────────────── */
  --color-feedback-error-border: #F97066;
  --color-feedback-error-text:   #D92D20;
  --color-feedback-error-bg:     #FEF3F2;

  /* ── Feedback / Success ──────────────────────── */
  --color-feedback-success-border: #32D583;
  --color-feedback-success-text:   #039855;
  --color-feedback-success-bg:     #ECFDF3;

  /* ── Feedback / Warning ──────────────────────── */
  --color-feedback-warning-border: #FDB022;
  --color-feedback-warning-text:   #B54708;
  --color-feedback-warning-bg:     #FFFAEB;

  /* ── Feedback / Info ─────────────────────────── */
  --color-feedback-info-border: #53B1FD;
  --color-feedback-info-text:   #1570EF;
  --color-feedback-info-bg:     #EFF8FF;

  /* ── Label ───────────────────────────────────── */
  --color-label-primary:    #3A5DFE;
  --color-label-background: #FFFFFF;
}
```

---

### 컴포넌트 Props 레퍼런스

#### Button

> Figma: [┗ Button](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=0-1)

| Prop | 값 | 기본값 | 설명 |
|------|----|--------|------|
| `type` | `solid` · `outline` · `text` | `solid` | 버튼 스타일 |
| `hierarchy` | `primary` · `secondary` · `assistive` · `normal` | `primary` | 버튼 위계 |
| `size` | `s` · `m` · `l` | `m` | Small(h=32) · Medium(h=40) · Large(h=48) |
| `disabled` | `on` · `off` | `off` | 비활성화 여부 |
| `leftIcon` | boolean | `false` | 왼쪽 아이콘 표시 |
| `rightIcon` | boolean | `false` | 오른쪽 아이콘 표시 |

**사이즈 스펙**

| Size | Height | Padding H | Font | Border Radius |
|------|--------|-----------|------|---------------|
| Small | 32px | 16px | 12px (label/sm) | 8px |
| Medium | 40px | 20px | 14px (label/md) | 10px |
| Large | 48px | 24px | 16px (label/lg) | 12px |

---

#### Input fields

> Figma: [┗ Input fields](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1567)

| Prop | 값 | 기본값 | 설명 |
|------|----|--------|------|
| `type` | `text input` · `password` · `long input` | `text input` | 입력 필드 유형 |
| `style` | `solide` · `underline` | `solide` | 테두리 스타일 |
| `status` | `enabled` · `typing` · `filled` · `success` · `error` · `disabled` | `enabled` | 입력 상태 |
| `size` | `small` · `medium` | `small` | 필드 크기 |
| `showLabel` | boolean | `true` | 레이블 표시 |
| `requiredIcon` | boolean | `true` | 필수 표시 (*) |
| `leftIcon` | boolean | `false` | 왼쪽 아이콘 |
| `rightIcon` | boolean | `false` | 오른쪽 아이콘 |
| `showUnit` | boolean | `false` | 단위 텍스트 표시 |
| `showHelperText` | boolean | `true` | 헬퍼 텍스트 표시 |
| `showCount` | boolean | `false` | 글자 수 카운터 |
| `bottomArea` | boolean | `true` | 하단 영역 (헬퍼 + 카운터) |

**상태별 색상 토큰**

| Status | Border | Helper Text |
|--------|--------|-------------|
| enabled | `color/border/default` `#EAECF0` | `color/text/tertiary` `#667085` |
| typing | `color/border/focus` `#3A5DFE` | `color/text/tertiary` `#667085` |
| filled | `color/border/default` `#EAECF0` | `color/text/tertiary` `#667085` |
| success | `color/feedback/success/border` `#32D583` | `color/feedback/success/text` `#039855` |
| error | `color/feedback/error/border` `#F97066` | `color/feedback/error/text` `#D92D20` |
| disabled | `color/border/default` `#EAECF0` | `color/text/placeholder` `#98A2B3` |

**사이즈 스펙**

| Type | Size | Input Height | Total Height | Padding H |
|------|------|-------------|-------------|-----------|
| text input · password | small | 40px | 82px | 12px |
| text input · password | medium | 48px | 90px | 12px |
| long input | small | 80px | 134px | 12px |
| long input | medium | 96px | 150px | 12px |

---

#### Badge

> Figma: [┗ Badge](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1569)

숫자·상태를 간결하게 표시하는 뱃지. 아이콘 위 오버레이 또는 단독 사용이 가능합니다.

---

#### Toggle

> Figma: [┗ Toggle](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1570)

On/Off 스위치. `border-radius: full(9999px)` 적용. 활성 색상: `color/action/primary/bg`.

---

#### Checkbox

> Figma: [┗ Checkbox](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1572)

다중 선택을 위한 체크박스. Checked 상태에서 `color/action/primary/bg` 적용.

---

#### Chip

> Figma: [┗ Chip](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1577)

필터·태그 선택. `border-radius: full(9999px)`. 선택 상태에서 Primary 색상 적용.

---

#### Avatar

> Figma: [┗ Avartar](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1573)

사용자 이미지 또는 이니셜 표시. `border-radius: full(9999px)`.

---

#### Tooltip

> Figma: [┗ Tooltip](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1579)

호버 시 보조 정보 제공. 배경: `color/bg/inverse`. 텍스트: `color/text/inverse`.

---

#### Toast

> Figma: [┗ Toast](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1580)

일시적 알림. Feedback 상태(success · error · warning · info)에 따른 색상 토큰 사용.

---

#### Tab

> Figma: [┗ Tab](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1581)

페이지 내 콘텐츠 전환. 활성 탭 하단 선 색상: `color/action/primary/bg`.

---

#### Menu

> Figma: [┗ Menu](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1582)

드롭다운·컨텍스트 메뉴. `border-radius: radius-lg(12px)`. `elevation` 토큰으로 그림자 적용.

---

#### Pagination

> Figma: [┗ Pagination](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1574)

페이지 탐색 컨트롤. 현재 페이지: `color/action/primary/bg` 배경.

---

#### Divider

> Figma: [┗ Divider](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1576)

수평·수직 구분선. 색상: `color/border/default`. `border-width: border-1(1px)`.

---

#### Loading

> Figma: [┗ Loading](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1575)

스피너 로딩 인디케이터. 색상: `color/action/primary/bg`.

---

#### Searchbar

> Figma: [┗ Searchbar](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=102-1571)

검색 전용 입력 필드. 내부에 검색 아이콘 포함.

---

### 반응형 그리드

```css
/* Breakpoints */
:root {
  --bp-desktop: 1440px;
  --bp-tablet:   768px;
  --bp-mobile:   375px;
}

/* Desktop — 12 columns, 24px gutter, 80px margin */
.container {
  max-width: 1440px;
  padding-inline: 80px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
}

/* Tablet — 8 columns, 16px gutter, 40px margin */
@media (max-width: 1024px) {
  .container { padding-inline: 40px; }
  .grid { grid-template-columns: repeat(8, 1fr); gap: 16px; }
}

/* Mobile — 4 columns, 16px gutter, 16px margin */
@media (max-width: 767px) {
  .container { padding-inline: 16px; }
  .grid { grid-template-columns: repeat(4, 1fr); gap: 16px; }
}
```

---

### 아이콘 사용

> Figma: [ㄴIconography](https://www.figma.com/design/gaGRZyQloPN8YaSBKFOJDn/Dmand-Design-System?node-id=5-8)

109개의 아이콘 셋. `Icon/Icons` 컴포넌트를 통해 교체하며 **기존 색상을 유지**합니다.

```tsx
// 아이콘 컴포넌트 사용 패턴 (색상은 부모에서 상속)
<Icon name="search" size={16} color="currentColor" />
<Icon name="chevron-down" size={20} color="var(--color-text-secondary)" />
<Icon name="check" size={16} color="var(--color-feedback-success-text)" />
```

**아이콘 사이즈 가이드**

| 사용 맥락 | 권장 사이즈 |
|-----------|------------|
| 인라인 (body 텍스트 내) | 16px |
| 버튼 아이콘 | 16–20px |
| 내비게이션 | 20–24px |
| 일러스트·강조 | 24–32px |

---

### Typography 클래스 매핑 (Tailwind)

| 토큰 | Tailwind 클래스 조합 | 용도 |
|------|----------------------|------|
| Display/lg | `text-[40px] leading-[56px] font-bold` | 최상위 헤드라인 |
| Title/lg | `text-[24px] leading-[36px] font-bold` | 페이지 타이틀 |
| Title/md | `text-[20px] leading-[32px] font-bold` | 섹션 타이틀 |
| Title/sm | `text-[18px] leading-[28px] font-bold` | 카드/모달 타이틀 |
| Heading/lg | `text-[18px] leading-[28px] font-semibold` | 섹션 헤더 |
| Heading/md | `text-[16px] leading-[24px] font-semibold` | 소제목 |
| Body/md | `text-[14px] leading-[24px] font-normal` | 본문 기본 |
| Body/sm | `text-[13px] leading-[22px] font-normal` | 본문 작게 |
| Label/md | `text-[14px] leading-[20px] font-medium` | 버튼 M |
| Label/sm | `text-[12px] leading-[18px] font-medium` | 버튼 S / 칩 |
| Caption/lg | `text-[12px] leading-[18px] font-normal` | 보조 텍스트 |
| Caption/md | `text-[11px] leading-[16px] font-normal` | 메타 정보 |

⚠️ Body 계열은 `font-normal`(400), Label은 `font-medium`(500). Body에 Medium이나 Bold를 임의로 쓰지 마세요.

---

### Tailwind 토큰 연결

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'action-primary':    'var(--color-action-primary-bg)',
        'text-primary':      'var(--color-text-primary)',
        'text-secondary':    'var(--color-text-secondary)',
        'text-tertiary':     'var(--color-text-tertiary)',
        'border-default':    'var(--color-border-default)',
        'border-focus':      'var(--color-border-focus)',
        'feedback-error':    'var(--color-feedback-error-text)',
        'feedback-success':  'var(--color-feedback-success-text)',
      },
      screens: {
        'md': '768px',    // Tablet
        'lg': '1440px',   // Desktop
      },
    },
  },
}
```

**컨테이너 마진**

| 브레이크포인트 | Tailwind | 사용 예시 |
|---|---|---|
| Desktop (1440px) | `lg:px-[80px] lg:grid-cols-12 gap-[24px]` | 카드 3열: `col-span-4` |
| Tablet (768px) | `md:px-[40px] md:grid-cols-8 gap-[16px]` | 카드 2열: `md:col-span-4` |
| Mobile (375px) | `px-[16px] grid-cols-4 gap-[16px]` | 카드 1열: `col-span-4` |

```html
<!-- 카드 그리드 예시 -->
<div class="grid grid-cols-4 gap-[16px] md:grid-cols-8 lg:grid-cols-12 lg:gap-[24px]">
  <div class="col-span-4 md:col-span-4 lg:col-span-4">...</div>
</div>
```

---

### Radius 체크리스트

| 토큰 | 값 | 사용 위치 | Tailwind |
|------|-----|----------|----------|
| radius-sm | 4px | 인풋, 태그, 배지 | `rounded-sm` |
| radius-md | 8px | 버튼, 카드 (기본) | `rounded-md` |
| radius-lg | 12px | 모달, 드롭다운 | `rounded-lg` |
| radius-xl | 16px | 대형 카드, 시트 | `rounded-xl` |
| radius-2xl | 24px | 바텀 시트, 패널 | `rounded-2xl` |
| radius-full | 9999px | 아바타, 토글, 칩 | `rounded-full` |

⚠️ **자주 틀리는 조합**
- 카드 → `rounded-md`(8px). `rounded-lg`(12px)는 모달용
- 인풋 → `rounded-sm`(4px). `rounded-md`(8px)는 버튼/카드용
- 아바타 → 반드시 `rounded-full`

---

### Button Variant 체크리스트

Button은 `Type × Hierarchy × Size` 3가지 속성으로 조합합니다.

| Type | Hierarchy | Size | 스펙 |
|------|-----------|------|------|
| Solid | Primary | L | `h-[48px] px-[24px] rounded-md bg-[#3A5DFE] text-white text-[16px] font-medium` |
| Solid | Primary | M | `h-[40px] px-[20px] rounded-[10px] bg-[#3A5DFE] text-white text-[14px] font-medium` |
| Solid | Primary | S | `h-[32px] px-[16px] rounded-md bg-[#3A5DFE] text-white text-[12px] font-medium` |
| Outline | Normal | M | `h-[40px] px-[20px] rounded-[10px] border border-[#EAECF0] bg-white text-[14px] font-medium` |
| Text | Normal | M | `h-[40px] px-[12px] text-[14px] font-medium` |

---

### 컴포넌트별 개발 체크리스트

**Card**
- [ ] Radius: `rounded-md` (8px)
- [ ] Border: `border border-[#EAECF0]`
- [ ] Background: `bg-white`
- [ ] Padding: `p-[20px]` 또는 `p-[24px]`

**Input fields**
- [ ] Radius: `rounded-md` (8px) — solid style
- [ ] Border enabled: `border border-[#EAECF0]`
- [ ] Border focus: `border-[#3A5DFE]`
- [ ] Border error: `border-[#F97066]`
- [ ] Border success: `border-[#32D583]`
- [ ] Helper text error: `text-[#D92D20]`
- [ ] Helper text success: `text-[#039855]`
- [ ] Disabled: `bg-[#F2F4F7] text-[#98A2B3] cursor-not-allowed`

**Avatar**
- [ ] Radius: 반드시 `rounded-full`
- [ ] Fallback: 이니셜 텍스트 중앙 정렬

**Tab**
- [ ] 활성 탭: `font-semibold` + 하단 인디케이터 `bg-[#3A5DFE]`
- [ ] 비활성 탭: `font-medium text-[#667085]`

**Toast**
- [ ] Radius: `rounded-lg` (12px)
- [ ] 위치: 하단 중앙 고정
- [ ] 자동 사라짐 (2~3초)

**Modal**
- [ ] Radius: `rounded-lg` (12px)
- [ ] Backdrop: `bg-black/40`
- [ ] Padding: `p-[24px]` (Mobile) / `p-[32px]` (Desktop)
- [ ] 최대 너비: `max-w-[480px]`
