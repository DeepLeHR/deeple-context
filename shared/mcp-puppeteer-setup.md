# Puppeteer MCP 설정 가이드

브라우저 자동화, 스크린샷 생성, 간단한 E2E/시각 회귀 테스트에 사용합니다.

## 설치

별도 설정 없이 Claude에게 직접 요청합니다.

```text
Connect to the Puppeteer MCP server for me.
```

Claude가 서버를 찾고 필요한 경우 설치·연결 과정을 안내합니다.

## 사용 시나리오

UI 구현 또는 리팩터링 후 Puppeteer MCP를 통해:

- 특정 페이지 접속
- 주요 상호작용(클릭, 입력 등) 수행
- 스크린샷/HTML 스냅샷 캡처

캡처 결과로:

- Figma 디자인과의 시각적 차이 확인
- 레이아웃 깨짐 / 반응형 이슈 조기 발견

## 권장 워크플로우

Figma MCP로 디자인 스펙 확인 → 구현 → Puppeteer MCP로 브라우저 결과 검증
