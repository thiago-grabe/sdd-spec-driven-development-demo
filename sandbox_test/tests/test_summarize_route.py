import logging
from unittest.mock import AsyncMock

import openai
import pytest


@pytest.mark.asyncio
async def test_happy_path_200(async_client) -> None:
    """R1: valid body returns 200 with a schema-valid SummarizeResponse."""
    client, _ = async_client
    resp = await client.post("/summarize", json={"text": "Hello world this is a test."})
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "word_count" in data
    assert "model" in data
    assert "request_id" in data
    assert data["word_count"] == len(data["summary"].split())


@pytest.mark.asyncio
async def test_empty_text_422_no_call(async_client) -> None:
    """R2: empty/whitespace text → 422, no model call."""
    client, mock = async_client
    resp = await client.post("/summarize", json={"text": "   "})
    assert resp.status_code == 422
    mock.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
async def test_oversize_413_no_call(async_client) -> None:
    """R3: text > 10k chars → 413, no model call."""
    client, mock = async_client
    big_text = "a" * 10_001
    resp = await client.post("/summarize", json={"text": big_text})
    assert resp.status_code == 413
    mock.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
async def test_upstream_failure_502(async_client) -> None:
    """R4: upstream error → 502 with ErrorResponse; raw error not leaked."""
    client, mock = async_client
    mock.chat.completions.create = AsyncMock(
        side_effect=openai.OpenAIError("raw upstream secret message")
    )
    resp = await client.post("/summarize", json={"text": "Valid text here."})
    assert resp.status_code == 502
    data = resp.json()
    assert "error" in data
    assert "request_id" in data
    assert "raw upstream secret message" not in resp.text


@pytest.mark.asyncio
async def test_request_id_on_every_response(async_client) -> None:
    """R5: every response carries request_id in body and X-Request-ID header, and they match."""
    client, mock = async_client

    # 200 success
    resp = await client.post("/summarize", json={"text": "Valid text for testing request id."})
    _assert_request_id(resp)

    # 422 empty
    resp = await client.post("/summarize", json={"text": "   "})
    _assert_request_id(resp)

    # 413 oversize
    resp = await client.post("/summarize", json={"text": "a" * 10_001})
    _assert_request_id(resp)

    # 502 upstream failure
    mock.chat.completions.create = AsyncMock(side_effect=openai.OpenAIError("err"))
    resp = await client.post("/summarize", json={"text": "trigger 502"})
    _assert_request_id(resp)


def _assert_request_id(resp) -> None:
    data = resp.json()
    assert "request_id" in data, f"Missing request_id in {resp.status_code} body"
    assert "X-Request-ID" in resp.headers, f"Missing X-Request-ID header on {resp.status_code}"
    assert data["request_id"] == resp.headers["X-Request-ID"]


@pytest.mark.asyncio
async def test_input_text_never_logged(async_client, caplog) -> None:
    """R7: input text must never appear in log records or response bodies."""
    client, _ = async_client
    marker = "SUPER_SECRET_UNIQUE_MARKER_XYZ_12345"
    with caplog.at_level(logging.DEBUG, logger="summarizer_service"):
        resp = await client.post("/summarize", json={"text": f"Some text with {marker} in it."})
    for record in caplog.records:
        assert marker not in record.getMessage(), (
            f"Input text marker found in log: {record.getMessage()}"
        )
    assert marker not in resp.text
