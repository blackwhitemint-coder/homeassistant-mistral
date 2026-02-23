# Modified by Louis Rokitta
"""Mistral API client helpers."""

from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
LOGGER = logging.getLogger(__name__)


class MistralClient:
    """Wrapper around Mistral's chat endpoint."""

    def __init__(self, api_key: str, http_client: httpx.AsyncClient) -> None:
        if not api_key:
            raise ValueError("API key required for Mistral client")
        if http_client is None:
            raise ValueError("HTTP client required for Mistral client")
        self.api_key = api_key
        self.http_client = http_client

    async def chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a chat payload to Mistral."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = await self.http_client.post(
                MISTRAL_API_URL,
                json=payload,
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            LOGGER.error(
                "Mistral API HTTP error: %s | Response: %s",
                err,
                err.response.text if err.response else None,
            )
            raise
        except Exception as err:
            LOGGER.error("Mistral API error: %s", err)
            raise
