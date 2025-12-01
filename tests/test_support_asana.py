"""Asana 연동 유틸리티 테스트."""

from ai_review_bot.support.asana import (
    build_ticket_context_from_asana,
)


def test_build_ticket_context_returns_none_when_no_asana_link():
    """Asana 링크가 없으면 None을 반환해야 한다."""
    description = "이 MR은 단순한 리팩토링입니다. 관련 링크 없음."

    result = build_ticket_context_from_asana(description, fetcher=lambda _tid: None)

    assert result is None


def test_build_ticket_context_uses_provided_fetcher_and_formats_output():
    """주입된 fetcher를 사용해 티켓 요약을 구성해야 한다."""
    description = "관련 작업: https://app.asana.com/0/123456/789012"

    def _fake_fetcher(task_id: str):
        assert task_id == "789012"
        return {
            "name": "주문 취소 플로우 개선",
            "notes": "환불 실패 시 재시도 로직 추가",
            "permalink_url": "https://app.asana.com/0/123456/789012",
        }

    result = build_ticket_context_from_asana(description, fetcher=_fake_fetcher)

    assert result is not None
    assert "[Asana] 주문 취소 플로우 개선" in result
    assert "환불 실패 시 재시도 로직 추가" in result
    assert "https://app.asana.com/0/123456/789012" in result


def test_build_ticket_context_supports_new_asana_url_format():
    """신규 Asana URL 포맷(app.asana.com/1/.../project/.../task/...)도 인식해야 한다."""
    description = (
        "요구사항: https://app.asana.com/1/173176713468093/project/1119186039581903/"
        "task/1212083742273047?focus=true"
    )

    captured_ids: list[str] = []

    def _fake_fetcher(task_id: str):
        captured_ids.append(task_id)
        return {
            "name": "신규 포맷 티켓",
            "notes": "신규 URL 패턴 테스트",
            "permalink_url": (
                "https://app.asana.com/1/173176713468093/project/1119186039581903/"
                "task/1212083742273047"
            ),
        }

    result = build_ticket_context_from_asana(description, fetcher=_fake_fetcher)

    assert captured_ids == ["1212083742273047"]
    assert result is not None
    assert "[Asana] 신규 포맷 티켓" in result
    assert "신규 URL 패턴 테스트" in result


