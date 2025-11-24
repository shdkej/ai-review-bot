"""ReviewLLMClient 동작 검증."""

from ai_review_bot.domain.prompt import PromptBundle
from ai_review_bot.support.llm import ReviewLLMClient


class _DummyResponse:
    def __init__(self, text: str = "ok") -> None:
        self.output_text = text


class _DummyResponses:
    def __init__(self) -> None:
        self.kwargs: dict | None = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return _DummyResponse()


class _DummyClient:
    def __init__(self) -> None:
        self.responses = _DummyResponses()


def _make_client(reasoning_effort: str | None = None) -> tuple[ReviewLLMClient, _DummyClient]:
    client = ReviewLLMClient(api_key="test", enabled=False, reasoning_effort=reasoning_effort)
    dummy = _DummyClient()
    client._client = dummy  # type: ignore[attr-defined]
    client._enabled = True  # type: ignore[attr-defined]
    return client, dummy


def test_generate_should_request_minimal_reasoning_by_default():
    """기본값으로 reasoning effort가 minimal로 설정되어야 한다."""
    llm, dummy = _make_client()

    result = llm.generate(PromptBundle(system="sys", user="usr"))

    assert result == "ok"
    assert dummy.responses.kwargs is not None
    assert dummy.responses.kwargs["reasoning"] == {"effort": "minimal"}


def test_generate_should_allow_custom_reasoning_effort():
    """reasoning_effort 인자를 통해 값을 재정의할 수 있어야 한다."""
    llm, dummy = _make_client(reasoning_effort="none")

    llm.generate(PromptBundle(system="sys", user="usr"))

    assert dummy.responses.kwargs is not None
    assert dummy.responses.kwargs["reasoning"] == {"effort": "none"}

