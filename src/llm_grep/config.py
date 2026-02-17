"""Configuration loading for llm_grep.

Loads settings from ~/.config/llm_grep/config.yaml with CLI flag overrides.
API keys are handled via standard environment variables (OPENAI_API_KEY, etc.)
which litellm reads automatically.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "llm_grep" / "config.yaml"

DEFAULT_SYSTEM_PROMPT = (
    "You are a text processing tool similar to grep, but powered by an LLM. "
    "You receive input text piped from a command and a user instruction. "
    "Process the input according to the instruction and return only the result. "
    "Do not add explanations, commentary, or formatting unless the user explicitly asks for it."
)

DEFAULT_MODEL = "bedrock/global.amazon.nova-2-lite-v1:0"


@dataclass
class Config:
    """Resolved configuration for a single llm_grep invocation."""

    model: str = DEFAULT_MODEL
    temperature: float = 0.0
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    # Additional litellm kwargs passed through to the completion call.
    extra: dict[str, Any] = field(default_factory=dict)


def load_config_file(path: Path | None = None) -> dict[str, Any]:
    """Load and return the YAML config file as a dict.

    Returns an empty dict if the file does not exist or is empty.
    """
    config_path = path or DEFAULT_CONFIG_PATH
    if not config_path.is_file():
        return {}

    with open(config_path) as f:
        data = yaml.safe_load(f)

    return data if isinstance(data, dict) else {}


def build_config(
    *,
    config_path: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    system_prompt: str | None = None,
) -> Config:
    """Build a resolved Config by merging config file values with CLI overrides.

    Precedence (highest to lowest):
      1. CLI flags
      2. Environment variable LLM_GREP_MODEL (for model only)
      3. Config file
      4. Built-in defaults
    """
    file_data = load_config_file(Path(config_path) if config_path else None)

    # Extract known keys; everything else is passed through to litellm as
    # keyword arguments.  This includes provider-specific options such as
    # aws_profile_name, aws_region_name, max_tokens, etc.
    known_keys = {"model", "temperature", "system_prompt"}
    extra = {k: v for k, v in file_data.items() if k not in known_keys}

    env_model = os.environ.get("LLM_GREP_MODEL")

    resolved_model = model or env_model or file_data.get("model") or DEFAULT_MODEL
    resolved_temp = (
        temperature if temperature is not None else file_data.get("temperature", 0.0)
    )
    resolved_system = (
        system_prompt or file_data.get("system_prompt") or DEFAULT_SYSTEM_PROMPT
    )

    return Config(
        model=resolved_model,
        temperature=resolved_temp,
        system_prompt=resolved_system,
        extra=extra,
    )
