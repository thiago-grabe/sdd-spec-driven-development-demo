from pydantic import BaseModel, Field, field_validator


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1)
    max_words: int | None = Field(default=150, ge=1, le=1000)

    @field_validator("text")
    @classmethod
    def text_not_whitespace_only(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("text must not be whitespace-only")
        return v


class SummarizeResponse(BaseModel):
    summary: str
    word_count: int
    model: str
    request_id: str


class ErrorResponse(BaseModel):
    error: str
    request_id: str
