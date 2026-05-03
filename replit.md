# Project Overview

This monorepo hosts a Discord bot called **Teru** (creator: **Chakala**), a JARVIS-inspired AI assistant.

## Architecture

- `bot/teru/teru.py` — Main bot. discord.py + OpenAI (via Replit AI Integrations). Self-aware, learns user style, proactive, supports embeds/buttons/dropdowns, moderation, server insights, web search, mini-games, batch confirmations.
- `bot/teru/data/` — Persistent memory (`memory.json` for facts, `style.json` for per-user speaking style).
- `artifacts/api-server/` — Default Fastify API server (unused by Teru).
- `artifacts/mockup-sandbox/` — Default canvas preview (unused by Teru).

## Workflows

- **Teru Bot** — `python bot/teru/teru.py` (console; the live bot).
- API Server / Mockup Sandbox — defaults from the template.

## Secrets

- `DISCORD_BOT_TOKEN` — Required.
- `AI_INTEGRATIONS_OPENAI_BASE_URL` / `AI_INTEGRATIONS_OPENAI_API_KEY` — Auto-set via Replit AI Integrations (OpenAI).

## Teru behavior

- Wake: `Hey Teru` / mention / message starting with `Teru,`.
- Sleep: `Enough` / `Done` / `Set free` / `Detach` / `Goodbye` / `Bye Teru` / `Stop Teru`. Auto-detach after 15 min silence.
- Proactive loop: every 45 min there's a 35% chance Teru drops a suggestion in any active channel.
- Identity: never claims to be GPT/OpenAI; always credits **Chakala**.
- Custom Unicode glyphs instead of default emojis (✦ ◆ ● ➤ ✓ ✗ ⚠ ⚡ ★ ◉ ▣ ▲ ☾ ☀ ♥ ⚑ ♪ ℹ ⌕ ⛨).

## Slash commands

`/about /search /embed /remember /recall /insights /roles /members /kick /ban /unban /mute /unmute /purge`

## Discord setup checklist

1. In the Discord developer portal, enable **all 3 Privileged Gateway Intents** (Presence, Server Members, Message Content).
2. Invite Teru with **Administrator** (or: Manage Roles, Kick/Ban Members, Moderate Members, Manage Messages, Send Messages, Embed Links, Read Message History).
