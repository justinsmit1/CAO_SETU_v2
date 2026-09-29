"""Het LLM als uitwisselbaar onderdeel.

Het invullen kent alleen het ``LLM``-protocol: berichten + JSON-schema erin, een dict (volgens het schema) eruit.
Welk model het wordt, is nog niet gekozen. ``MistralLLM`` gebruikt het model dat je expliciet opgeeft, of dat in
``config.toml`` staat onder ``[invullen] model = "..."``; er is bewust geen standaardmodel. In tests wordt
``nep.NepLLM`` gebruikt.
"""

import json
import tomllib
from pathlib import Path
from typing import Any, Protocol

CONFIG_PAD = Path(__file__).resolve().parents[4] / "config.toml"


class LLM(Protocol):
    def vraag_json(self, berichten: list[dict[str, str]], schema: dict[str, Any], naam: str) -> dict[str, Any]:
        """Stuurt de berichten (``{"role": "system"|"user"|"assistant", "content": ...}``) en geeft het antwoord
        terug als dict volgens ``schema`` (strict JSON-schema met de naam ``naam``)."""
        ...


class GeenModelGekozen(RuntimeError):
    pass


def invul_model(config_pad: str | Path = CONFIG_PAD) -> str:
    """Het model voor het invullen uit ``[invullen] model`` in config.toml."""
    pad = Path(config_pad)
    config = tomllib.loads(pad.read_text(encoding="utf-8")) if pad.exists() else {}
    model = config.get("invullen", {}).get("model")
    if not model:
        raise GeenModelGekozen(
            f"Er is nog geen model gekozen voor het invullen. Zet in {pad}:\n\n[invullen]\nmodel = \"...\"\n\n"
            "of geef het model op bij MistralLLM(model=...)."
        )
    return model


class MistralLLM:
    """Mistral chat met ``response_format`` json_schema (strict), zoals ``pijplijn/qa.py``."""

    def __init__(self, model: str, client: Any = None, temperatuur: float = 0.0):
        if client is None:
            from mistralai.client import Mistral

            from .pijplijn.config import load_config

            client = Mistral(api_key=load_config().api_key)
        self.model, self.client, self.temperatuur = model, client, temperatuur

    @classmethod
    def uit_config(cls, config_pad: str | Path = CONFIG_PAD) -> "MistralLLM":
        return cls(invul_model(config_pad))

    def vraag_json(self, berichten: list[dict[str, str]], schema: dict[str, Any], naam: str) -> dict[str, Any]:
        antwoord = self.client.chat.complete(
            model=self.model,
            messages=berichten,
            temperature=self.temperatuur,
            response_format={"type": "json_schema", "json_schema": {"name": naam, "schema": schema, "strict": True}},
        )
        return json.loads(antwoord.choices[0].message.content)
