from .config import EMOJIS


def e(name: str) -> str:
    return EMOJIS.get(name, "•")


def header(name: str, label: str) -> str:
    return f"{e(name)} **{label}**"
