# MySQL MCP 설정 가이드

DB 조회(`db-query` 스킬)를 사용하려면 MySQL MCP 서버가 연결되어 있어야 합니다.
dev / prod 두 서버를 동시에 등록해두고, 프롬프트에서 원하는 서버를 지정해 사용합니다.

## 1단계 — env 파일 생성

계정 정보는 별도 문의. (host/port는 공통)

```bash
# dev
cat > ~/.mysql-dev.env << 'EOF'
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_USER=<dev_user>
MYSQL_PASS=<dev_password>
MYSQL_DB=GD_dev
EOF

# prod
cat > ~/.mysql-prod.env << 'EOF'
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_USER=<prod_user>
MYSQL_PASS=<prod_password>
MYSQL_DB=GD_production
EOF

chmod 600 ~/.mysql-dev.env ~/.mysql-prod.env
```

## 2단계 — 등록 스크립트 설치

```bash
mkdir -p ~/.local/bin

cat > ~/.local/bin/mysql-mcp-register << 'EOF'
#!/bin/bash
set -e

source ~/.mysql-dev.env
claude mcp remove mysql_dev -s user 2>/dev/null || true
claude mcp add mysql_dev \
  -s user \
  -e MYSQL_HOST="$MYSQL_HOST" \
  -e MYSQL_PORT="$MYSQL_PORT" \
  -e MYSQL_USER="$MYSQL_USER" \
  -e MYSQL_PASS="$MYSQL_PASS" \
  -e MYSQL_DB="$MYSQL_DB" \
  -- npx -y @benborla29/mcp-server-mysql

source ~/.mysql-prod.env
claude mcp remove mysql_prod -s user 2>/dev/null || true
claude mcp add mysql_prod \
  -s user \
  -e MYSQL_HOST="$MYSQL_HOST" \
  -e MYSQL_PORT="$MYSQL_PORT" \
  -e MYSQL_USER="$MYSQL_USER" \
  -e MYSQL_PASS="$MYSQL_PASS" \
  -e MYSQL_DB="$MYSQL_DB" \
  -- npx -y @benborla29/mcp-server-mysql

echo "✓ mysql_dev, mysql_prod 등록 완료"
EOF

chmod +x ~/.local/bin/mysql-mcp-register
```

`~/.local/bin`이 PATH에 없으면 `~/.zshrc`에 추가:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## 3단계 — 등록 실행

```bash
mysql-mcp-register
claude mcp list  # mysql_dev, mysql_prod 확인
```

## 사용법

```
# Claude 프롬프트에서 서버 이름 지정
"이 쿼리 mysql_dev에 실행해줘"
"mysql_prod에서 users 테이블 조회해줘"
```

## 자격증명 변경 시

```bash
# env 파일 수정 후 재등록
nano ~/.mysql-dev.env
mysql-mcp-register
```
