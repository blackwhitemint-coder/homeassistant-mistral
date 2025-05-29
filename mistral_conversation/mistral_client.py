"""Mistral API Python Client for Home Assistant Custom Integration."""

# Modified by Louis Rokitta

import httpx
import logging
from typing import Any, Dict, Optional

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

_LOGGER = logging.getLogger(__name__)

class MistralClient:
    def __init__(self, api_key: str, http_client: Optional[httpx.AsyncClient] = None):
        self.api_key = api_key
        self.http_client = http_client or httpx.AsyncClient()

    async def chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = await self.http_client.post(
                MISTRAL_API_URL, json=payload, headers=headers, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            _LOGGER.error("Mistral API HTTP error: %s | Response: %s", err, err.response.text if err.response else None)
            raise
        except Exception as err:
            _LOGGER.error("Mistral API error: %s", err, exc_info=True)
            raise
