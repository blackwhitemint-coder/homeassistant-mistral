# Mistral AI für Home Assistant

---

## 🇩🇪 Deutsch

### Was ist das?

Mit dieser Custom Component kannst du Mistral AI direkt in Home Assistant nutzen. Die Integration ist ein Umbau der offiziellen OpenAI-Integration.

### Was kann die Integration?

- Nutzt die [Mistral Chat API](https://docs.mistral.ai/api/) für Antworten und Steuerbefehle
- Funktioniert mit Home Assistant Conversation (also Sprachsteuerung, Chat, Automationen)
- Du kannst das Mistral-Modell direkt in der UI auswählen (z.B. `mistral-medium`, `mistral-large`)
- System-Prompt sorgt dafür, dass die KI sich auf Smart-Home-Kommandos konzentriert
- Konversationen werden gespeichert (wenn du willst)
- Keine Bildgenerierung

### Was brauchst du?

- Home Assistant (ab Version 2024.5 getestet)
- Einen Mistral API Key ([hier bekommst du einen](https://console.mistral.ai/))

### Installation

1. Lade dieses Repository herunter (oder klone es)
2. Lege den Ordner `custom_components/mistral_ai_api` in deinem Home Assistant `config`-Verzeichnis an
3. Kopiere alle Dateien aus diesem Repo in diesen Ordner
4. Starte Home Assistant neu

### Einrichtung

- Füge die Integration über die Home Assistant UI hinzu ("Integration hinzufügen" > "Mistral AI Conversation")
- Gib deinen API Key ein
- Wähle das Modell und weitere Optionen in den Einstellungen der Integration

#### Modellwahl in der UI

Im Optionsmenü kannst du das gewünschte Mistral-Modell auswählen (z.B. `mistral-medium`, `mistral-large`).

#### Beispiel: Automation mit Live-Daten

```yaml
- alias: "Frage Mistral nach Temperatur"
  trigger:
    - platform: state
      entity_id: sensor.wohnzimmer_temperature
  action:
    - service: conversation.process
      data:
        agent_id: "conversation.mistral_ai_api"
        text: >
          Die aktuelle Temperatur im Wohnzimmer beträgt {{ states('sensor.wohnzimmer_temperature') }} °C. Was soll ich tun?
```

### Noch wichtig

- Die Integration ist stabil, aber Rückmeldungen sind immer willkommen!
- Bildgenerierung ist nicht möglich.
- Funktion-Calling, Tool-Calls und Websuche sind mit Mistral sind leider auch noch nicht möglich.
- **Technischer Hinweis:** Diese Komponente basiert auf der offiziellen OpenAI-Conversation-Integration, ist aber komplett auf Mistral umgebaut.

### Lizenz

Apache License 2.0

Teile dieses Codes basieren auf der offiziellen Home Assistant OpenAI-Integration (Apache License 2.0).

---

## 🇬🇧 English

### What is this?

This custom component lets you use Mistral AI in Home Assistant – for voice control, chatbots, or smart automations. It's a full rewrite of the official OpenAI integration, but everything runs on the Mistral API now.

### What does it do?

- Uses the [Mistral Chat API](https://docs.mistral.ai/api/) for smart replies and home control
- Works with Home Assistant Conversation (voice, chat, automations)
- You can pick the Mistral model right in the UI (e.g. `mistral-medium`, `mistral-large`)
- System prompt keeps the AI focused on smart home commands
- Conversation history is saved (if you want)
- No image generation (Mistral doesn't support it yet)

### What do you need?

- Home Assistant (tested from version 2024.5)
- A Mistral API key ([get one here](https://console.mistral.ai/))

### Installation

1. Download this repo (or clone it)
2. Create the folder `custom_components/mistral_ai_api` in your Home Assistant `config` directory
3. Copy all files from this repo into that folder
4. Restart Home Assistant

### Setup

- Add the integration via the Home Assistant UI ("Add Integration" > "Mistral AI Conversation")
- Enter your API key
- Pick your model and other options in the integration settings

#### Model selection in the UI

You can select your preferred Mistral model (e.g. `mistral-medium`, `mistral-large`) in the options menu.

#### Example: Automation with live data

```yaml
- alias: "Ask Mistral for temperature"
  trigger:
    - platform: state
      entity_id: sensor.living_room_temperature
  action:
    - service: conversation.process
      data:
        agent_id: "conversation.mistral_ai_api"
        text: >
          The current temperature in the living room is {{ states('sensor.living_room_temperature') }} °C. What should I do?
```

### Good to know

- The integration is stable, but feedback is always welcome!
- Image generation is not possible.
- Function calling, tool calls, and web search are unfortunately not possible yet.
- **Technical note:** This component is based on the official OpenAI Conversation integration, but fully rebuilt for Mistral.

### License

Apache License 2.0

Parts of this code are based on the official Home Assistant OpenAI integration (Apache License 2.0).

---

**Links:**
- [Mistral AI API Docs](https://docs.mistral.ai/api/)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Offizielle Home Assistant OpenAI-Integration (GitHub)](https://github.com/home-assistant/core/tree/dev/homeassistant/components/openai_conversation)
