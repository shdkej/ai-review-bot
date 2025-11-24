"""OpenAI Responses API를 통한 GPT-5 호출 래퍼."""

from __future__ import annotations

import os
from typing import Any

try:  # pragma: no cover - import 오류는 런타임에서만 감지됨
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment,misc]

from ai_review_bot.domain.prompt import PromptBundle


class ReviewLLMClient:
    """OpenAI GPT-5 모델과 통신하는 헬퍼."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        enabled: bool | None = None,
        reasoning_effort: str | None = None,
    ) -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._model = model or os.getenv("OPENAI_REVIEW_MODEL", "gpt-5.1")
        self._enabled = enabled if enabled is not None else bool(self._api_key)
        effort = (
            reasoning_effort
            or os.getenv("OPENAI_REVIEW_REASONING_EFFORT")
            or "minimal"
        )
        self._reasoning_effort = effort.strip() or None
        self._client: Any | None = None

        if self._enabled and OpenAI is not None:
            self._client = OpenAI(api_key=self._api_key)

    @property
    def is_available(self) -> bool:
        return self._enabled and self._client is not None

    def generate(self, prompt: PromptBundle) -> str:
        if not self.is_available or self._client is None:
            raise RuntimeError("LLM client is disabled; set OPENAI_API_KEY to enable it.")

        try:
            payload: dict[str, Any] = {
                "model": self._model,
                "input": [
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": prompt.system}],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt.user}],
                    },
                ],
            }
            if self._reasoning_effort:
                payload["reasoning"] = {"effort": self._reasoning_effort}

            response = self._client.responses.create(**payload)
        except Exception as exc:  # pragma: no cover - 네트워크 오류에 대한 방어
            message = str(exc)
            status = getattr(exc, "status_code", None)
            if status == 401 or "invalid_api_key" in message.lower():
                raise RuntimeError(
                    "OpenAI API 키가 유효하지 않습니다. 키 값을 다시 확인해 주세요."
                ) from exc
            raise RuntimeError(f"Failed to call OpenAI Responses API: {message}") from exc

        output_text = getattr(response, "output_text", None)
        if not output_text:
            raise RuntimeError("OpenAI response did not include text output.")
        return str(output_text)
