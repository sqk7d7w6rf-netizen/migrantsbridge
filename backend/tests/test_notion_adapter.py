"""Tests for the Notion integration adapter."""

from __future__ import annotations

from app.integrations.notion import NOTION_BASE_URL, NOTION_VERSION, NotionAdapter


class _FakeResponse:
    def __init__(self, json_data: dict, status_code: int = 200) -> None:
        self._json = json_data
        self.status_code = status_code

    def json(self) -> dict:
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_text_title_helper():
    assert NotionAdapter.text_title("Case 42") == {
        "title": [{"text": {"content": "Case 42"}}]
    }


def test_create_page_builds_correct_request(monkeypatch):
    captured: dict = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _FakeResponse({"id": "page-123"})

    monkeypatch.setattr("app.integrations.notion.httpx.post", fake_post)

    adapter = NotionAdapter(api_key="secret_token")
    result = adapter.create_page(
        database_id="db-1",
        properties={"Name": NotionAdapter.text_title("Hello")},
        children=[{"type": "paragraph"}],
    )

    assert result == {"id": "page-123"}
    assert captured["url"] == f"{NOTION_BASE_URL}/pages"
    assert captured["headers"]["Authorization"] == "Bearer secret_token"
    assert captured["headers"]["Notion-Version"] == NOTION_VERSION
    assert captured["json"]["parent"] == {"database_id": "db-1"}
    assert captured["json"]["properties"]["Name"]["title"][0]["text"]["content"] == "Hello"
    assert captured["json"]["children"] == [{"type": "paragraph"}]


def test_create_page_unconfigured_is_noop(monkeypatch):
    def fail_post(*args, **kwargs):  # pragma: no cover - should never be called
        raise AssertionError("httpx.post should not be called when unconfigured")

    monkeypatch.setattr("app.integrations.notion.httpx.post", fail_post)

    adapter = NotionAdapter(api_key="")
    assert adapter.create_page(database_id="db-1", properties={}) is None


def test_append_blocks_builds_correct_request(monkeypatch):
    captured: dict = {}

    def fake_patch(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        return _FakeResponse({"results": []})

    monkeypatch.setattr("app.integrations.notion.httpx.patch", fake_patch)

    adapter = NotionAdapter(api_key="secret_token")
    assert adapter.append_blocks("block-1", [{"type": "paragraph"}]) is True
    assert captured["url"] == f"{NOTION_BASE_URL}/blocks/block-1/children"
    assert captured["json"]["children"] == [{"type": "paragraph"}]


def test_append_blocks_unconfigured_is_noop(monkeypatch):
    def fail_patch(*args, **kwargs):  # pragma: no cover - should never be called
        raise AssertionError("httpx.patch should not be called when unconfigured")

    monkeypatch.setattr("app.integrations.notion.httpx.patch", fail_patch)

    adapter = NotionAdapter(api_key="")
    assert adapter.append_blocks("block-1", []) is False
