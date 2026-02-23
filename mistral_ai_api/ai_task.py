# Modified by Louis Rokitta
"""AI Task platform support for Mistral."""

from __future__ import annotations

import json
from json import JSONDecodeError

from voluptuous_openapi import convert

from homeassistant.components import ai_task, conversation
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers import llm

from .entity import MistralBaseLLMEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up AI Task entities for each configured subentry."""
    for subentry in config_entry.subentries.values():
        if subentry.subentry_type != "ai_task_data":
            continue

        async_add_entities(
            [MistralAITaskEntity(config_entry, subentry)],
            config_subentry_id=subentry.subentry_id,
        )


class MistralAITaskEntity(ai_task.AITaskEntity, MistralBaseLLMEntity):
    """AI Task entity backed by the Mistral API."""

    _attr_supported_features = ai_task.AITaskEntityFeature.GENERATE_DATA

    async def _async_generate_data(
        self,
        task: ai_task.GenDataTask,
        chat_log: conversation.ChatLog,
    ) -> ai_task.GenDataTaskResult:
        """Handle a structured data task."""
        structure_prompt: str | None = None
        if task.structure is not None:
            schema_dict = convert(
                task.structure,
                custom_serializer=llm.selector_serializer,
            )
            structure_prompt = (
                "Return your final answer strictly as JSON matching this schema:\n"
                f"{json.dumps(schema_dict, indent=2)}"
            )

        await self._async_handle_chat_log(self.hass, chat_log, structure_prompt)

        last_assistant = next(
            (
                content
                for content in reversed(chat_log.content)
                if isinstance(content, conversation.AssistantContent)
            ),
            None,
        )
        if not last_assistant:
            raise HomeAssistantError("LLM did not return a response")

        text = last_assistant.content or ""
        if not task.structure:
            return ai_task.GenDataTaskResult(
                conversation_id=chat_log.conversation_id,
                data=text,
            )

        try:
            data = json.loads(text)
        except JSONDecodeError as err:
            raise HomeAssistantError("Structured response was not valid JSON") from err

        return ai_task.GenDataTaskResult(
            conversation_id=chat_log.conversation_id,
            data=data,
        )

    async def _async_generate_image(
        self,
        task: ai_task.GenImageTask,
        chat_log: conversation.ChatLog,
    ) -> ai_task.GenImageTaskResult:
        """Mistral does not support image generation."""
        raise HomeAssistantError("Mistral API does not support image generation")
