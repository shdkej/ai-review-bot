"""Asana 티켓 정보를 읽어와 리뷰 컨텍스트용 텍스트로 변환하는 유틸리티."""

from __future__ import annotations

import os
import re
import sys
from typing import Any, Callable, Mapping

import requests

_ASANA_URL_PATTERN = re.compile(
    r"https://app\.asana\.com/"
    r"(?:(?:0/\d+/)|(?:1/\d+/project/\d+/task/))"
    r"(?P<task_id>\d+)",
    re.IGNORECASE,
)


def _extract_task_ids(text: str) -> list[str]:
    """설명 문자열에서 Asana task id 목록을 추출한다."""
    if not text:
        return []
    ids: list[str] = []
    for match in _ASANA_URL_PATTERN.finditer(text):
        task_id = match.group("task_id")
        if task_id not in ids:
            ids.append(task_id)
    return ids


def _default_fetcher(task_id: str) -> Mapping[str, Any] | None:
    """Asana API를 호출해 태스크 정보를 가져온다.

    ASANA_ACCESS_TOKEN이 없거나 호출 실패 시 None을 반환한다.
    """
    token = os.getenv("ASANA_ACCESS_TOKEN")
    if not token:
        print("[llm-code-review] ERROR: ASANA_ACCESS_TOKEN is missing", file=sys.stderr)
        return None

    url = f"https://app.asana.com/api/1.0/tasks/{task_id}"
    try:
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
    except Exception:
        return None

    if not resp.ok:
        return None

    try:
        data = resp.json()
    except ValueError:
        return None

    return data.get("data") or None


def build_ticket_context_from_asana(
    description: str,
    fetcher: Callable[[str], Mapping[str, Any] | None] | None = None,
    extra_texts: list[str] | None = None,
) -> str | None:
    """MR description에서 Asana 링크를 찾아 티켓 요약 텍스트를 생성한다.

    - Asana 링크가 없으면 None을 반환한다.
    - ASANA_ACCESS_TOKEN이 없거나 API 호출이 실패하면 None을 반환한다.
    - 테스트에서는 fetcher를 주입해 네트워크 호출 없이 동작을 검증할 수 있다.
    """
    texts = [description] + (extra_texts or [])
    task_ids: list[str] = []
    for text in texts:
        for task_id in _extract_task_ids(text):
            if task_id not in task_ids:
                task_ids.append(task_id)

    if not task_ids:
        print("[llm-code-review] ERROR: No Asana task IDs found in description", file=sys.stderr)
        return None

    print(f"[llm-code-review] found Asana task ids: {', '.join(task_ids)}")

    fetch = fetcher or _default_fetcher
    lines: list[str] = []

    for task_id in task_ids:
        data = fetch(task_id)
        if not data:
            continue
        name = str(data.get("name") or "").strip()
        notes = str(data.get("notes") or "").strip()
        permalink = str(data.get("permalink_url") or "").strip()

        if not name and not notes and not permalink:
            continue

        lines.append(f"[Asana] {name or task_id}")
        if notes:
            lines.append(notes)
        if permalink:
            lines.append(f"링크: {permalink}")
        lines.append("")  # 티켓 간 구분용 빈 줄

    result = "\n".join(lines).strip()
    return result or None
