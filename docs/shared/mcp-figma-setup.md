# Figma MCP 설정 가이드

Figma 디자인 파일로부터 컴포넌트 구조, 스타일, 토큰 등을 불러와 코드에 반영할 때 사용합니다.

## 설치

Figma 앱 안에서 MCP 클라이언트를 추가하면 안내에 따라 진행합니다.

1. Figma 상단 MCP 설정에서 `Claude Code (figma)` 클라이언트 선택
2. 팝업에 나오는 명령을 터미널에 복사·실행

```bash
claude plugin install figma@claude-plugins-official
# 또는
claude mcp add --transport http figma https://mcp.figma.com/mcp
```

3. 설치 확인

```bash
claude mcp list  # figma 서버 확인
```

## 사용 패턴

1. Figma에서 구현 대상 화면의 URL(파일 + 노드) 준비
2. Claude에서 Figma MCP 툴로 디자인 컨텍스트 조회
3. 생성된 코드/스타일은 반드시 `frontend-web/CLAUDE.md` 규칙에 맞게 수정 후 사용
   - Emotion `css` prop
   - `shared-ui/deeple-ds` 컴포넌트
   - `COLOR` 토큰
   - `components/[ComponentName]/index.tsx` 구조
