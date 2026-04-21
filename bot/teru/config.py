import os

BOT_NAME = "Teru"
CREATOR = "Chakala"

WAKE_PHRASES = ["hey teru", "yo teru", "teru wake up"]
SLEEP_PHRASES = ["enough", "done", "set free", "detach", "goodbye"]

DETACH_TIMEOUT_SECONDS = 60 * 10

PROACTIVE_MIN_SECONDS = 60 * 25
PROACTIVE_MAX_SECONDS = 60 * 90

ACCENT_COLOR = 0x6E5BFF
SUCCESS_COLOR = 0x3DD68C
WARNING_COLOR = 0xFFB454
DANGER_COLOR = 0xFF5C7A
NEUTRAL_COLOR = 0x2B2D31

EMOJIS = {
    "logo": os.getenv("TERU_EMOJI_LOGO", "◈"),
    "spark": os.getenv("TERU_EMOJI_SPARK", "✦"),
    "think": os.getenv("TERU_EMOJI_THINK", "⟡"),
    "ok": os.getenv("TERU_EMOJI_OK", "✓"),
    "warn": os.getenv("TERU_EMOJI_WARN", "⚠"),
    "danger": os.getenv("TERU_EMOJI_DANGER", "✕"),
    "info": os.getenv("TERU_EMOJI_INFO", "▸"),
    "user": os.getenv("TERU_EMOJI_USER", "◉"),
    "role": os.getenv("TERU_EMOJI_ROLE", "◆"),
    "channel": os.getenv("TERU_EMOJI_CHANNEL", "❯"),
    "ban": os.getenv("TERU_EMOJI_BAN", "⛔"),
    "kick": os.getenv("TERU_EMOJI_KICK", "➤"),
    "mute": os.getenv("TERU_EMOJI_MUTE", "✣"),
    "unban": os.getenv("TERU_EMOJI_UNBAN", "↺"),
    "music": os.getenv("TERU_EMOJI_MUSIC", "♪"),
    "search": os.getenv("TERU_EMOJI_SEARCH", "⌕"),
    "dot": os.getenv("TERU_EMOJI_DOT", "·"),
}

DISCORD_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")

MODEL = "gpt-5.2"
