# Modified by Louis Rokitta
"""Base entity helpers for the Mistral integration."""

from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any, Callable, Iterable, Literal

from voluptuous_openapi import convert

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, llm
from homeassistant.helpers.entity import Entity

from .const import (
    CONF_CHAT_MODEL,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DEFAULT_NAME,
    LOGGER,
    MAX_TOOL_ITERATIONS,
    RECOMMENDED_CHAT_MODEL,
    RECOMMENDED_MAX_TOKENS,
    RECOMMENDED_TEMPERATURE,
    RECOMMENDED_TOP_P,
)
from .mistral_client import MistralClient


def _format_tool(tool: llm.Tool, serializer: Callable[[Any], Any] | None) -> dict:
    """Convert a Home Assistant tool definition to Mistral schema."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": convert(
                tool.parameters,
                custom_serializer=serializer or llm.selector_serializer,
            ),
        },
    }


def _message_content_to_text(content: str | list[dict] | None) -> str | None:
    """Flatten the response content into a printable string."""
    if content is None:
        return None
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
            continue
        if isinstance(item, dict):
            if (text := item.get("text")) is not None:
                parts.append(text)
            elif (raw := item.get("content")) is not None:
                parts.append(raw)
    return "\n".join(parts) if parts else None


def _convert_tool_calls(
    tool_calls: list[dict] | None,
) -> list[llm.ToolInput] | None:
    """Convert tool calls in a Mistral response to llm.ToolInput objects."""
    if not tool_calls:
        return None

    result: list[llm.ToolInput] = []
    for call in tool_calls:
        name = ""
        args: dict[str, Any] = {}
        call_id = call.get("id")
        if function := call.get("function"):
            name = function.get("name", "")
            arguments = function.get("arguments", "{}")
            try:
                args = json.loads(arguments)
            except (ValueError, JSONDecodeError):
                LOGGER.warning("Failed to parse tool args '%s'", arguments)
                args = {}
        if not call_id:
            call_id = llm.ToolInput(tool_name=name, tool_args={}).id
        result.append(llm.ToolInput(tool_name=name, tool_args=args, id=call_id))
    return result


def _convert_chat_content(content: conversation.Content) -> list[dict]:
    """Serialize chat log entries into the payload Mistral expects."""
    if isinstance(content, conversation.ToolResultContent):
        return [
            {
                "role": "tool",
                "tool_call_id": content.tool_call_id,
                "name": content.tool_name,
                "content": json.dumps(
                    content.tool_result, default=lambda obj: repr(obj)
                ),
            }
        ]

    if isinstance(content, conversation.AssistantContent):
        message: dict[str, Any] = {"role": "assistant"}
        if content.content:
            message["content"] = content.content
        if content.tool_calls:
            message["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.tool_name,
                        "arguments": json.dumps(tool_call.tool_args),
                    },
                }
                for tool_call in content.tool_calls
            ]
        return [message]

    if content.content:
        return [{"role": content.role, "content": content.content}]
    return []


def _build_messages(chat_content: Iterable[conversation.Content]) -> list[dict]:
    """Serialize the entire chat log."""
    messages: list[dict] = []
    for content in chat_content:
        messages.extend(_convert_chat_content(content))
    return messages


class MistralBaseLLMEntity(Entity):
    """Common functionality for Mistral entities."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entry: ConfigEntry, subentry: ConfigSubentry) -> None:
        self.entry = entry
        self.subentry = subentry
        self._attr_unique_id = subentry.subentry_id
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(entry.domain, subentry.subentry_id)},
            name=entry.title or DEFAULT_NAME,
            manufacturer="Mistral AI",
            model="Mistral Chat",
            entry_type=dr.DeviceEntryType.SERVICE,
        )

    @property
    def client(self) -> MistralClient:
        """Return the cached API client."""
        return self.entry.runtime_data

    def _options(self) -> dict[str, Any]:
        return self.subentry.data or {}

    async def _async_handle_chat_log(
        self,
        hass: HomeAssistant,
        chat_log: conversation.ChatLog,
        structure_prompt: str | None = None,
    ) -> conversation.AssistantContent:
        """Generate a new turn for the chat log."""
        options = self._options()
        tools: list[dict] = []

        if chat_log.llm_api and chat_log.llm_api.tools:
            tools = [
                _format_tool(tool, chat_log.llm_api.custom_serializer)
                for tool in chat_log.llm_api.tools
            ]

        messages = _build_messages(chat_log.content)
        if structure_prompt:
            messages.insert(
                0,
                {
                    "role": "system",
                    "content": structure_prompt,
                },
            )

        for _ in range(MAX_TOOL_ITERATIONS):
            payload = {
                "model": options.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL),
                "messages": messages,
                "max_tokens": options.get(CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS),
                "temperature": options.get(CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE),
                "top_p": options.get(CONF_TOP_P, RECOMMENDED_TOP_P),
                "stream": False,
            }
            if tools:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"
            try:
                response = await self.client.chat(payload)
            except Exception as err:
                LOGGER.error("Error talking to Mistral: %s", err)
                raise HomeAssistantError("Error talking to Mistral") from err

            if not response or "choices" not in response or not response["choices"]:
                raise HomeAssistantError("No response from Mistral API")

            message = response["choices"][0]["message"]
            assistant_tool_calls = _convert_tool_calls(message.get("tool_calls"))
            assistant_content = conversation.AssistantContent(
                agent_id=self.entity_id,
                content=_message_content_to_text(message.get("content")),
                tool_calls=assistant_tool_calls,
            )

            if assistant_tool_calls:
                tool_results = chat_log.async_add_assistant_content(assistant_content)
                async for _ in tool_results:
                    pass
                messages = _build_messages(chat_log.content)
                continue

            chat_log.async_add_assistant_content_without_tools(assistant_content)
            return assistant_content

        raise HomeAssistantError("Too many tool iterations without response")
