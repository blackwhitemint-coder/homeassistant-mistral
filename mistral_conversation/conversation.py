# Modified by Louis Rokitta
from collections.abc import AsyncGenerator, Callable
import json
from typing import Any, Literal, cast

from homeassistant.components import assist_pipeline, conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LLM_HASS_API, MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, intent, llm
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MistralClient
from .const import (
    CONF_CHAT_MODEL,
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
)

MAX_TOOL_ITERATIONS = 3

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    agent = MistralConversationEntity(config_entry)
    async_add_entities([agent])


def _convert_content_to_param(content: conversation.Content) -> list[dict]:
    messages = []
    if content.content:
        role = content.role
        if role == "system":
            role = "system"
        elif role == "user":
            role = "user"
        elif role == "assistant":
            role = "assistant"
        else:
            role = "user"
        messages.append({"role": role, "content": content.content})
    return messages


class MistralConversationEntity(
    conversation.ConversationEntity, conversation.AbstractConversationAgent
):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_supports_streaming = False

    def __init__(self, entry: ConfigEntry) -> None:
        self.entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Mistral AI",
            model="Mistral Chat",
            entry_type=dr.DeviceEntryType.SERVICE,
        )
        if self.entry.options.get(CONF_LLM_HASS_API):
            self._attr_supported_features = (
                conversation.ConversationEntityFeature.CONTROL
            )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return MATCH_ALL

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        assist_pipeline.async_migrate_engine(
            self.hass, "conversation", self.entry.entry_id, self.entity_id
        )
        conversation.async_set_agent(self.hass, self.entry, self)
        self.entry.async_on_unload(
            self.entry.add_update_listener(self._async_entry_update_listener)
        )

    async def async_will_remove_from_hass(self) -> None:
        conversation.async_unset_agent(self.hass, self.entry)
        await super().async_will_remove_from_hass()

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        options = self.entry.options
        try:
            await chat_log.async_update_llm_data(
                DOMAIN,
                user_input,
                options.get(CONF_LLM_HASS_API),
                options.get(CONF_PROMPT),
            )
        except conversation.ConverseError as err:
            return err.as_conversation_result()
        await self._async_handle_chat_log(chat_log)
        intent_response = intent.IntentResponse(language=user_input.language)
        last_assistant = None
        for c in reversed(chat_log.content):
            if isinstance(c, conversation.AssistantContent):
                last_assistant = c
                break
        if last_assistant is not None:
            intent_response.async_set_speech(last_assistant.content or "")
        else:
            intent_response.async_set_speech("")
        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=chat_log.conversation_id,
            continue_conversation=chat_log.continue_conversation,
        )

    async def _async_handle_chat_log(self, chat_log: conversation.ChatLog) -> None:
        options = self.entry.options
        model = options.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL)
        messages = [
            {"role": "system", "content": "You are a Home Assistant smart home AI. Only respond with Home Assistant compatible commands."}
        ]
        for content in chat_log.content:
            messages.extend(_convert_content_to_param(content))
        client = self.entry.runtime_data
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": options.get(CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS),
            "temperature": options.get(CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE),
            "top_p": options.get(CONF_TOP_P, RECOMMENDED_TOP_P),
            "stream": False,
        }
        try:
            response = await client.chat(payload)
        except Exception as err:
            raise HomeAssistantError("Error talking to Mistral") from err
        if not response or "choices" not in response or not response["choices"]:
            raise HomeAssistantError("No response from Mistral API")
        content = response["choices"][0]["message"]["content"]
        chat_log.async_add_assistant_content(
            conversation.AssistantContent(content=content, agent_id=self.entity_id)
        )

    async def _async_entry_update_listener(
        self, hass: HomeAssistant, entry: ConfigEntry
    ) -> None:
        await hass.config_entries.async_reload(entry.entry_id)
