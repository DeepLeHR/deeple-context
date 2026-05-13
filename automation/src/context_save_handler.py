from datetime import datetime, timezone, timedelta
import os
from context_analyzer import analyze_placement
from context_git import (
    create_branch,
    write_content,
    create_pull_request,
    sanitize_branch_name,
)
from context_extractor import extract_thread_messages, get_permalink
from slack_sender import send_message
from notion_converter import fetch_notion_page_markdown, extract_page_id_from_url

KST = timezone(timedelta(hours=9))
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

# 허용되는 최상위 디렉토리
ALLOWED_TOP_DIRS = {"shared", "dmand", "gocho", "new", "_sync"}


def _validate_path(file_path: str) -> str:
    """경로 검증: 안전하지 않은 경로 차단"""
    # 상위 디렉토리 참조 차단
    if ".." in file_path:
        raise ValueError(f"Invalid path (contains '..'): {file_path}")
    # 절대 경로 차단
    if file_path.startswith("/"):
        raise ValueError(f"Invalid path (absolute): {file_path}")
    # 확장자 검증
    if not file_path.endswith(".md"):
        raise ValueError(f"Invalid path (must be .md): {file_path}")
    # 최상위 디렉토리 화이트리스트
    top_dir = file_path.split("/")[0]
    if top_dir not in ALLOWED_TOP_DIRS:
        raise ValueError(
            f"Invalid path (top dir '{top_dir}' not in {ALLOWED_TOP_DIRS}): {file_path}"
        )
    return file_path


def build_source_header(
    source: str,
    notion_page_id: str = None,
    slack_channel_id: str = None,
    slack_message_ts: str = None,
    edit_priority: str = "notion",
) -> str:
    """문서 최상단 YAML frontmatter 헤더 생성"""
    lines = ["---"]
    lines.append(f"source: {source}")
    if notion_page_id:
        lines.append(f"notion_page_id: {notion_page_id}")
    if slack_channel_id:
        lines.append(f"slack_channel_id: {slack_channel_id}")
    if slack_message_ts:
        lines.append(f"slack_message_ts: {slack_message_ts}")
    lines.append(f"last_synced: {datetime.now(KST).isoformat()}")
    lines.append(f"edit_priority: {edit_priority}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def _build_pr_success_message(pr: dict, file_path: str, reason: str) -> dict:
    """PR 생성 성공 시 Slack 메시지 구성"""
    pr_url = pr.get("pr_url", "")
    pr_title = pr.get("pr_title", "")
    return {
        "text": f"✅ *Context PR 생성 완료*\n\n"
                f"• 제목: *{pr_title}*\n"
                f"• 경로: `{file_path}`\n"
                f"• PR: {pr_url}\n"
                f"• 이유: {reason}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*✅ Context PR 생성 완료*\n\n"
                            f"• *제목:* {pr_title}\n"
                            f"• *경로:* `{file_path}`\n"
                            f"• *PR:* <{pr_url}|보기>\n"
                            f"• *선택 이유:* {reason}"
                }
            }
        ]
    }


def _build_error_message(error: str) -> dict:
    return {
        "text": f"❌ Context 처리 실패\n```\n{error}\n```",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*❌ Context 처리 실패*\n```\n{error}\n```"
                }
            }
        ]
    }


def save_slack_thread(channel_id: str, thread_ts: str, response_url: str = None):
    """슬랙 스레드를 context에 PR로 저장"""
    try:
        # 1. 스레드 메시지 수집
        content = extract_thread_messages(channel_id, thread_ts)
        if not content.strip():
            if response_url:
                send_message(response_url, _build_error_message("스레드 내용이 비어있습니다."))
            return {"statusCode": 400, "error": "Empty thread"}

        # 2. permalink + 헤더 생성
        permalink = get_permalink(channel_id, thread_ts)
        source_header = build_source_header(
            source="slack",
            slack_channel_id=channel_id,
            slack_message_ts=thread_ts,
            edit_priority="slack",
        )
        if permalink:
            content += f"\n\n---\n\n*출처:* {permalink}"
        full_content = source_header + content

        # 3. AI로 최적 위치 분석
        placement = analyze_placement(content)

        # 4. 브랜치 생성
        branch_name = f"context/slack-{sanitize_branch_name(channel_id)}-{sanitize_branch_name(thread_ts)}"
        create_branch(branch_name)

        # 5. 파일 쓰기 (브랜치 기준)
        file_path = placement["new_path"]
        action = placement["action"]
        title = placement["title"]

        write_content(file_path, full_content, title, action, branch=branch_name)

        # 6. PR 생성
        pr = create_pull_request(
            title=f"docs({placement['service']}): {title}",
            body=f"### 자동 동기화: Slack Thread\n\n"
                 f"- **출처:** {permalink or f'{channel_id}/{thread_ts}'}\n"
                 f"- **AI 선택 이유:** {placement.get('reason', '')}\n"
                 f"- **대상 경로:** `{file_path}`\n\n"
                 f"---\n"
                 f"⚠️ **검토 후 머지해주세요.**",
            head=branch_name,
        )

        # 7. 완료 알림 (response_url 있을 때만)
        if response_url:
            send_message(
                response_url,
                _build_pr_success_message(pr, file_path, placement.get("reason", "")),
            )
        return {"statusCode": 200, "pr_url": pr["pr_url"]}

    except Exception as e:
        if response_url:
            send_message(response_url, _build_error_message(str(e)))
        return {"statusCode": 500, "error": str(e)}


def save_notion_page(notion_url: str, response_url: str):
    """노션 페이지를 context에 PR로 저장 (수동 /context-save 용)"""
    try:
        page_id = extract_page_id_from_url(notion_url)
        if not page_id:
            send_message(response_url, _build_error_message("올바른 Notion URL이 아닙니다."))
            return {"statusCode": 400}

        content = fetch_notion_page_markdown(page_id)
        if not content.strip():
            send_message(response_url, _build_error_message("노션 페이지 내용이 비어있습니다."))
            return {"statusCode": 400}

        source_header = build_source_header(
            source="notion",
            notion_page_id=page_id,
            edit_priority="notion",
        )
        full_content = source_header + content

        placement = analyze_placement(content)
        file_path = placement["new_path"]
        action = placement["action"]
        title = placement["title"]

        branch_name = f"context/notion-{sanitize_branch_name(page_id)}"
        create_branch(branch_name)

        write_content(file_path, full_content, title, action, branch=branch_name)

        pr = create_pull_request(
            title=f"docs({placement['service']}): {title}",
            body=f"### 자동 동기화: Notion Page\n\n"
                 f"- **출처:** {notion_url}\n"
                 f"- **AI 선택 이유:** {placement.get('reason', '')}\n"
                 f"- **대상 경로:** `{file_path}`\n\n"
                 f"---\n"
                 f"⚠️ **검토 후 머지해주세요.**",
            head=branch_name,
        )

        send_message(
            response_url,
            _build_pr_success_message(pr, file_path, placement.get("reason", "")),
        )
        return {"statusCode": 200, "pr_url": pr["pr_url"]}

    except Exception as e:
        send_message(response_url, _build_error_message(str(e)))
        return {"statusCode": 500}
