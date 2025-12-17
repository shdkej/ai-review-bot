"""GitLab 이슈 본문 수집 유틸리티 테스트."""

from ai_review_bot.support.gitlab import collect_issue_descriptions, extract_issue_iids


def test_extract_issue_iids_should_find_links_with_dash_segment():
    """- 세그먼트를 포함한 GitLab 이슈 링크에서 IID를 추출해야 한다."""
    text = (
        "관련 이슈: https://gitlab.com/org/proj/-/issues/42 "
        "그리고 https://gitlab.com/org/proj/issues/99"
    )

    result = extract_issue_iids(text)

    assert result == ["42", "99"]


def test_collect_issue_descriptions_should_use_fetcher_and_skip_empty():
    """주입된 fetcher로 이슈 본문을 모으고 빈 본문은 건너뛴다."""
    fetched: list[str] = []

    def _fake_fetcher(issue_iid: str, api_url: str, project_id: str, token: str):
        fetched.append(issue_iid)
        if issue_iid == "99":
            return {"description": ""}
        return {"description": f"본문 {issue_iid}"}

    bodies = collect_issue_descriptions(
        "https://example.com/group/proj/-/issues/42 다른 링크 https://example.com/issues/99",
        api_url="https://gitlab.example.com/api/v4",
        project_id="123",
        token="token",
        fetcher=_fake_fetcher,
    )

    assert fetched == ["42", "99"]
    assert bodies == ["본문 42"]
