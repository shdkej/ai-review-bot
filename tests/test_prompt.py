"""Prompt 규칙 검증 테스트."""

from ai_review_bot.prompt import SYSTEM_PROMPT


def test_system_prompt_should_forbid_bullets_on_headings() -> None:
    """섹션 제목 앞에 불릿을 붙이지 말라는 규칙이 명시돼야 한다."""
    assert "Summary/Must Fix/Nice to Have/도메인 제목 앞에 불릿" in SYSTEM_PROMPT, (
        "섹션 제목 불릿 금지 규칙이 누락됨"
    )


def test_system_prompt_should_forbid_blank_lines_between_summary_items() -> None:
    """Summary 항목 사이에 빈 줄을 금지하는 규칙이 명시돼야 한다."""
    assert (
        "Summary 항목 `- Must Fix`, `- Nice to Have`, `- 핵심 위험 요약` 사이에 빈 줄을 넣지 말 것"
        in SYSTEM_PROMPT
    ), "Summary 항목 사이 공백 금지 규칙이 누락됨"


def test_system_prompt_should_prioritize_requirement_based_review() -> None:
    """티켓/요구사항 컨텍스트를 기준으로 리뷰하라는 지침이 있어야 한다."""
    assert "티켓/요구사항" in SYSTEM_PROMPT
    assert "요구사항을 충족하는지" in SYSTEM_PROMPT
