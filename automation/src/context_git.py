import os
import base64
import json
import re
from typing import Optional, Tuple
import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_OWNER = os.environ.get("CONTEXT_REPO_OWNER", "DeepLeHR")
REPO_NAME = os.environ.get("CONTEXT_REPO_NAME", "deeple-context")
BRANCH = os.environ.get("CONTEXT_BRANCH", "main")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"


def _get(path: str) -> dict:
    resp = requests.get(f"{API_BASE}{path}", headers=HEADERS)
    if resp.status_code == 404:
        return {"_not_found": True}
    resp.raise_for_status()
    return resp.json()


def _put(path: str, body: dict) -> dict:
    resp = requests.put(f"{API_BASE}{path}", headers=HEADERS, json=body)
    resp.raise_for_status()
    return resp.json()


def _post(path: str, body: dict) -> dict:
    resp = requests.post(f"{API_BASE}{path}", headers=HEADERS, json=body)
    resp.raise_for_status()
    return resp.json()


def get_file_info(file_path: str, branch: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    파일 존재 여부, sha, content(base64 decoded) 반환
    """
    ref = f"?ref={branch}" if branch else f"?ref={BRANCH}"
    data = _get(f"/contents/{file_path}{ref}")
    if data.get("_not_found"):
        return False, None, None
    content_b64 = data.get("content", "")
    try:
        content = base64.b64decode(content_b64).decode("utf-8")
    except Exception:
        content = ""
    return True, data.get("sha"), content


def get_repo_tree(branch: str = None) -> list:
    """repo의 모든 파일 경로 목록 반환 (md 파일만)"""
    tree_branch = branch or BRANCH
    data = _get(f"/git/trees/{tree_branch}?recursive=1")
    tree = data.get("tree", [])
    return [item["path"] for item in tree if item["type"] == "blob" and item["path"].endswith(".md")]


def get_file_preview(file_path: str, max_chars: int = 300, branch: str = None) -> str:
    """파일 내용 앞부분만 반환"""
    exists, _, content = get_file_info(file_path, branch)
    if not exists:
        return ""
    preview = ""
    for line in content.strip().splitlines():
        stripped = line.strip()
        if stripped:
            preview += stripped + " "
        if len(preview) >= max_chars:
            break
    return preview[:max_chars].strip()


def create_branch(branch_name: str, base_branch: str = None) -> str:
    """새 브랜치 생성. 이미 존재하면 기존 이름 반환"""
    base = base_branch or BRANCH
    base_ref = _get(f"/git/refs/heads/{base}")
    sha = base_ref["object"]["sha"]

    try:
        _post("/git/refs", {"ref": f"refs/heads/{branch_name}", "sha": sha})
    except requests.HTTPError as e:
        if e.response.status_code == 422:
            # 이미 존재
            pass
        else:
            raise
    return branch_name


def write_content(
    file_path: str,
    content: str,
    title: str = None,
    action: str = "create",
    branch: str = None,
) -> dict:
    """
    GitHub Contents API로 파일을 직접 커밋.
    action: create | append | update
    branch: None이면 main, 아니면 해당 브랜치
    title이 None이면 마크다운 헤더를 붙이지 않습니다 (log, yaml 등)
    """
    target_branch = branch or BRANCH
    exists, sha, existing_content = get_file_info(file_path, target_branch)

    if action == "append" and exists:
        new_content = f"{existing_content}\n\n---\n\n{content}"
    elif action == "update" and exists:
        new_content = content
    else:
        if title and not content.strip().startswith("#"):
            new_content = f"# {title}\n\n{content}"
        else:
            new_content = content

    body = {
        "message": f"docs: {title or file_path}",
        "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
        "branch": target_branch,
    }
    if exists:
        body["sha"] = sha

    result = _put(f"/contents/{file_path}", body)
    return {
        "commit_hash": result.get("commit", {}).get("sha", "")[:7],
        "file_path": file_path,
        "html_url": result.get("content", {}).get("html_url", ""),
    }


def create_pull_request(title: str, body: str, head: str, base: str = None) -> dict:
    """PR 생성"""
    base_branch = base or BRANCH
    result = _post("/pulls", {
        "title": title,
        "body": body,
        "head": head,
        "base": base_branch,
    })
    return {
        "pr_number": result.get("number"),
        "pr_url": result.get("html_url"),
        "pr_title": result.get("title"),
    }


def sanitize_branch_name(name: str) -> str:
    """브랜치명으로 사용할 수 없는 문자 제거"""
    return re.sub(r"[^a-zA-Z0-9._-]", "-", name)[:50]
