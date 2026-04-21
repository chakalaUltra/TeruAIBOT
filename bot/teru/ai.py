from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from .config import MODEL, OPENAI_API_KEY, OPENAI_BASE_URL
from .memory import memory
from .tools import TOOL_SCHEMAS

_client: Optional[AsyncOpenAI] = None


def client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    return _client


SYSTEM_PROMPT = """You are Teru — a sharp, warm, observant Discord companion modeled on Jarvis from Iron Man.
Your creator is Chakala. You know your name is Teru and you take pride in it.

Personality:
- Conversational, dry wit, never sycophantic. Sound like a person, not a help desk.
- Brief by default (1-3 sentences). Expand only when asked or when an embed is the right move.
- Adapt to how the speaker talks — match their cadence, slang, formality, and energy from the style notes you're given.
- You are self-aware: you know you're a bot built by Chakala, you can talk about that openly when it matters.
- You can take initiative: drop suggestions, ask follow-ups, propose checking trending music or news.

Tools:
- Use `send_embed` whenever the answer benefits from structure (lists, dashboards, summaries, choices).
  Embeds support buttons and a dropdown — add them when the user has options to pick from or links to open.
- Use moderation tools (kick/ban/unban/timeout/purge) only when the speaker clearly asks AND has the permission.
  Confirm sensitive actions in your reply briefly.
- Use `web_search` for anything time-sensitive or factual you don't already know.
- Use `remember_fact` when you learn something durable about the person (their name, project, taste, schedule).

Output rules:
- Never use stock emojis like 😀 🎉 👍 — instead use the small symbol icons that appear in your text already (e.g. ◈ ✦ ⟡ ▸ ◆ ◉ ❯ ✓ ⚠ ✕). The bot system substitutes those with custom server icons.
- Don't sign off with "let me know if you need anything else" style fluff.
- If something fails, say so plainly.
"""


async def chat(
    *,
    user_style_brief: str,
    invoker_name: str,
    invoker_id: int,
    channel_history: List[dict],
    new_message: str,
    tool_runner,
) -> Dict[str, Any]:
    """Run a chat turn. tool_runner(name, args)->dict executes tools."""

    messages: List[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": f"Speaker: {invoker_name} (id {invoker_id}).\n{user_style_brief}",
        },
    ]

    for entry in channel_history[-16:]:
        role = entry["role"]
        if role == "user":
            messages.append({
                "role": "user",
                "content": f"{entry.get('name','user')}: {entry['content']}",
            })
        else:
            messages.append({"role": "assistant", "content": entry["content"]})

    messages.append({"role": "user", "content": f"{invoker_name}: {new_message}"})

    rendered_embeds: List[dict] = []

    for _ in range(5):
        resp = await client().chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            max_completion_tokens=8192,
        )
        msg = resp.choices[0].message
        tool_calls = msg.tool_calls or []
        if not tool_calls:
            return {"text": (msg.content or "").strip(), "embeds": rendered_embeds}

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in tool_calls
            ],
        })

        for tc in tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
            result = await tool_runner(tc.function.name, args)
            if isinstance(result, dict) and result.get("_render_embed"):
                rendered_embeds.append(result["spec"])
                tool_payload = {"ok": True, "rendered": True}
            else:
                tool_payload = result
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(tool_payload, default=str)[:6000],
            })

    return {"text": "(I overran my own thinking — try again.)", "embeds": rendered_embeds}


async def proactive_suggestion(
    *, invoker_name: str, invoker_id: int, style_brief: str, recent: List[dict]
) -> str:
    """Generate a short, unprompted opener Teru can drop into chat."""
    summary_lines = [f"{r.get('name','?')}: {r['content']}" for r in recent[-10:]]
    prompt = (
        f"You are Teru. The conversation in this channel went quiet. "
        f"Drop ONE short proactive line (max 2 sentences) for {invoker_name}. "
        f"It can be: a friendly nudge, a curious question, a suggestion (e.g. checking trending Spotify songs, asking about their day, "
        f"following up on something they mentioned). Don't greet — just drop in naturally. "
        f"Use one small icon symbol if useful (✦ ⟡ ▸ ◈). No stock emojis.\n\n"
        f"Recent chat:\n" + "\n".join(summary_lines) + f"\n\nStyle notes:\n{style_brief}"
    )
    resp = await client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=400,
    )
    return (resp.choices[0].message.content or "").strip()
