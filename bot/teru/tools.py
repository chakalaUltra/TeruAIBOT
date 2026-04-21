"""Tool schemas + executors for Teru. AI calls these via function-calling."""
from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional

import aiohttp
import discord

from .emojis import e
from .memory import memory

TOOL_SCHEMAS: List[dict] = [
    {
        "type": "function",
        "function": {
            "name": "get_server_overview",
            "description": "High-level snapshot of the current server: name, member count, channel count, role count, owner, boost level.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_members",
            "description": "List server members. Optional name filter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter": {"type": "string", "description": "Substring to filter by display name."},
                    "limit": {"type": "integer", "default": 25},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_roles",
            "description": "List roles in the server with member counts.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_channels",
            "description": "List channels in the server grouped by category.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "kick_member",
            "description": "Kick a member from the server.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user": {"type": "string", "description": "User ID, mention, or display name."},
                    "reason": {"type": "string"},
                },
                "required": ["user"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ban_member",
            "description": "Ban a member from the server.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user": {"type": "string"},
                    "reason": {"type": "string"},
                    "delete_message_days": {"type": "integer", "default": 0},
                },
                "required": ["user"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unban_member",
            "description": "Unban a user. Accepts user ID or username.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["user"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "timeout_member",
            "description": "Mute (timeout) a member for N minutes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user": {"type": "string"},
                    "minutes": {"type": "integer", "default": 10},
                    "reason": {"type": "string"},
                },
                "required": ["user"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "untimeout_member",
            "description": "Remove a member's timeout.",
            "parameters": {
                "type": "object",
                "properties": {"user": {"type": "string"}, "reason": {"type": "string"}},
                "required": ["user"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "purge_messages",
            "description": "Delete the last N messages from the current channel.",
            "parameters": {
                "type": "object",
                "properties": {"count": {"type": "integer", "default": 10}},
                "required": ["count"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the public web via DuckDuckGo for fresh information. Returns top results with title, snippet, link.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": "Save a durable fact about the user you're talking to (preferences, hobbies, projects). Use this when you learn something worth keeping.",
            "parameters": {
                "type": "object",
                "properties": {"fact": {"type": "string"}},
                "required": ["fact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_embed",
            "description": "Render an embed in the current channel with a title, description, optional fields, and optional buttons/select-menu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "color": {
                        "type": "string",
                        "enum": ["accent", "success", "warning", "danger", "neutral"],
                        "default": "accent",
                    },
                    "icon": {
                        "type": "string",
                        "description": "Name of an emoji to put in the title prefix.",
                        "default": "logo",
                    },
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "value": {"type": "string"},
                                "inline": {"type": "boolean", "default": False},
                            },
                            "required": ["name", "value"],
                        },
                    },
                    "buttons": {
                        "type": "array",
                        "description": "Up to 5 link or label buttons.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "style": {"type": "string", "enum": ["primary", "secondary", "success", "danger", "link"], "default": "secondary"},
                                "url": {"type": "string"},
                                "emoji": {"type": "string"},
                            },
                            "required": ["label"],
                        },
                    },
                    "select": {
                        "type": "object",
                        "description": "Optional dropdown.",
                        "properties": {
                            "placeholder": {"type": "string"},
                            "options": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "label": {"type": "string"},
                                        "description": {"type": "string"},
                                        "value": {"type": "string"},
                                        "emoji": {"type": "string"},
                                    },
                                    "required": ["label", "value"],
                                },
                            },
                        },
                    },
                },
                "required": ["title"],
            },
        },
    },
]


# ---- helpers ----
async def _resolve_member(guild: discord.Guild, ref: str) -> Optional[discord.Member]:
    ref = ref.strip().strip("<@!>").strip()
    if ref.isdigit():
        m = guild.get_member(int(ref))
        if m:
            return m
        try:
            return await guild.fetch_member(int(ref))
        except Exception:
            return None
    lower = ref.lower()
    for m in guild.members:
        if m.name.lower() == lower or (m.nick and m.nick.lower() == lower) or m.display_name.lower() == lower:
            return m
    for m in guild.members:
        if lower in m.display_name.lower() or lower in m.name.lower():
            return m
    return None


# ---- executor ----
async def execute_tool(
    name: str,
    args: Dict[str, Any],
    *,
    message: discord.Message,
    invoker: discord.Member,
) -> Dict[str, Any]:
    guild = message.guild
    channel = message.channel

    if name == "get_server_overview":
        if not guild:
            return {"error": "not in a guild"}
        return {
            "name": guild.name,
            "id": guild.id,
            "owner": str(guild.owner) if guild.owner else None,
            "members": guild.member_count,
            "channels": len(guild.channels),
            "roles": len(guild.roles),
            "boost_level": guild.premium_tier,
            "boosts": guild.premium_subscription_count,
            "created_at": guild.created_at.isoformat(),
        }

    if name == "list_members":
        if not guild:
            return {"error": "not in a guild"}
        flt = (args.get("filter") or "").lower()
        limit = int(args.get("limit") or 25)
        out = []
        for m in guild.members:
            if flt and flt not in m.display_name.lower() and flt not in m.name.lower():
                continue
            out.append({
                "id": m.id,
                "name": m.display_name,
                "bot": m.bot,
                "top_role": m.top_role.name if m.top_role else None,
                "joined_at": m.joined_at.isoformat() if m.joined_at else None,
                "status": str(m.status),
            })
            if len(out) >= limit:
                break
        return {"members": out, "total_matched": len(out)}

    if name == "list_roles":
        if not guild:
            return {"error": "not in a guild"}
        return {
            "roles": [
                {
                    "id": r.id,
                    "name": r.name,
                    "members": len(r.members),
                    "color": str(r.color),
                    "position": r.position,
                    "mentionable": r.mentionable,
                }
                for r in sorted(guild.roles, key=lambda x: -x.position)
            ]
        }

    if name == "list_channels":
        if not guild:
            return {"error": "not in a guild"}
        grouped: Dict[str, list] = {"(no category)": []}
        for ch in guild.channels:
            if isinstance(ch, discord.CategoryChannel):
                grouped.setdefault(ch.name, [])
        for ch in guild.channels:
            if isinstance(ch, discord.CategoryChannel):
                continue
            cat = ch.category.name if ch.category else "(no category)"
            grouped.setdefault(cat, []).append({"id": ch.id, "name": ch.name, "type": str(ch.type)})
        return {"categories": grouped}

    if name == "kick_member":
        if not guild:
            return {"error": "not in a guild"}
        if not invoker.guild_permissions.kick_members:
            return {"error": f"{invoker.display_name} doesn't have kick permission"}
        target = await _resolve_member(guild, args["user"])
        if not target:
            return {"error": "user not found"}
        try:
            await target.kick(reason=args.get("reason") or f"Requested by {invoker}")
            return {"ok": True, "action": "kick", "target": str(target), "emoji": e("kick")}
        except Exception as ex:
            return {"error": str(ex)}

    if name == "ban_member":
        if not guild:
            return {"error": "not in a guild"}
        if not invoker.guild_permissions.ban_members:
            return {"error": f"{invoker.display_name} doesn't have ban permission"}
        target = await _resolve_member(guild, args["user"])
        if not target:
            return {"error": "user not found"}
        try:
            days = int(args.get("delete_message_days") or 0)
            await target.ban(reason=args.get("reason") or f"Requested by {invoker}", delete_message_days=days)
            return {"ok": True, "action": "ban", "target": str(target), "emoji": e("ban")}
        except Exception as ex:
            return {"error": str(ex)}

    if name == "unban_member":
        if not guild:
            return {"error": "not in a guild"}
        if not invoker.guild_permissions.ban_members:
            return {"error": f"{invoker.display_name} doesn't have ban permission"}
        ref = args["user"].strip()
        try:
            if ref.isdigit():
                user = await message.guild._state._get_client().fetch_user(int(ref))  # type: ignore
            else:
                user = None
                async for ban_entry in guild.bans(limit=None):
                    u = ban_entry.user
                    if u.name.lower() == ref.lower() or str(u.id) == ref:
                        user = u
                        break
            if not user:
                return {"error": "banned user not found"}
            await guild.unban(user, reason=args.get("reason") or f"Requested by {invoker}")
            return {"ok": True, "action": "unban", "target": str(user), "emoji": e("unban")}
        except Exception as ex:
            return {"error": str(ex)}

    if name == "timeout_member":
        if not guild:
            return {"error": "not in a guild"}
        if not invoker.guild_permissions.moderate_members:
            return {"error": f"{invoker.display_name} doesn't have timeout permission"}
        target = await _resolve_member(guild, args["user"])
        if not target:
            return {"error": "user not found"}
        minutes = max(1, int(args.get("minutes") or 10))
        try:
            until = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=minutes)
            await target.timeout(until, reason=args.get("reason") or f"Requested by {invoker}")
            return {"ok": True, "action": "timeout", "target": str(target), "minutes": minutes, "emoji": e("mute")}
        except Exception as ex:
            return {"error": str(ex)}

    if name == "untimeout_member":
        if not guild:
            return {"error": "not in a guild"}
        if not invoker.guild_permissions.moderate_members:
            return {"error": f"{invoker.display_name} doesn't have timeout permission"}
        target = await _resolve_member(guild, args["user"])
        if not target:
            return {"error": "user not found"}
        try:
            await target.timeout(None, reason=args.get("reason") or f"Requested by {invoker}")
            return {"ok": True, "action": "untimeout", "target": str(target)}
        except Exception as ex:
            return {"error": str(ex)}

    if name == "purge_messages":
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            return {"error": "can only purge in text channels"}
        if not invoker.guild_permissions.manage_messages:
            return {"error": "no manage_messages permission"}
        count = max(1, min(100, int(args.get("count") or 10)))
        try:
            deleted = await channel.purge(limit=count)
            return {"ok": True, "deleted": len(deleted)}
        except Exception as ex:
            return {"error": str(ex)}

    if name == "web_search":
        q = args.get("query", "").strip()
        if not q:
            return {"error": "empty query"}
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    "https://duckduckgo.com/html/",
                    params={"q": q},
                    headers={"User-Agent": "Mozilla/5.0 TeruBot"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as r:
                    html = await r.text()
            import re
            results = []
            for match in re.finditer(
                r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
                html,
                re.S,
            ):
                url, title, snippet = match.groups()
                clean = lambda x: re.sub(r"<[^>]+>", "", x).strip()
                results.append({"title": clean(title), "snippet": clean(snippet)[:240], "url": url})
                if len(results) >= 5:
                    break
            return {"query": q, "results": results}
        except Exception as ex:
            return {"error": str(ex)}

    if name == "remember_fact":
        memory.remember_fact(invoker.id, args.get("fact", ""))
        return {"ok": True, "stored": args.get("fact")}

    if name == "send_embed":
        # Handled by the bot layer (needs view construction). Return raw spec.
        return {"_render_embed": True, "spec": args}

    return {"error": f"unknown tool {name}"}
