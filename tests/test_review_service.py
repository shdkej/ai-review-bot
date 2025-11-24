"""ReviewService 관련 테스트."""

from ai_review_bot.service.review_service import _extract_section, _format_section


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


def test_format_section_should_keep_existing_headings_without_prefix():
    """도메인 헤딩과 파일명은 불릿 없이 그대로 유지되어야 한다."""
    section = """### Maintainability
(unknown.py:2-2)
  - 문제: 내용
""".strip()

    formatted = _format_section(section)

    assert formatted.startswith("### Maintainability")
    assert "(unknown.py:2-2)" in formatted
    assert formatted.splitlines()[0] == "### Maintainability"
    assert not formatted.startswith("- ")


def test_format_section_should_preserve_single_blank_lines_between_issues():
    """원본 섹션에 있는 단일 빈 줄은 유지해야 한다."""
    section = """### Maintainability
(unknown.py:2-2)

### Performance
(foo.py:10-12)
""".strip()

    formatted = _format_section(section)

    assert "\n\n" in formatted
    assert formatted.split("\n\n")[1].startswith("### Performance")



