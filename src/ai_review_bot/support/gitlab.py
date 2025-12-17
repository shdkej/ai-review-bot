"""GitLab 연동 유틸리티."""

from __future__ import annotations

import re
from typing import Any, Callable, Mapping

import requests

_ISSUE_IID_PATTERN = re.compile(
    r"(?:https?://[^\s]+?/"
    r"(?:(?:-)/)?issues/(?P<link_iid>\d+)"  # https://gitlab.com/.../-/issues/123 또는
    # .../issues/123
    r"|(?:^|[\s\[(])#(?P<reference_iid>\d+))",  # MR 설명의 #123 형식 참조(링크 내부 #은 무시)
    re.IGNORECASE,
)


def extract_issue_iids(text: str) -> list[str]:
    """문자열에서 GitLab 이슈 IID 목록을 추출한다."""
    if not text:
        return []
    issue_iids: list[str] = []
    for match in _ISSUE_IID_PATTERN.finditer(text):
        iid = match.group("link_iid") or match.group("reference_iid")
        if iid not in issue_iids:
            issue_iids.append(iid)
    return issue_iids


def _default_issue_fetcher(
    issue_iid: str,
    *,
    api_url: str,
    project_id: str,
    token: str,
) -> Mapping[str, Any] | None:
    url = f"{api_url}/projects/{project_id}/issues/{issue_iid}"
    try:
        resp = requests.get(
            url,
            headers={"PRIVATE-TOKEN": token},
            timeout=10,
        )
    except Exception:
        return None
    if not resp.ok:
        return None
    try:
        return resp.json()
    except ValueError:
        return None


def collect_issue_descriptions(
    description: str,
    *,
    api_url: str,
    project_id: str,
    token: str,
    fetcher: Callable[[str, str, str, str], Mapping[str, Any] | None] | None = None,
) -> list[str]:
    """PR/MR 설명에 포함된 이슈 링크를 따라가 이슈 본문을 수집한다."""
    issue_iids = extract_issue_iids(description)
    if not issue_iids:
        return []

    fetch = fetcher or _default_issue_fetcher
    bodies: list[str] = []

    for issue_iid in issue_iids:
        data = fetch(issue_iid, api_url, project_id, token)
        if not data:
            continue
        body = str(data.get("description") or "").strip()
        if body:
            bodies.append(body)

    return bodies
