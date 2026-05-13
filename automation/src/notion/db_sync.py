import os
import json
from datetime import datetime, timezone, timedelta
from notion.client import find_pages, update_property
from notion.converter import fetch_notion_page_markdown
from context_git import get_file_info, write_content
from context_analyzer import analyze_placement
from context_save_handler import build_source_header

NOTION_PLANNING_DB_ID = os.environ.get("NOTION_PLANNING_DB_ID", "")
KST = timezone(timedelta(hours=9))


def run_daily_sync() -> dict:
    """매일 자정 실행: Notion DB에서 sync_to_context == true 인 페이지 동기화"""
    if not NOTION_PLANNING_DB_ID:
        print("NOTION_PLANNING_DB_ID not set")
        return {"statusCode": 500, "body": "NOTION_PLANNING_DB_ID not set"}

    try:
        pages = _find_unsynced_pages()
        results = []

        for page in pages:
            result = _sync_page(page)
            results.append(result)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"synced_count": len(results), "results": results},
                ensure_ascii=False,
            ),
        }
    except Exception as e:
        print(f"Cron sync failed: {e}")
        return {"statusCode": 500, "body": str(e)}


def _find_unsynced_pages() -> list:
    """sync_to_context == true 인 페이지 조회"""
    url = f"https://api.notion.com/v1/databases/{NOTION_PLANNING_DB_ID}/query"
    import requests

    headers = {
        "Authorization": f"Bearer {os.environ.get('NOTION_TOKEN')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    body = {
        "filter": {
            "property": "sync_to_context",
            "checkbox": {"equals": True},
        }
    }

    resp = requests.post(url, headers=headers, json=body)
    data = resp.json()
    return data.get("results", [])


def _sync_page(page: dict) -> dict:
    """단일 노션 페이지를 context에 동기화"""
    page_id = page["id"]
    props = page.get("properties", {})

    # 제목 추출
    title = ""
    title_obj = props.get("제목", props.get("Name", props.get("name", {})))
    if "title" in title_obj:
        title = "".join(t.get("text", {}).get("content", "") for t in title_obj["title"])

    # target_path
    target_path_prop = props.get("target_path", {}).get("rich_text", [])
    target_path = target_path_prop[0].get("text", {}).get("content", "") if target_path_prop else ""

    # synced_at
    synced_at = props.get("synced_at", {}).get("date", {}).get("start", "")

    # 1. 페이지 콘텐츠 수집
    content = fetch_notion_page_markdown(page_id)
    notion_url = page.get("url", f"https://notion.so/{page_id.replace('-', '')}")

    # 2. 출처 헤더 추가
    source_header = build_source_header(
        source="notion",
        notion_page_id=page_id,
        edit_priority="notion",
    )
    full_content = source_header + content

    # 3. 경로 결정
    if target_path:
        file_path = target_path
        action = "update"
        reason = f"사용자 지정 경로: {target_path}"
    else:
        placement = analyze_placement(content)
        file_path = placement["new_path"]
        action = placement["action"]
        reason = placement.get("reason", "AI 분석")
        title = placement.get("title", title)

    # 4. GitHub에 저장
    result = write_content(file_path, full_content, title, action)

    # 5. notion-mapping.yaml 업데이트
    _update_notion_mapping(page_id, file_path, title)

    # 6. synced_at 업데이트
    now_iso = datetime.now(KST).strftime("%Y-%m-%d")
    update_property(
        page_id,
        {"synced_at": {"date": {"start": now_iso}}},
    )

    return {
        "page_id": page_id,
        "title": title,
        "file_path": file_path,
        "commit_hash": result.get("commit_hash"),
        "reason": reason,
    }


def _update_notion_mapping(page_id: str, file_path: str, title: str):
    """_sync/notion-mapping.yaml 업데이트"""
    try:
        exists, _, content = get_file_info("_sync/notion-mapping.yaml")
        new_entry = f"- page_id: {page_id}\n  path: {file_path}\n  title: {title}\n  updated_at: {datetime.now(KST).isoformat()}\n"

        if exists:
            # 기존 entry가 있으면 교체, 없으면 append
            lines = content.splitlines()
            new_lines = []
            skip = 0
            for line in lines:
                if skip > 0:
                    skip -= 1
                    continue
                if f"page_id: {page_id}" in line:
                    skip = 3  # page_id, path, title, updated_at 4줄
                    continue
                new_lines.append(line)
            new_content = "\n".join(new_lines) + "\n" + new_entry
        else:
            new_content = new_entry

        write_content(
            "_sync/notion-mapping.yaml",
            new_content,
            title=None,
            action="update" if exists else "create",
        )
    except Exception as e:
        print(f"Failed to update notion mapping: {e}")
