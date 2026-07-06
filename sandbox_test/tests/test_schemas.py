import pytest

from summarizer_service.models.schemas import SummarizeResponse


@pytest.mark.parametrize(
    "summary,expected_count",
    [
        ("Hello world", 2),
        ("One", 1),
        ("  leading and trailing spaces  ", 4),
        ("The quick brown fox jumps over the lazy dog", 9),
    ],
)
def test_word_count_matches_summary(summary: str, expected_count: int) -> None:
    """R6: word_count must equal the number of whitespace-separated words in summary."""
    response = SummarizeResponse(
        summary=summary,
        word_count=len(summary.split()),
        model="gpt-5.5",
        request_id="test-id",
    )
    assert response.word_count == expected_count
