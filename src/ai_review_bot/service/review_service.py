"""비즈니스 서비스 계층."""

from __future__ import annotations

from typing import Final

from ai_review_bot.domain.prompt import PromptBundle, build_review_prompt
from ai_review_bot.entity.review import ReviewContext
from ai_review_bot.support.llm import ReviewLLMClient

_HEADERS: Final[list[str]] = [
    "주요 이슈 (Must Fix Before Merge)",
    "개선 제안 (Nice to Have)",
]
_PRAISE_MESSAGE: Final[str] = (
    "> 👏 주요 이슈와 개선 제안이 모두 없었습니다. 가이드를 잘 지킨 안정적인 변경이에요!"
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
            if header not in report:
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
    if any(header not in report for header in _HEADERS):
        return False
    for header in _HEADERS:
        section = _extract_section(report, header)
        if not _is_section_empty(section):
            return False
    return True


def _extract_section(report: str, header: str) -> str:
    if header not in report:
        return ""
    start = report.index(header) + len(header)
    section = report[start:]
    section = section.lstrip("\n")
    for other in _HEADERS:
        if other == header:
            continue
        marker = f"## {other}"
        idx = section.find(marker)
        if idx == -1:
            idx = section.find(other)
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
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    if not lines:
        return "- 없음"

    formatted: list[str] = []
    for line in lines:
        if line.startswith(("-", "*")):
            formatted.append(line)
        else:
            formatted.append(f"- {line}")
    return "\n".join(formatted)
