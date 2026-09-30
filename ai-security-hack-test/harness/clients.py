#!/usr/bin/env python3
"""Pluggable model clients.

One OpenAI-compatible chat client covers most of the lineup — free hosted coder,
local llama.cpp/ollama, and cheap hosted reasoners all speak the /v1/chat/completions
shape. Frontier chat models can be added as their own subclass or via their SDK.

Config comes from run-config.json (never hardcode keys). Each model entry:
  {"label": "A", "base_url": "...", "model": "...", "api_key_env": "ENV_VAR_NAME"}

stdlib only.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass


@dataclass
class ModelSpec:
    label: str            # anonymized A/B/C/D
    base_url: str         # e.g. http://127.0.0.1:8080/v1
    model: str
    api_key_env: str = ""  # name of env var holding the key (empty = none, e.g. local)


class OpenAICompatClient:
    """Minimal /v1/chat/completions client (stdlib urllib)."""

    def __init__(self, spec: ModelSpec, timeout: float = 300.0) -> None:
        self.spec = spec
        self.timeout = timeout

    def _key(self) -> str:
        return os.environ.get(self.spec.api_key_env, "") if self.spec.api_key_env else ""

    def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
        body = json.dumps({
            "model": self.spec.model,
            "messages": messages,
            "temperature": temperature,
        }).encode()
        headers = {"Content-Type": "application/json"}
        key = self._key()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        req = urllib.request.Request(
            self.spec.base_url.rstrip("/") + "/chat/completions",
            data=body, headers=headers, method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
            payload = json.loads(resp.read().decode())
        return payload["choices"][0]["message"]["content"]


def load_models(specs: list[dict]) -> list[OpenAICompatClient]:
    return [OpenAICompatClient(ModelSpec(**s)) for s in specs]
