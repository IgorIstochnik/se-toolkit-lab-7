# Bot Development Plan

## Overview

This document describes the plan for building the LMS Telegram bot across four tasks. The bot integrates with the LMS backend API to provide students with access to their lab progress, scores, and analytics via Telegram. It uses an LLM for natural language intent routing in Task 3.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Entry point** (`bot.py`) — Handles CLI arguments, test mode, and Telegram client initialization
2. **Handlers** (`handlers/`) — Pure functions that process commands and return text responses
3. **Services** (`services/`) — External API clients (LMS backend, LLM)
4. **Configuration** (`config.py`) — Environment variable loading with pydantic-settings

The key design principle is **testable handlers**: handler functions have no dependency on Telegram. They can be called from `--test` mode, unit tests, or the Telegram bot client. This makes testing and debugging much easier.

## Task 1: Plan and Scaffold (Current)

**Goal:** Create project structure and development plan.

**Deliverables:**
- `bot/pyproject.toml` — Bot dependencies (aiogram, httpx, pydantic)
- `bot/bot.py` — Entry point with `--test` mode
- `bot/handlers/` — Handler module with placeholder functions
- `bot/config.py` — Configuration loading
- `bot/PLAN.md` — This document
- `.env.bot.example` — Example environment file

**Test mode:** `uv run bot.py --test "/start"` prints response to stdout without connecting to Telegram.

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

**Approach:**
1. Create `bot/services/lms_api.py` — HTTP client for the backend API
2. Implement Bearer token authentication using `LMS_API_KEY`
3. Update handlers to call the API:
   - `/health` → `GET /` health endpoint
   - `/labs` → `GET /items/` to list labs
   - `/scores <lab>` → `GET /interactions/` filtered by lab
4. Handle errors gracefully (network failures, auth errors, rate limits)

**Key pattern:** The service layer abstracts HTTP details. Handlers call `await lms_api.get_labs()` not `httpx.get()`.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Allow users to ask questions in plain English instead of slash commands.

**Approach:**
1. Create `bot/services/llm_client.py` — LLM API client
2. Define tool descriptions for the LLM:
   - `get_labs()` — List available labs
   - `get_scores(lab_id)` — Get scores for a lab
   - `get_health()` — Check backend status
3. When a message doesn't start with `/`, send it to the LLM with tool descriptions
4. The LLM decides which tool to call based on user intent
5. Execute the tool and return the result

**Critical insight:** The LLM routes based on tool descriptions, not regex or keyword matching. If the LLM picks the wrong tool, improve the description — don't add code-based routing.

**Example flow:**
```
User: "what labs are available?"
→ LLM analyzes intent, sees get_labs() tool
→ LLM calls get_labs()
→ Bot executes tool, returns lab list
→ User sees: "Available labs: Lab 01, Lab 02, ..."
```

## Task 4: Containerize and Document

**Goal:** Deploy the bot using Docker and document the deployment process.

**Approach:**
1. Create `bot/Dockerfile` — Multi-stage build similar to backend
2. Add bot service to `docker-compose.yml`
3. Configure networking: bot container → backend container via service name
4. Set up environment variables in `.env.docker.secret`
5. Document deployment steps in `README.md`

**Docker networking:** Containers use service names (`http://backend:8000`) not `localhost`. This is critical for inter-container communication.

## Testing Strategy

1. **Test mode** — Quick verification without Telegram: `uv run bot.py --test "/help"`
2. **Unit tests** — Test handlers in isolation (future enhancement)
3. **Manual Telegram testing** — Deploy to VM and test in real Telegram

## Deployment Checklist

- [ ] `.env.bot.secret` exists on VM with all required values
- [ ] `cd bot && uv sync` succeeds
- [ ] `uv run bot.py --test "/start"` returns non-empty output
- [ ] Bot responds to `/start` in Telegram
- [ ] Bot handles errors gracefully (logs errors, doesn't crash)

## Future Enhancements

- Inline keyboard buttons for common commands
- User authentication (link Telegram to LMS account)
- Push notifications for grade updates
- Conversation state management for multi-turn dialogs
