---
name: xiaoai-cloud
description: Control Xiaomi XiaoAi speakers via Hermes Agent — voice interception, TTS playback, volume control, and remote wake-up
version: 2.0.0
author: Hermes Adaptation
tags: [smart-home, xiaomi, xiaoai, speaker, voice, tts]
---

# XiaoAI Cloud Plugin for Hermes

Control Xiaomi XiaoAi smart speakers from Hermes Agent. Intercepts voice queries, forwards them to an LLM, and plays responses back on the speaker.

## Features

- Voice interception & forwarding (intercept XiaoAi's voice, forward to LLM)
- Remote speaker wake-up and TTS playback
- Volume, wake word, and context memory control
- Embedded web console for login, device switching, and conversation control
- Audio reply handling

## Prerequisites

- Node.js 22+
- Xiaomi account with XiaoAi speaker
- LLM API endpoint (OpenAI-compatible)

## Installation

```bash
cd /root/Xiaoai-Claw-Addon
npm install
npm run build
```

## Configuration

Create `~/.hermes/xiaoai-cloud/config.json`:

```json
{
  "account": "your-xiaomi-account",
  "serverCountry": "cn",
  "speakerName": "Living Room Speaker",
  "llmApiUrl": "https://api.openai.com",
  "llmApiKey": "sk-...",
  "llmModel": "gpt-4o-mini",
  "notificationWebhookUrl": "http://localhost:8787/webhooks/xiaoai",
  "wakeWordPattern": "小虾|小瞎|小侠",
  "dialogWindowSeconds": 30,
  "pollIntervalMs": 320
}
```

## Running

```bash
# Start directly
npm start

# Or with environment variables
XIAOAI_PORT=17890 LLM_API_URL=https://api.openai.com LLM_API_KEY=sk-... npm start
```

## HTTP API

The service exposes these endpoints on port 17890 (configurable):

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /api/xiaoai/tools | List available tools |
| POST | /api/xiaoai/speak | Make speaker say text |
| POST | /api/xiaoai/play-audio | Play audio URL on speaker |
| POST | /api/xiaoai/set-volume | Set speaker volume |
| GET | /api/xiaoai/get-volume | Get current volume |
| POST | /api/xiaoai/new-session | Reset voice context |
| POST | /api/xiaoai/wake-up | Remote wake speaker |
| POST | /api/xiaoai/execute | Send command to speaker |
| POST | /api/xiaoai/set-mode | Switch intercept mode |
| GET | /api/xiaoai/status | Full plugin status |
| POST | /api/xiaoai/login-begin | Start Xiaomi login |
| GET | /api/xiaoai/login-status | Check login status |
| GET | /console | Web console |

## Systemd Service

```bash
sudo cp xiaoai-cloud.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now xiaoai-cloud
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| XIAOAI_PORT | 17890 | HTTP server port |
| XIAOAI_HOST | 0.0.0.0 | HTTP server bind address |
| LLM_API_URL | (required) | OpenAI-compatible API endpoint |
| LLM_API_KEY | (optional) | API key for LLM |
| LLM_MODEL | gpt-4o-mini | Model to use |
| HERMES_HOME | ~/.hermes | Hermes home directory |

## Troubleshooting

1. **Speaker not found**: Login via console at http://localhost:17890/console
2. **Voice not intercepted**: Check wake word pattern and mode (wake/proxy/silent)
3. **LLM not responding**: Verify LLM_API_URL and LLM_API_KEY
4. **Port conflict**: Change XIAOAI_PORT environment variable
