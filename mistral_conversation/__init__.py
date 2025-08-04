"""The Mistral AI Conversation integration."""

# Modified by Louis Rokitta

from __future__ import annotations
import base64
from mimetypes import guess_type
from pathlib import Path
from .mistral_client import MistralClient

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import (
    ConfigEntryNotReady,
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers import config_validation as cv, selector
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_CHAT_MODEL,
    CONF_FILENAMES,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_REASONING_EFFORT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DOMAIN,
    LOGGER,
    RECOMMENDED_CHAT_MODEL,
    RECOMMENDED_MAX_TOKENS,
    RECOMMENDED_REASONING_EFFORT,
    RECOMMENDED_TEMPERATURE,
    RECOMMENDED_TOP_P,
    DEFAULT_SYSTEM_PROMPT,
)

SERVICE_GENERATE_IMAGE = "generate_image"
SERVICE_GENERATE_CONTENT = "generate_content"

PLATFORMS = (Platform.CONVERSATION,)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def encode_file(file_path: str) -> tuple[str, str]:
    """Return base64 version of file contents."""
    mime_type, _ = guess_type(file_path)
    if (mime_type is None):
        mime_type = "application/octet-stream"
    with open(file_path, "rb") as image_file:
        return (mime_type, base64.b64encode(image_file.read()).decode("utf-8"))


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Mistral AI Conversation."""

    async def render_image(call: ServiceCall) -> ServiceResponse:
        """Render an image with Mistral (not supported, placeholder)."""
        raise HomeAssistantError("Mistral API does not support image generation.")

    async def send_prompt(call: ServiceCall) -> ServiceResponse:
        """Send a prompt to Mistral and return the response."""
        entry_id = call.data["config_entry"]
        entry = hass.config_entries.async_get_entry(entry_id)

        if (entry is None or entry.domain != DOMAIN):
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_config_entry",
                translation_placeholders={"config_entry": entry_id},
            )

        model: str = entry.options.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL)
        api_key: str = entry.data.get(CONF_API_KEY)
        client = MistralClient(api_key, get_async_client(hass))

        user_prompt = call.data[CONF_PROMPT]
        system_prompt = entry.options.get(CONF_PROMPT, DEFAULT_SYSTEM_PROMPT)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": entry.options.get(CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS),
            "temperature": entry.options.get(CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE),
            "top_p": entry.options.get(CONF_TOP_P, RECOMMENDED_TOP_P),
            "stream": False,
        }
        try:
            response = await client.chat(payload)
        except Exception as err:
            raise HomeAssistantError(f"Error generating content: {err}") from err
        if not response or "choices" not in response or not response["choices"]:
            raise HomeAssistantError("No response from Mistral API")
        return {"text": response["choices"][0]["message"]["content"]}

    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_CONTENT,
        send_prompt,
        schema=vol.Schema(
            {
                vol.Required("config_entry"): selector.ConfigEntrySelector(
                    {"integration": DOMAIN}
                ),
                vol.Required(CONF_PROMPT): cv.string,
                vol.Optional(CONF_FILENAMES, default=[]): vol.All(cv.ensure_list, [cv.string]),
            }
        ),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_IMAGE,
        render_image,
        schema=vol.Schema(
            {
                vol.Required("config_entry"): selector.ConfigEntrySelector(
                    {"integration": DOMAIN}
                ),
                vol.Required(CONF_PROMPT): cv.string,
                vol.Optional("size", default="1024x1024"): vol.In(("1024x1024", "1024x1792", "1792x1024")),
                vol.Optional("quality", default="standard"): vol.In(("standard", "hd")),
                vol.Optional("style", default="vivid"): vol.In(("vivid", "natural")),
            }
        ),
        supports_response=SupportsResponse.ONLY,
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mistral AI Conversation from a config entry."""
    api_key = entry.data.get(CONF_API_KEY)
    entry.runtime_data = MistralClient(api_key, get_async_client(hass))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Mistral AI."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
