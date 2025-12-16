"""리뷰 요청의 최상위 제어 흐름."""

from __future__ import annotations

from ai_review_bot.review import ReviewContext
from ai_review_bot.review_service import ReviewService


class ReviewController:
    """Lambda 스타일 핸들러 역할을 수행한다."""

    def __init__(self, service: ReviewService | None = None) -> None:
        self._service = service or ReviewService()

    def run(self, *, project_name: str, pr_number: str, raw_diff: str) -> str:
        context = ReviewContext(
            project_name=project_name,
            pr_number=pr_number,
            diff=raw_diff,
        )
        return self._service.create_review(context)
