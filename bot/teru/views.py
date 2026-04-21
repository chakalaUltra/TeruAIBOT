from __future__ import annotations

from typing import Any, Dict, List

import discord

from .config import (
    ACCENT_COLOR,
    DANGER_COLOR,
    NEUTRAL_COLOR,
    SUCCESS_COLOR,
    WARNING_COLOR,
)
from .emojis import e

_COLOR_MAP = {
    "accent": ACCENT_COLOR,
    "success": SUCCESS_COLOR,
    "warning": WARNING_COLOR,
    "danger": DANGER_COLOR,
    "neutral": NEUTRAL_COLOR,
}

_STYLE_MAP = {
    "primary": discord.ButtonStyle.primary,
    "secondary": discord.ButtonStyle.secondary,
    "success": discord.ButtonStyle.success,
    "danger": discord.ButtonStyle.danger,
    "link": discord.ButtonStyle.link,
}


class TeruDynamicView(discord.ui.View):
    def __init__(self, spec: Dict[str, Any]):
        super().__init__(timeout=600)
        for btn in (spec.get("buttons") or [])[:5]:
            style = _STYLE_MAP.get(btn.get("style", "secondary"), discord.ButtonStyle.secondary)
            kwargs = {"label": btn.get("label", "Button"), "style": style}
            emoji = btn.get("emoji")
            if emoji:
                try:
                    kwargs["emoji"] = emoji
                except Exception:
                    pass
            if style == discord.ButtonStyle.link:
                if btn.get("url"):
                    kwargs["url"] = btn["url"]
                    self.add_item(discord.ui.Button(**kwargs))
                continue
            button = discord.ui.Button(**kwargs)

            async def _cb(interaction: discord.Interaction, label=btn.get("label", "")):
                await interaction.response.send_message(
                    f"{e('spark')} You picked **{label}** — noted.", ephemeral=True
                )

            button.callback = _cb
            self.add_item(button)

        sel = spec.get("select")
        if sel and sel.get("options"):
            options: List[discord.SelectOption] = []
            for o in sel["options"][:25]:
                opt_kwargs = {"label": o["label"][:100], "value": o["value"][:100]}
                if o.get("description"):
                    opt_kwargs["description"] = o["description"][:100]
                if o.get("emoji"):
                    try:
                        opt_kwargs["emoji"] = o["emoji"]
                    except Exception:
                        pass
                options.append(discord.SelectOption(**opt_kwargs))
            select = discord.ui.Select(
                placeholder=sel.get("placeholder", "Pick one"),
                options=options,
                min_values=1,
                max_values=1,
            )

            async def _scb(interaction: discord.Interaction):
                value = select.values[0]
                await interaction.response.send_message(
                    f"{e('info')} You chose **{value}** — got it.", ephemeral=True
                )

            select.callback = _scb
            self.add_item(select)


def build_embed(spec: Dict[str, Any]) -> discord.Embed:
    color = _COLOR_MAP.get(spec.get("color", "accent"), ACCENT_COLOR)
    icon = e(spec.get("icon", "logo"))
    title = f"{icon}  {spec.get('title', '').strip()}"
    embed = discord.Embed(
        title=title[:256],
        description=(spec.get("description") or "")[:4000] or None,
        color=color,
    )
    for f in (spec.get("fields") or [])[:25]:
        embed.add_field(
            name=f"{e('dot')} {f['name']}"[:256],
            value=f["value"][:1024],
            inline=bool(f.get("inline", False)),
        )
    embed.set_footer(text=f"Teru · crafted by Chakala")
    return embed
