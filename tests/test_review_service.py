"""ReviewService 관련 테스트."""

from ai_review_bot.service.review_service import _extract_section


def test_extract_section_should_find_by_marker_not_plain_text():
    """본문에 헤더 이름이 포함되어 있어도 마커(## ...) 기준으로 찾아야 한다."""
    report = """## Summary
This is a summary section. The word Summary appears here but should not be confused.

## Must Fix
- Issue 1
- Issue 2

## Nice to Have
- Suggestion 1"""

    result = _extract_section(report, "Summary")
    assert "This is a summary section" in result
    assert "Must Fix" not in result
    assert "Nice to Have" not in result


def test_extract_section_should_handle_header_in_content():
    """본문 내용에 헤더 이름이 포함된 경우에도 올바르게 추출해야 한다."""
    report = """## Summary
The word Summary appears in this content, but we should extract correctly.

## Must Fix
- Fix the Summary section issue
- Another issue

## Nice to Have
- Nice suggestion"""

    result = _extract_section(report, "Summary")
    assert "The word Summary appears" in result
    assert "Fix the Summary section issue" not in result
    assert "Must Fix" not in result


