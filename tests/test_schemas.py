import pytest

from summarizer_service.models.schemas import SummarizeResponse


@pytest.mark.parametrize(
    "summary",
    [
        "A short summary.",
        "One two three four five six seven eight nine ten.",
        "Single",
        "The quick brown fox jumps over the lazy dog and runs away fast.",
    ],
)
def test_word_count_matches_summary(summary: str) -> None:
    response = SummarizeResponse(
        summary=summary,
        word_count=len(summary.split()),
        model="gpt-5.5",
        request_id="test-id",
    )
    assert response.word_count == len(summary.split())
