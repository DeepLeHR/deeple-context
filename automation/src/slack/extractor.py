import os
import re
from typing import Optional
import requests

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")


def extract_thread_messages(channel_id: str, thread_ts: str) -> str:
    """
    Slack API로 스레드의 모든 메시지를 수집하여 마크다운으로 반환
    """
    url = "https://slack.com/api/conversations.replies"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    params = {
        "channel": channel_id,
        "ts": thread_ts,
        "limit": 200,
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if not data.get("ok"):
        error = data.get("error", "unknown")
        raise RuntimeError(f"Slack API error: {error}")

    messages = data.get("messages", [])
    if not messages:
        return ""

    # 첫 메시지는 주제, 나머지는 댓글
    lines = []
    for i, msg in enumerate(messages):
        user = msg.get("user", "unknown")
        text = msg.get("text", "")
        # 멘션(<@USER_ID>) 제거 또는 치환
        text = re.sub(r"<@\w+>", "", text).strip()
        # URL unfurl 제거 (<URL|TEXT> → TEXT)
        text = re.sub(r"<(https?://[^|]+)\|([^>]+)>", r"[\2](\1)", text)
        text = re.sub(r"<(https?://[^>]+)>", r"\1", text)

        if not text:
            continue

        if i == 0:
            lines.append(f"**주제:** {text}\n")
        else:
            lines.append(f"- {text}")

    return "\n".join(lines)


def get_channel_info(channel_id: str) -> dict:
    """채널 정보 조회 (public/private 여부 등)"""
    url = "https://slack.com/api/conversations.info"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    params = {"channel": channel_id}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if not data.get("ok"):
        print(f"Failed to get channel info: {data.get('error')}")
        return {"_error": True}
    return data.get("channel", {})


def get_permalink(channel_id: str, message_ts: str) -> Optional[str]:
    """슬랙 메시지 permalink 가져오기"""
    url = "https://slack.com/api/chat.getPermalink"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    params = {"channel": channel_id, "message_ts": message_ts}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data.get("ok"):
        return data.get("permalink")
    return None
