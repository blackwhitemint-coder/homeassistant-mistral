# Modified by Louis Rokitta
"""Constants for the Mistral AI Conversation integration."""

import logging

DOMAIN = "mistral_ai_api"
LOGGER: logging.Logger = logging.getLogger(__package__)

CONF_CHAT_MODEL = "chat_model"
CONF_FILENAMES = "filenames"
CONF_MAX_TOKENS = "max_tokens"
CONF_PROMPT = "prompt"
CONF_REASONING_EFFORT = "reasoning_effort"
CONF_RECOMMENDED = "recommended"
CONF_TEMPERATURE = "temperature"
CONF_TOP_P = "top_p"

RECOMMENDED_CHAT_MODEL = "mistral-medium"
RECOMMENDED_MAX_TOKENS = 150
RECOMMENDED_REASONING_EFFORT = "low"
RECOMMENDED_TEMPERATURE = 1.0
RECOMMENDED_TOP_P = 1.0

# Mistral unterstützt keine Websuche, daher deaktiviert
CONF_WEB_SEARCH = "web_search"
CONF_WEB_SEARCH_USER_LOCATION = "user_location"
CONF_WEB_SEARCH_CONTEXT_SIZE = "search_context_size"
CONF_WEB_SEARCH_CITY = "city"
CONF_WEB_SEARCH_REGION = "region"
CONF_WEB_SEARCH_COUNTRY = "country"
CONF_WEB_SEARCH_TIMEZONE = "timezone"
RECOMMENDED_WEB_SEARCH = False
RECOMMENDED_WEB_SEARCH_CONTEXT_SIZE = "medium"
RECOMMENDED_WEB_SEARCH_USER_LOCATION = False

UNSUPPORTED_MODELS: list[str] = [
    # Hier ggf. Mistral-spezifische Modelle ergänzen, falls welche nicht unterstützt werden
]

WEB_SEARCH_MODELS: list[str] = [
    # Mistral unterstützt keine Websuche, daher leer lassen
]
