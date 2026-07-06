class PayloadTooLargeError(Exception):
    """Raised when the input text exceeds the configured character cap."""

    input_length: int = 0


class SummarizerError(Exception):
    """Raised when the upstream OpenAI call fails or times out."""
