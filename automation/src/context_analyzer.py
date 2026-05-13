import os
import json
from pathlib import Path
from typing import Optional
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")

# 로컬 repo 기준: automation/src/ → repo root
CONTEXT_ROOT = Path(__file__).parent.parent.parent


def get_context_tree() -> str:
    """deeple-context의 md 파일 목록을 로컬에서 조회"""
    files = []
    for path in sorted(CONTEXT_ROOT.rglob("*.md")):
        rel = path.relative_to(CONTEXT_ROOT)
        # 숨김 파일, automation/, _sync/ 제외
        if any(part.startswith(".") for part in rel.parts):
            continue
        if str(rel).startswith("automation/"):
            continue
        files.append(str(rel))
    return "\n".join(files)


def get_file_summaries(max_chars: int = 300) -> str:
    """각 md 파일의 경로 + 앞부분 요약 (로컬에서 읽기)"""
    summaries = []
    for path in sorted(CONTEXT_ROOT.rglob("*.md")):
        rel = path.relative_to(CONTEXT_ROOT)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if str(rel).startswith("automation/"):
            continue
        try:
            content = path.read_text(encoding="utf-8")
            preview = ""
            for line in content.strip().splitlines():
                stripped = line.strip()
                if stripped:
                    preview += stripped + " "
                if len(preview) >= max_chars:
                    break
            summaries.append(f"- {rel}: {preview[:max_chars].strip()}")
        except Exception:
            continue
        if len(summaries) >= 50:
            break
    return "\n".join(summaries)


SYSTEM_PROMPT = """당신은 'deeple-context'라는 공유 지식 저장소의 구조를 분석하고, 새로운 도메인 지식을 최적의 위치에 배치하는 AI 아키텍트입니다.

원칙:
1. 디렉토리를 과도하게 세분화하지 마세요. 최대 2~3단계 깊이까지만 사용합니다.
2. 기존 파일 중 내용이 유사한 것이 있다면 반드시 병합(append)을 우선 고려하세요.
3. 파일명은 kebab-case 영문으로 작성합니다.
4. Context는 "도메인 지식(what)"만 담습니다. 실행 방법(how)은 skill로 위임합니다.
5. 서비스 구분: dmand(디맨드), gocho(고초), shared(공통), new(새 서비스)
6. category는 다음 중 하나: domain, cs, policy, glossary, service, faq, meeting-note, screen-code, etc

출력은 반드시 아래 JSON 형식만 사용하세요. 설명은 JSON 외부에 쓰지 마세요.

{
  "service": "dmand|gocho|shared|new",
  "category": "domain|cs|policy|glossary|service|faq|meeting-note|screen-code|etc",
  "existing_file": "path/to/existing.md 또는 null",
  "action": "create|append|update",
  "new_path": "path/to/new-file.md",
  "reason": "왜 이 위치/파일을 선택했는지 한국어로 간단히",
  "title": "파일 상단 H1 제목 (한국어)"
}
"""


def analyze_placement(content: str) -> dict:
    """새 콘텐츠를 어디에 배치할지 LLM으로 분석"""
    tree = get_context_tree()
    summaries = get_file_summaries()

    user_prompt = f"""[현재 deeple-context 파일 목록]
{tree}

[기존 파일 요약]
{summaries}

[새로 저장할 콘텐츠]
{content[:4000]}

---
위 콘텐츠를 deeple-context에 저장하려고 합니다. 최적의 경로와 방식을 결정해주세요."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        result = json.loads(raw)
        return result
    except Exception as e:
        return {
            "service": "shared",
            "category": "etc",
            "existing_file": None,
            "action": "create",
            "new_path": "shared/unsorted-note.md",
            "reason": f"분석 실패 ({str(e)}), 기본 경로로 fallback",
            "title": "미분류 노트",
        }
