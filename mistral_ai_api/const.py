# Modified by Louis Rokitta
"""Constants for the Mistral AI Conversation integration."""

from homeassistant.const import CONF_LLM_HASS_API
from homeassistant.helpers import llm
import logging

DOMAIN = "mistral_ai_api"
LOGGER: logging.Logger = logging.getLogger(__package__)

DEFAULT_CONVERSATION_NAME = "Mistral Conversation"
DEFAULT_AI_TASK_NAME = "Mistral AI Task"
DEFAULT_NAME = "Mistral Conversation"

CONF_CHAT_MODEL = "chat_model"
CONF_FILENAMES = "filenames"
CONF_MAX_TOKENS = "max_tokens"
CONF_PROMPT = "prompt"
CONF_REASONING_EFFORT = "reasoning_effort"
CONF_RECOMMENDED = "recommended"
CONF_TEMPERATURE = "temperature"
CONF_TOP_P = "top_p"

RECOMMENDED_CHAT_MODEL = "mistral-large-latest"
RECOMMENDED_MAX_TOKENS = 512
RECOMMENDED_REASONING_EFFORT = "medium"
RECOMMENDED_TEMPERATURE = 0.7
RECOMMENDED_TOP_P = 0.9
DEFAULT_SYSTEM_PROMPT = (
    "You are a Home Assistant smart home AI. Only respond with Home Assistant compatible commands."
)
MAX_TOOL_ITERATIONS = 10

UNSUPPORTED_MODELS: list[str] = []
WEB_SEARCH_MODELS: list[str] = []

RECOMMENDED_CONVERSATION_OPTIONS = {
    CONF_RECOMMENDED: True,
    CONF_LLM_HASS_API: [llm.LLM_API_ASSIST],
    CONF_PROMPT: llm.DEFAULT_INSTRUCTIONS_PROMPT,
}
RECOMMENDED_AI_TASK_OPTIONS = {
    CONF_RECOMMENDED: True,
}
