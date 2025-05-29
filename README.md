````markdown name=README.md
# Mistral AI Home Assistant Integration

---

## 🇩🇪 Deutsch

### Überblick

Diese Home Assistant Custom Integration ermöglicht die Nutzung von Mistral AI als KI-Backend für smarte Automatisierungen, Sprachsteuerung oder Chatbots im Smart Home.  
**Sie verwendet die offizielle OpenAI-Integration als Basis und wurde entsprechend angepasst, um mit der Mistral API zu funktionieren.**

### Features

- Nutzt die [Mistral Chat API](https://docs.mistral.ai/api/) für KI-gestützte Antworten und Steuerbefehle
- Kompatibel mit Home Assistant Sensoren, Aktoren und Konversationen
- System-Prompt für smarthome-spezifische Kommandos
- Speicherung von Konversationen (optional)
- Anpassbar an eigene Anwendungsfälle und Modelle

### Voraussetzungen

- Home Assistant (getestet ab 2024.5)
- Mistral AI API Key ([hier beantragen](https://console.mistral.ai/))
- Grundkenntnisse in YAML und Home Assistant Custom Integrations

### Installation

1. **Repo klonen oder als ZIP herunterladen**
2. Den Ordner `custom_components/mistral_ai_api` im Home Assistant `config`-Verzeichnis anlegen
3. Dateien aus diesem Repository in diesen Ordner kopieren
4. Home Assistant neu starten

### Konfiguration

Füge in deine `configuration.yaml` (oder via UI):

```yaml
mistral_ai_api:
  api_key: !secret mistral_api_key
  model: mistral-medium
  exposed_entities:
    - light.wohnzimmer
    - climate.schlafzimmer
    - ...
```

- **api_key:** Dein Mistral API Key
- **model:** Gewünschtes Modell (z.B. `mistral-medium`, `mistral-large`)
- **exposed_entities:** Liste der steuerbaren Home Assistant Entities

### Nutzung

- Die Integration stellt einen Sensor bereit, der letzte Prompts/Antworten anzeigen kann
- Automationen/Skripte können via Service-Aufruf den KI-Chat triggern
- Die KI antwortet im Home Assistant-Kommandoformat und kann direkt Aktionen auslösen

### Hinweise

- Die Integration befindet sich im Beta-Status
- Vorschläge, Bugreports und Pull Requests sind willkommen!
- **Technischer Hinweis:** Die Integration basiert auf der offiziellen OpenAI-Integration von Home Assistant und wurde angepasst, um mit den APIs und Modellen von Mistral AI kompatibel zu sein.

### Lizenz

MIT License

---

## 🇬🇧 English

### Overview

This Home Assistant custom integration allows you to use Mistral AI as a smart home AI backend for automations, voice control, or chatbots.  
**It uses the official OpenAI integration as a base and has been modified to work with the Mistral API.**

### Features

- Uses the [Mistral Chat API](https://docs.mistral.ai/api/) for AI-powered responses and smart home commands
- Compatible with Home Assistant sensors, actuators, and conversations
- System prompt for smart home-specific commands
- Conversation storage (optional)
- Customizable for your own use cases and models

### Requirements

- Home Assistant (tested from 2024.5)
- Mistral AI API key ([get one here](https://console.mistral.ai/))
- Basic knowledge of YAML and Home Assistant custom integrations

### Installation

1. **Clone this repo or download as ZIP**
2. Create the folder `custom_components/mistral_ai_api` in your Home Assistant `config` directory
3. Copy all files from this repository into that folder
4. Restart Home Assistant

### Configuration

Add to your `configuration.yaml` (or via UI):

```yaml
mistral_ai_api:
  api_key: !secret mistral_api_key
  model: mistral-medium
  exposed_entities:
    - light.living_room
    - climate.bedroom
    - ...
```

- **api_key:** Your Mistral API key
- **model:** Desired model (e.g. `mistral-medium`, `mistral-large`)
- **exposed_entities:** List of Home Assistant entities to be controlled

### Usage

- The integration provides a sensor showing the last prompts/responses
- Automations/scripts can trigger the AI chat via service call
- The AI replies in Home Assistant command format and can directly trigger actions

### Notes

- The integration is in beta status
- Suggestions, bug reports and pull requests are welcome!
- **Technical note:** The integration is based on the official Home Assistant OpenAI integration and was adapted to be compatible with Mistral AI's APIs and models.

### License

MIT License

---

**Links / Links:**
- [Mistral AI API Docs](https://docs.mistral.ai/api/)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
````