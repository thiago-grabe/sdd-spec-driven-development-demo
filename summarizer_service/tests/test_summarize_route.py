import logging
from unittest.mock import AsyncMock

import httpx
import pytest
from openai import OpenAIError

_FAKE_REQUEST = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")


async def test_happy_path_200(async_client: httpx.AsyncClient) -> None:
    resp = await async_client.post(
        "/summarize", json={"text": "Hello world from the test."}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "summary" in body
    assert "word_count" in body
    assert "model" in body
    assert "request_id" in body
    assert body["word_count"] == len(body["summary"].split())


async def test_empty_text_422_no_call(
    async_client: httpx.AsyncClient, mock_openai_client
) -> None:
    resp = await async_client.post("/summarize", json={"text": ""})
    assert resp.status_code == 422
    mock_openai_client.chat.completions.create.assert_not_called()


async def test_whitespace_text_422_no_call(
    async_client: httpx.AsyncClient, mock_openai_client
) -> None:
    resp = await async_client.post("/summarize", json={"text": "   "})
    assert resp.status_code == 422
    mock_openai_client.chat.completions.create.assert_not_called()


async def test_oversize_413_no_call(
    async_client: httpx.AsyncClient, mock_openai_client
) -> None:
    resp = await async_client.post("/summarize", json={"text": "x" * 10_001})
    assert resp.status_code == 413
    mock_openai_client.chat.completions.create.assert_not_called()


async def test_upstream_failure_502(
    async_client: httpx.AsyncClient, mock_openai_client
) -> None:
    mock_openai_client.chat.completions.create = AsyncMock(
        side_effect=OpenAIError("upstream broke")
    )
    resp = await async_client.post("/summarize", json={"text": "Some valid text."})
    assert resp.status_code == 502
    body = resp.json()
    assert "error" in body
    assert "upstream broke" not in body["error"]
    assert "request_id" in body


async def test_request_id_on_every_response(
    async_client: httpx.AsyncClient, mock_openai_client
) -> None:
    def _check(resp: httpx.Response) -> None:
        body = resp.json()
        assert "request_id" in body, f"missing request_id for status {resp.status_code}"
        assert "X-Request-ID" in resp.headers
        assert resp.headers["X-Request-ID"] == body["request_id"]

    # 200
    resp = await async_client.post("/summarize", json={"text": "Valid input text."})
    assert resp.status_code == 200
    _check(resp)

    # 422 — empty body
    resp = await async_client.post("/summarize", json={"text": ""})
    assert resp.status_code == 422
    _check(resp)

    # 413 — oversize
    resp = await async_client.post("/summarize", json={"text": "x" * 10_001})
    assert resp.status_code == 413
    _check(resp)

    # 502 — upstream error
    mock_openai_client.chat.completions.create = AsyncMock(
        side_effect=OpenAIError("boom")
    )
    resp = await async_client.post("/summarize", json={"text": "Valid input text."})
    assert resp.status_code == 502
    _check(resp)


async def test_input_text_never_logged(
    async_client: httpx.AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    sentinel = "UNIQUE_SENTINEL_XYZ_98765_SECRET"

    with caplog.at_level(logging.DEBUG):
        resp = await async_client.post("/summarize", json={"text": sentinel})

    assert resp.status_code == 200

    # Sentinel must not appear in any log record message
    for record in caplog.records:
        assert sentinel not in record.getMessage(), (
            f"Sentinel found in log record: {record.getMessage()}"
        )

    # Sentinel must not appear in the response body
    assert sentinel not in resp.text
