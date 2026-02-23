# Modified by Louis Rokitta
"""Set up the Mistral AI integration."""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv, device_registry as dr, entity_registry as er, selector
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_FILENAMES,
    CONF_PROMPT,
    DEFAULT_AI_TASK_NAME,
    DEFAULT_NAME,
    DOMAIN,
    LOGGER,
    RECOMMENDED_AI_TASK_OPTIONS,
    RECOMMENDED_CONVERSATION_OPTIONS,
)
from .entity import MistralBaseLLMEntity, _build_messages
from .mistral_client import MistralClient

PLATFORMS = (Platform.CONVERSATION, Platform.AI_TASK)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Mistral services."""

    async def send_prompt(call: ServiceCall) -> ServiceResponse:
        entry_id = call.data["config_entry"]
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is None or entry.domain != DOMAIN:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_config_entry",
                translation_placeholders={"config_entry": entry_id},
            )

        conversation_subentry = next(
            (
                sub
                for sub in entry.subentries.values()
                if sub.subentry_type == "conversation"
            ),
            None,
        )
        if not conversation_subentry:
            raise ServiceValidationError("No conversation configuration found")

        client: MistralClient = entry.runtime_data
        messages = [
            {"role": "system", "content": conversation_subentry.data.get(CONF_PROMPT)},
            {"role": "user", "content": call.data[CONF_PROMPT]},
        ]

        if filenames := call.data.get(CONF_FILENAMES):
            for filename in filenames:
                if not hass.config.is_allowed_path(filename):
                    raise HomeAssistantError(
                        f"Cannot read `{filename}`; adjust allowlist_external_dirs"
                    )
                messages.append(
                    {
                        "role": "user",
                        "content": Path(filename).read_text(),
                    }
                )

        response = await client.chat(
            {
                "model": conversation_subentry.data.get(
                    "chat_model", "mistral-large-latest"
                ),
                "messages": messages,
                "stream": False,
            }
        )
        return {"text": response["choices"][0]["message"]["content"]}

    hass.services.async_register(
        DOMAIN,
        "generate_content",
        send_prompt,
        schema=vol.Schema(
            {
                vol.Required("config_entry"): selector.ConfigEntrySelector(
                    {
                        "integration": DOMAIN,
                    }
                ),
                vol.Required(CONF_PROMPT): cv.string,
                vol.Optional(CONF_FILENAMES, default=[]): vol.All(
                    cv.ensure_list, [cv.string]
                ),
            }
        ),
        supports_response=SupportsResponse.ONLY,
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    api_key = entry.data[CONF_API_KEY]
    client = MistralClient(api_key, get_async_client(hass))
    entry.runtime_data = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
