"""ReviewLLMClient 동작 검증."""

from ai_review_bot.prompt import PromptBundle
from ai_review_bot.llm import ReviewLLMClient


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


def _make_client(
    reasoning_effort: str | None = None,
    text_verbosity: str | None = None,
) -> tuple[ReviewLLMClient, _DummyClient]:
    client = ReviewLLMClient(
        api_key="test",
        enabled=False,
        reasoning_effort=reasoning_effort,
        text_verbosity=text_verbosity,
    )
    dummy = _DummyClient()
    client._client = dummy  # type: ignore[attr-defined]
    client._enabled = True  # type: ignore[attr-defined]
    return client, dummy


def test_generate_should_request_default_reasoning_and_text_verbosity():
    """기본값으로 reasoning effort=low, text verbosity=low 설정이 적용돼야 한다."""
    llm, dummy = _make_client()

    result = llm.generate(PromptBundle(system="sys", user="usr"))

    assert result == "ok"
    assert dummy.responses.kwargs is not None
    assert dummy.responses.kwargs["reasoning"] == {"effort": "low"}
    assert dummy.responses.kwargs["text"] == {"verbosity": "low"}


def test_generate_should_allow_custom_reasoning_and_text_verbosity():
    """reasoning effort과 text verbosity를 인자로 재정의할 수 있어야 한다."""
    llm, dummy = _make_client(reasoning_effort="high", text_verbosity="medium")

    llm.generate(PromptBundle(system="sys", user="usr"))

    assert dummy.responses.kwargs is not None
    assert dummy.responses.kwargs["reasoning"] == {"effort": "high"}
    assert dummy.responses.kwargs["text"] == {"verbosity": "medium"}

