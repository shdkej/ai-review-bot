"""Prompt 빌더가 티켓/요구사항 컨텍스트를 포함하는지 검증."""

from ai_review_bot.prompt import build_review_prompt
from ai_review_bot.review import ReviewContext


def test_build_review_prompt_includes_ticket_context_when_present():
    """ticket_context가 있으면 프롬프트에 별도 섹션으로 포함돼야 한다."""
    context = ReviewContext(
        project_name="kop-web",
        pr_number="123",
        diff="diff --git a/foo.py b/foo.py\n",
        ticket_context="Asana: 주문 취소 플로우 개선\n상세: 환불 실패 시 재시도 필요",
    )

    bundle = build_review_prompt(context)

    assert "[티켓/요구사항]" in bundle.user
    assert "Asana: 주문 취소 플로우 개선" in bundle.user
    assert "상세: 환불 실패 시 재시도 필요" in bundle.user


def test_build_review_prompt_includes_project_overview_when_present():
    """project_overview가 있으면 프롬프트에 별도 섹션으로 포함돼야 한다."""
    context = ReviewContext(
        project_name="kop-api",
        pr_number="99",
        diff="diff --git a/bar.js b/bar.js\n",
        project_overview="이 프로젝트는 GraphQL API 서버입니다.",
    )

    bundle = build_review_prompt(context)

    assert "[프로젝트 개요]" in bundle.user
    assert "GraphQL API 서버" in bundle.user
