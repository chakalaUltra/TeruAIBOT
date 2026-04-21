"""Lightweight persistent memory: per-user speech profile + recent dialog."""
from __future__ import annotations

import json
import os
import time
from collections import deque
from pathlib import Path
from typing import Deque, Dict, List

DATA_DIR = Path(os.getenv("TERU_DATA_DIR", "bot/teru/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_FILE = DATA_DIR / "memory.json"

MAX_HISTORY = 24
MAX_STYLE_SAMPLES = 40


class Memory:
    def __init__(self) -> None:
        self._users: Dict[str, dict] = {}
        self._channels: Dict[str, Deque[dict]] = {}
        self._load()

    def _load(self) -> None:
        if MEMORY_FILE.exists():
            try:
                raw = json.loads(MEMORY_FILE.read_text())
                self._users = raw.get("users", {})
            except Exception:
                self._users = {}

    def _save(self) -> None:
        try:
            MEMORY_FILE.write_text(
                json.dumps({"users": self._users}, indent=2, ensure_ascii=False)
            )
        except Exception:
            pass

    # --- user profile ---
    def user(self, user_id: int) -> dict:
        key = str(user_id)
        if key not in self._users:
            self._users[key] = {
                "samples": [],
                "facts": [],
                "first_seen": int(time.time()),
                "last_seen": int(time.time()),
                "message_count": 0,
            }
        return self._users[key]

    def observe_message(self, user_id: int, content: str) -> None:
        u = self.user(user_id)
        u["last_seen"] = int(time.time())
        u["message_count"] = u.get("message_count", 0) + 1
        sample = content.strip()
        if 3 < len(sample) < 280:
            samples: List[str] = u.setdefault("samples", [])
            samples.append(sample)
            if len(samples) > MAX_STYLE_SAMPLES:
                del samples[0 : len(samples) - MAX_STYLE_SAMPLES]
        if u["message_count"] % 5 == 0:
            self._save()

    def remember_fact(self, user_id: int, fact: str) -> None:
        u = self.user(user_id)
        facts = u.setdefault("facts", [])
        fact = fact.strip()
        if fact and fact not in facts:
            facts.append(fact)
            if len(facts) > 40:
                del facts[0 : len(facts) - 40]
            self._save()

    def style_brief(self, user_id: int) -> str:
        u = self.user(user_id)
        samples = u.get("samples", [])[-12:]
        facts = u.get("facts", [])[-15:]
        parts = []
        if samples:
            joined = " ⟂ ".join(s.replace("\n", " ") for s in samples)
            parts.append(f"Recent ways they speak: {joined}")
        if facts:
            parts.append("Things you've learned about them: " + " | ".join(facts))
        parts.append(f"You have spoken with them {u.get('message_count', 0)} times.")
        return "\n".join(parts)

    # --- per-channel rolling dialog ---
    def push_dialog(self, channel_id: int, role: str, name: str, content: str) -> None:
        dq = self._channels.setdefault(str(channel_id), deque(maxlen=MAX_HISTORY))
        dq.append({"role": role, "name": name, "content": content})

    def get_dialog(self, channel_id: int) -> List[dict]:
        return list(self._channels.get(str(channel_id), []))


memory = Memory()
