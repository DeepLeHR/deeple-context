import os
import json
from pathlib import Path


def load_secrets():
    """
    AWS Secrets Manager에서 민감한 환경변수를 읽어 os.environ에 주입합니다.
    로컬 환경에서는 .env 파일을 fallback으로 사용합니다.
    """
    secret_name = os.environ.get("SECRETS_MANAGER_NAME", "deeple-context-automation/prod")
    region = os.environ.get("AWS_REGION", "ap-northeast-2")

    # 1. Secrets Manager에서 읽기 시도
    try:
        import boto3
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        secrets = json.loads(response["SecretString"])
        for key, value in secrets.items():
            os.environ.setdefault(key, value)
        print(f"Loaded secrets from Secrets Manager: {secret_name}")
        return
    except ImportError:
        print("boto3 not available, skipping Secrets Manager")
    except Exception as e:
        print(f"Failed to load from Secrets Manager: {e}")

    # 2. Fallback: 로컬 .env 파일
    _load_dotenv()


def _load_dotenv():
    """로컬 .env 파일 로드"""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print(f".env not found at {env_path}, using existing env vars")
        return

    loaded = 0
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value:
            os.environ.setdefault(key, value)
            loaded += 1

    print(f"Loaded {loaded} vars from .env")
