import logging
from unittest.mock import AsyncMock

from summarizer_service.exceptions import SummarizerError


async def test_happy_path_200(app_client) -> None:
    client, mock = app_client
    response = await client.post("/summarize", json={"text": "Hello world."})

    assert response.status_code == 200
    body = response.json()
    assert "summary" in body
    assert "word_count" in body
    assert "model" in body
    assert "request_id" in body
    assert body["word_count"] == len(body["summary"].split())


async def test_empty_text_422_no_call(app_client) -> None:
    client, mock = app_client
    response = await client.post("/summarize", json={"text": "   "})

    assert response.status_code == 422
    assert mock.chat.completions.create.call_count == 0


async def test_oversize_413_no_call(app_client) -> None:
    client, mock = app_client
    big_text = "a" * 10_001
    response = await client.post("/summarize", json={"text": big_text})

    assert response.status_code == 413
    assert mock.chat.completions.create.call_count == 0


async def test_upstream_failure_502(app_client) -> None:
    client, mock = app_client
    mock.chat.completions.create = AsyncMock(side_effect=SummarizerError("boom"))

    response = await client.post("/summarize", json={"text": "Some text."})

    assert response.status_code == 502
    body = response.json()
    assert "boom" not in body.get("error", "")
    assert "request_id" in body


async def test_request_id_on_every_response(app_client) -> None:
    client, mock = app_client

    # 200
    r = await client.post("/summarize", json={"text": "Hello."})
    assert r.status_code == 200
    assert r.json()["request_id"] == r.headers["x-request-id"]

    # 422
    r = await client.post("/summarize", json={"text": "   "})
    assert r.status_code == 422
    assert r.json()["request_id"] == r.headers["x-request-id"]

    # 413
    r = await client.post("/summarize", json={"text": "a" * 10_001})
    assert r.status_code == 413
    assert r.json()["request_id"] == r.headers["x-request-id"]

    # 502
    mock.chat.completions.create = AsyncMock(side_effect=SummarizerError("fail"))
    r = await client.post("/summarize", json={"text": "Hello."})
    assert r.status_code == 502
    assert r.json()["request_id"] == r.headers["x-request-id"]


async def test_input_text_never_logged(app_client, caplog) -> None:
    client, _ = app_client
    sentinel = "SENTINEL_XK92_PRIVATE"

    with caplog.at_level(logging.DEBUG, logger="summarizer_service"):
        response = await client.post("/summarize", json={"text": sentinel})

    for record in caplog.records:
        assert sentinel not in record.getMessage(), (
            f"Sentinel found in log record: {record.getMessage()}"
        )

    body_text = response.text
    assert sentinel not in body_text
