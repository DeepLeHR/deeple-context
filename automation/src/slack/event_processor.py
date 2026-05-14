import os
import json
import boto3
from slack.sender import send_message
from context_save_handler import save_slack_thread
from slack.extractor import get_channel_info
from context_git import is_message_pinned, mark_message_pinned

SLACK_CONTEXT_CHANNELS = os.environ.get("SLACK_CONTEXT_CHANNELS", "")
TARGET_CHANNELS = {c.strip() for c in SLACK_CONTEXT_CHANNELS.split(",") if c.strip()}
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL", "")


def handle_slack_event(body: dict) -> dict:
    """Slack Event API payload 처리"""
    event = body.get("event", {})
    event_type = event.get("type", "")

    if event_type == "reaction_added":
        return _handle_reaction_added(event)

    # 다른 이벤트는 무시
    return {"statusCode": 200, "body": "Ignored"}


def _handle_reaction_added(event: dict) -> dict:
    reaction = event.get("reaction", "")
    item = event.get("item", {})
    channel_id = item.get("channel", "")
    message_ts = item.get("ts", "")

    # 📌 pushpin 이모지만 처리
    if reaction != "pushpin":
        return {"statusCode": 200, "body": "Ignored reaction"}

    # 지정된 채널만 처리
    if TARGET_CHANNELS and channel_id not in TARGET_CHANNELS:
        print(f"Channel {channel_id} not in target list {TARGET_CHANNELS}")
        return {"statusCode": 200, "body": "Channel not targeted"}

    # Public channel만 허용 (개인정보/기밀 누출 방지)
    channel_info = get_channel_info(channel_id)
    if channel_info.get("is_private") or channel_info.get("is_im") or channel_info.get("is_mpim"):
        print(f"Channel {channel_id} is private/DM. Ignored.")
        return {"statusCode": 200, "body": "Private channel ignored"}

    # 중복 처리 방지 (정확한 라인 단위 매칭)
    if is_message_pinned(channel_id, message_ts):
        print(f"Already processed: {channel_id}/{message_ts}")
        return {"statusCode": 200, "body": "Already processed"}

    # SQS 전송 전에 선점 표시 (race condition 방지)
    # 다른 인스턴스가 동시에 들어와도 이 표시로 중복 처리 방지
    try:
        mark_message_pinned(channel_id, message_ts)
    except Exception as e:
        print(f"Failed to mark pinned before SQS: {e}")

    # SQS로 전송하고 즉시 200 응답 (3초 타임아웃 방지)
    _send_to_sqs({
        "type": "slack_reaction",
        "channel_id": channel_id,
        "message_ts": message_ts,
    })

    return {"statusCode": 200, "body": "Accepted"}


def _send_to_sqs(message: dict):
    """SQS에 메시지 전송"""
    if not SQS_QUEUE_URL:
        raise RuntimeError("SQS_QUEUE_URL not set")
    sqs = boto3.client("sqs")
    sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(message),
    )
