# Modified by Louis Rokitta
"""Config flow for Mistral AI Conversation integration."""

from __future__ import annotations
from collections.abc import Mapping
import logging
from types import MappingProxyType
from typing import Any
import voluptuous as vol
from voluptuous_openapi import convert
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_API_KEY,
    CONF_LLM_HASS_API,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TemplateSelector,
)
from homeassistant.helpers.typing import VolDictType
from .mistral_client import MistralClient
from .const import (
    CONF_CHAT_MODEL,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_REASONING_EFFORT,
    CONF_RECOMMENDED,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DOMAIN,
    RECOMMENDED_CHAT_MODEL,
    RECOMMENDED_MAX_TOKENS,
    RECOMMENDED_REASONING_EFFORT,
    RECOMMENDED_TEMPERATURE,
    RECOMMENDED_TOP_P,
    UNSUPPORTED_MODELS,
    WEB_SEARCH_MODELS,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})
RECOMMENDED_OPTIONS = {
    CONF_RECOMMENDED: True,
    CONF_LLM_HASS_API: llm.LLM_API_ASSIST,
    CONF_PROMPT: llm.DEFAULT_INSTRUCTIONS_PROMPT,
}

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate the user input allows us to connect to Mistral."""
    client = MistralClient(data[CONF_API_KEY])
    # Mistral does not have a models endpoint, so we do a dummy chat call
    payload = {
        "model": RECOMMENDED_CHAT_MODEL,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
        "stream": False,
    }
    await client.chat(payload)

class MistralConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mistral AI Conversation."""
    VERSION = 1
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)
        errors: dict[str, str] = {}
        try:
            await validate_input(self.hass, user_input)
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "cannot_connect"
        else:
            return self.async_create_entry(
                title="Mistral AI",
                data=user_input,
                options=RECOMMENDED_OPTIONS,
            )
        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)
    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return MistralOptionsFlow(config_entry)

class MistralOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self.last_rendered_recommended = config_entry.options.get(CONF_RECOMMENDED, False)
        self.config_entry = config_entry
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        options: dict[str, Any] | MappingProxyType[str, Any] = self.config_entry.options
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input[CONF_RECOMMENDED] == self.last_rendered_recommended:
                if not user_input.get(CONF_LLM_HASS_API):
                    user_input.pop(CONF_LLM_HASS_API, None)
                if user_input.get(CONF_CHAT_MODEL) in UNSUPPORTED_MODELS:
                    errors[CONF_CHAT_MODEL] = "model_not_supported"
                if not errors:
                    return self.async_create_entry(title="", data=user_input)
            else:
                self.last_rendered_recommended = user_input[CONF_RECOMMENDED]
                options = {
                    CONF_RECOMMENDED: user_input[CONF_RECOMMENDED],
                    CONF_PROMPT: user_input.get(CONF_PROMPT, llm.DEFAULT_INSTRUCTIONS_PROMPT),
                    CONF_LLM_HASS_API: user_input.get(CONF_LLM_HASS_API),
                }
        schema = mistral_config_option_schema(self.hass, options)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
            errors=errors,
        )

def mistral_config_option_schema(hass: HomeAssistant, options: Mapping[str, Any]) -> VolDictType:
    hass_apis: list[SelectOptionDict] = [
        SelectOptionDict(label=api.name, value=api.id) for api in llm.async_get_apis(hass)
    ]
    if (suggested_llm_apis := options.get(CONF_LLM_HASS_API)) and isinstance(suggested_llm_apis, str):
        suggested_llm_apis = [suggested_llm_apis]
    schema: VolDictType = {
        vol.Optional(
            CONF_PROMPT,
            description={"suggested_value": options.get(CONF_PROMPT, llm.DEFAULT_INSTRUCTIONS_PROMPT)},
        ): TemplateSelector(),
        vol.Optional(
            CONF_LLM_HASS_API,
            description={"suggested_value": suggested_llm_apis},
        ): SelectSelector(SelectSelectorConfig(options=hass_apis, multiple=True)),
        vol.Required(CONF_RECOMMENDED, default=options.get(CONF_RECOMMENDED, False)): bool,
    }
    if options.get(CONF_RECOMMENDED):
        return schema
    schema.update({
        vol.Optional(
            CONF_CHAT_MODEL,
            description={"suggested_value": options.get(CONF_CHAT_MODEL)},
            default=RECOMMENDED_CHAT_MODEL,
        ): str,
        vol.Optional(
            CONF_MAX_TOKENS,
            description={"suggested_value": options.get(CONF_MAX_TOKENS)},
            default=RECOMMENDED_MAX_TOKENS,
        ): int,
        vol.Optional(
            CONF_TOP_P,
            description={"suggested_value": options.get(CONF_TOP_P)},
            default=RECOMMENDED_TOP_P,
        ): NumberSelector(NumberSelectorConfig(min=0, max=1, step=0.05)),
        vol.Optional(
            CONF_TEMPERATURE,
            description={"suggested_value": options.get(CONF_TEMPERATURE)},
            default=RECOMMENDED_TEMPERATURE,
        ): NumberSelector(NumberSelectorConfig(min=0, max=2, step=0.05)),
        vol.Optional(
            CONF_REASONING_EFFORT,
            description={"suggested_value": options.get(CONF_REASONING_EFFORT)},
            default=RECOMMENDED_REASONING_EFFORT,
        ): SelectSelector(
            SelectSelectorConfig(
                options=["low", "medium", "high"],
                translation_key=CONF_REASONING_EFFORT,
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
    })
    return schema
