"""비즈니스 서비스 계층."""

from __future__ import annotations

from typing import Final

from ai_review_bot.prompt import PromptBundle, build_review_prompt
from ai_review_bot.review import ReviewContext
from ai_review_bot.llm import ReviewLLMClient

_HEADERS: Final[list[str]] = [
    "핵심 요약",
    "안정성을 위해 먼저 살펴보면 좋은 부분",
    "추가 개선 아이디어",
]
_PRAISE_MESSAGE: Final[str] = (
    "> 👏 핵심 요약, 안정성을 위해 먼저 살펴보면 좋은 부분, 추가 개선 아이디어이 모두 없었습니다. 가이드를 잘 지킨 안정적인 변경이에요!"
)


class ReviewService:
    """리뷰 생성 워크플로를 조합한다."""

    def __init__(self, llm_client: ReviewLLMClient | None = None) -> None:
        self._llm_client = llm_client or ReviewLLMClient()

    def create_review(self, context: ReviewContext) -> str:
        context.validate()
        if not self._llm_client.is_available:
            raise RuntimeError(
                "OpenAI API를 사용할 수 없습니다. 환경 변수 OPENAI_API_KEY와 "
                "패키지 의존성(openai)이 올바르게 설정되었는지 확인해 주세요."
            )
        bundle: PromptBundle = build_review_prompt(context)
        report = self._llm_client.generate(bundle)
        report = self._normalize_markdown(report)
        return self._append_praise_if_empty(report)

    @staticmethod
    def _normalize_markdown(report: str) -> str:
        if not report:
            return report

        formatted_sections: list[str] = []
        for header in _HEADERS:
            marker = f"## {header}"
            if marker not in report:
                # 헤더가 하나라도 빠져 있으면 원본 형식을 유지한다.
                return report
            section = _extract_section(report, header)
            formatted = _format_section(section)
            formatted_sections.append(f"## {header}\n{formatted}")

        return "\n\n".join(formatted_sections).strip()

    @staticmethod
    def _append_praise_if_empty(report: str) -> str:
        if _is_review_empty(report):
            return f"{report.rstrip()}\n\n{_PRAISE_MESSAGE}\n"
        return report


def _is_review_empty(report: str) -> bool:
    """모든 헤더 섹션이 비어있는지 확인한다."""
    if any(f"## {header}" not in report for header in _HEADERS):
        return False
    for header in _HEADERS:
        section = _extract_section(report, header)
        if not _is_section_empty(section):
            return False
    return True


def _extract_section(report: str, header: str) -> str:
    """헤더 마커(## ...)를 기준으로 섹션을 추출한다."""
    marker = f"## {header}"
    if marker not in report:
        return ""
    start = report.index(marker) + len(marker)
    section = report[start:]
    section = section.lstrip("\n")
    for other in _HEADERS:
        if other == header:
            continue
        other_marker = f"## {other}"
        idx = section.find(other_marker)
        if idx != -1:
            section = section[:idx]
            break
    return section.strip()


def _is_section_empty(section: str) -> bool:
    if not section:
        return True
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    if not lines:
        return True
    for line in lines:
        normalized = line.lstrip("-*•").strip()
        if normalized != "없음":
            return False
    return True


def _format_section(section: str) -> str:
    raw_lines = section.splitlines()
    cleaned: list[str] = []
    previous_blank = False
    for raw in raw_lines:
        if not raw.strip():
            if cleaned and not previous_blank:
                cleaned.append("")
            previous_blank = True
            continue
        cleaned.append(raw.rstrip())
        previous_blank = False

    if not cleaned:
        return "- 없음"

    return "\n".join(cleaned)

