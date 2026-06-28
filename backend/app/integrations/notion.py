"""Notion adapter using httpx."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

NOTION_BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


class NotionAdapter:
    """Notion API adapter for logging cases, KPIs, and knowledge records."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.NOTION_API_KEY

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    @staticmethod
    def text_title(value: str) -> dict:
        """Build a Notion title property from a plain string."""
        return {"title": [{"text": {"content": value}}]}

    def create_page(
        self,
        database_id: str,
        properties: dict,
        children: list | None = None,
    ) -> dict | None:
        """Create a page in a Notion database. Returns the page object or None."""
        if not self.api_key:
            logger.warning("Notion create_page skipped (NOTION_API_KEY not configured)")
            return None

        payload: dict = {"parent": {"database_id": database_id}, "properties": properties}
        if children:
            payload["children"] = children

        try:
            response = httpx.post(
                f"{NOTION_BASE_URL}/pages",
                headers=self._headers(),
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            logger.info("Notion page created in database %s", database_id)
            return response.json()
        except Exception:
            logger.exception("Failed to create Notion page in database %s", database_id)
            return None

    def append_blocks(self, block_id: str, children: list) -> bool:
        """Append child blocks to a Notion block/page. Returns True on success."""
        if not self.api_key:
            logger.warning("Notion append_blocks skipped (NOTION_API_KEY not configured)")
            return False

        try:
            response = httpx.patch(
                f"{NOTION_BASE_URL}/blocks/{block_id}/children",
                headers=self._headers(),
                json={"children": children},
                timeout=10.0,
            )
            response.raise_for_status()
            logger.info("Appended %d block(s) to Notion block %s", len(children), block_id)
            return True
        except Exception:
            logger.exception("Failed to append blocks to Notion block %s", block_id)
            return False


notion_adapter = NotionAdapter()
