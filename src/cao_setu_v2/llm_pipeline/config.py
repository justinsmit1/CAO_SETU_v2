"""Loads Mistral settings from config.toml (with env var overrides)."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config.toml"


@dataclass(frozen=True)
class MistralConfig:
    api_key: str
    model: str
    embed_model: str


def _load_toml() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


def load_config() -> MistralConfig:
    toml = _load_toml()
    mistral = toml.get("mistral", {})
    defaults = toml.get("defaults", {})

    api_key = os.environ.get("MISTRAL_API_KEY") or mistral.get("api_key")
    if not api_key:
        raise SystemExit(
            "MISTRAL_API_KEY is not set. Get one at https://console.mistral.ai/ "
            "(or set api_key under [mistral] in config.toml)"
        )

    return MistralConfig(
        api_key=api_key,
        model=defaults.get("model", "open-mistral-7b"),
        embed_model=defaults.get("embed_model", "mistral-embed"),
    )


def load_hf_token() -> str | None:
    toml = _load_toml()
    return (
        os.environ.get("HF_TOKEN")
        or os.environ.get("HUGGING_FACE_HUB_TOKEN")
        or toml.get("hf", {}).get("HF_TOKEN")
    )
