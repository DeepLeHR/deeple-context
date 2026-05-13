import os
import re
from typing import List, Optional
import requests

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def _rich_text_to_markdown(rich_texts: list) -> str:
    """Notion rich_text 배열을 마크다운 문자열로 변환"""
    parts = []
    for rt in rich_texts:
        text = rt.get("text", {}).get("content", "")
        annotations = rt.get("annotations", {})

        if annotations.get("bold"):
            text = f"**{text}**"
        if annotations.get("italic"):
            text = f"*{text}*"
        if annotations.get("strikethrough"):
            text = f"~~{text}~~"
        if annotations.get("code"):
            text = f"`{text}`"

        href = rt.get("href") or rt.get("text", {}).get("link", {}).get("url")
        if href:
            text = f"[{text}]({href})"

        parts.append(text)
    return "".join(parts)


def _blocks_to_markdown(blocks: list, indent_level: int = 0) -> str:
    """Notion blocks 리스트를 재귀적으로 마크다운으로 변환"""
    lines: List[str] = []
    indent = "  " * indent_level

    for block in blocks:
        btype = block.get("type", "")
        val = block.get(btype, {})

        if btype == "paragraph":
            text = _rich_text_to_markdown(val.get("rich_text", []))
            if text.strip():
                lines.append(f"{indent}{text}")
            else:
                lines.append("")

        elif btype == "heading_1":
            text = _rich_text_to_markdown(val.get("rich_text", []))
            lines.append(f"{indent}# {text}")

        elif btype == "heading_2":
            text = _rich_text_to_markdown(val.get("rich_text", []))
            lines.append(f"{indent}## {text}")

        elif btype == "heading_3":
            text = _rich_text_to_markdown(val.get("rich_text", []))
            lines.append(f"{indent}### {text}")

        elif btype == "bulleted_list_item":
            text = _rich_text_to_markdown(val.get("rich_text", []))
            lines.append(f"{indent}- {text}")

        elif btype == "numbered_list_item":
            text = _rich_text_to_markdown(val.get("rich_text", []))
            lines.append(f"{indent}1. {text}")

        elif btype == "to_do":
            text = _rich_text_to_markdown(val.get("rich_text", []))
            checked = "x" if val.get("checked") else " "
            lines.append(f"{indent}- [{checked}] {text}")

        elif btype == "quote":
            text = _rich_text_to_markdown(val.get("rich_text", []))
            lines.append(f"{indent}> {text}")

        elif btype == "code":
            text = _rich_text_to_markdown(val.get("rich_text", []))
            language = val.get("language", "")
            lines.append(f"{indent}```{language}\n{text}\n{indent}```")

        elif btype == "divider":
            lines.append(f"{indent}---")

        elif btype == "image":
            caption = _rich_text_to_markdown(val.get("caption", []))
            img_url = val.get("external", {}).get("url") or val.get("file", {}).get("url", "")
            if img_url:
                lines.append(f"{indent}![{caption}]({img_url})")

        elif btype == "bookmark":
            url = val.get("url", "")
            lines.append(f"{indent}[Bookmark]({url})")

        elif btype == "callout":
            text = _rich_text_to_markdown(val.get("rich_text", []))
            icon = val.get("icon", {}).get("emoji", "💡")
            lines.append(f"{indent}> {icon} {text}")

        # children (nested blocks) 처리
        children = block.get("children", [])
        if children:
            lines.append(_blocks_to_markdown(children, indent_level + 1))

    return "\n".join(lines)


def fetch_notion_page_markdown(page_id: str) -> str:
    """Notion page의 모든 block을 조회하여 마크다운으로 반환"""
    clean_id = page_id.replace("-", "")
    url = f"https://api.notion.com/v1/blocks/{clean_id}/children"
    all_blocks = []
    next_cursor = None

    while True:
        params = {"page_size": 100}
        if next_cursor:
            params["start_cursor"] = next_cursor

        resp = requests.get(url, headers=HEADERS, params=params)
        data = resp.json()

        if not data.get("ok", True) and data.get("status") >= 400:
            raise RuntimeError(f"Notion API error: {data}")

        results = data.get("results", [])
        all_blocks.extend(results)
        next_cursor = data.get("next_cursor")
        if not next_cursor:
            break

    return _blocks_to_markdown(all_blocks)


def extract_page_id_from_url(notion_url: str) -> Optional[str]:
    """Notion URL에서 page ID 추출"""
    # https://www.notion.so/Title-1234567890abcdef1234567890abcdef
    match = re.search(r"[a-f0-9]{32}", notion_url.replace("-", ""))
    if match:
        return match.group(0)
    # https://www.notion.so/deeplehr/Title-12345678-1234-1234-1234-123456789abc
    match = re.search(r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", notion_url)
    if match:
        return match.group(1)
    return None
