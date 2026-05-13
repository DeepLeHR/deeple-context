import json
import base64
import urllib.parse

from commander import command_processor
from actor import action_processor, shortcut_processor
from event_processor import handle_slack_event
from cron_handler import run_daily_sync
from context_save_handler import save_slack_thread


def lambda_handler(event, context):
    print("=== RAW EVENT ===")
    print(json.dumps(event, default=str, ensure_ascii=False)[:2000])

    # 1. SQS trigger (Worker)
    if event.get("Records"):
        return _handle_sqs_records(event["Records"])

    # 2. EventBridge Cron (자정)
    if event.get("source") == "aws.events":
        print("Cron triggered")
        return run_daily_sync()

    # 3. API Gateway (Slack)
    body_raw = event.get("body", "")
    is_base64 = event.get("isBase64Encoded", False)

    if is_base64:
        body_raw = base64.b64decode(body_raw).decode("utf-8")

    # JSON body인지 판단 (Slack Event API)
    try:
        body_json = json.loads(body_raw)
        print("Parsed as JSON (Event API)")

        # URL Verification (처음 등록 시)
        if body_json.get("type") == "url_verification":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/plain"},
                "body": body_json["challenge"],
            }

        # Event Callback
        if body_json.get("type") == "event_callback":
            return handle_slack_event(body_json)

        return {"statusCode": 400, "body": "Unknown JSON payload"}

    except json.JSONDecodeError:
        print("Parsed as form-urlencoded (Slash/Interactive)")
        pass

    # 4. form-urlencoded (Slash Command / Block Actions / Message Shortcut)
    decoded_body = urllib.parse.unquote(body_raw)
    body = urllib.parse.parse_qs(decoded_body)

    print(body)

    is_command = "payload" not in body

    if is_command:
        command = check_null(body["command"][0])
        text = body.get("text", [""])[0]
        response_url = check_null(body["response_url"][0])

        print({"command": command, "text": text, "response_url": response_url})

        return command_processor(command, text, response_url)
    else:
        payload = json.loads(body["payload"][0])
        payload_type = payload.get("type", "")
        response_url = check_null(payload["response_url"])

        if payload_type == "message_action":
            return shortcut_processor(payload, response_url)
        else:
            blocks = check_null(payload["state"]["values"])
            action = check_null(payload["actions"][0])
            return action_processor(blocks, action, response_url)


def _handle_sqs_records(records):
    """SQS Worker: 실제 처리 수행"""
    errors = []
    for record in records:
        body = json.loads(record["body"])
        print(f"SQS message: {body}")
        try:
            if body.get("type") == "slack_reaction":
                result = save_slack_thread(
                    body["channel_id"],
                    body["message_ts"],
                    response_url=None,
                )
                if result.get("statusCode") != 200:
                    errors.append(result.get("error", "Unknown error"))
            else:
                errors.append(f"Unknown message type: {body.get('type')}")
        except Exception as e:
            errors.append(str(e))

    if errors:
        print(f"SQS processing errors: {errors}")
        # SQS DLQ로 전달되도록 500 반환 (retry)
        return {"statusCode": 500, "body": json.dumps({"errors": errors}, ensure_ascii=False)}

    return {"statusCode": 200, "body": "OK"}


def check_null(*values):
    for value in values:
        if value is None:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    "요청이 정상적으로 입력되지 않았습니다.", ensure_ascii=False
                ),
            }

    if len(values) == 1:
        return values[0]
    else:
        return values
