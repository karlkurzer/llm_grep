"""Tests for llm_grep configuration."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from llm_grep.config import (
    DEFAULT_MODEL,
    DEFAULT_SYSTEM_PROMPT,
    Config,
    build_config,
    load_config_file,
)


class TestLoadConfigFile:
    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        assert load_config_file(tmp_path / "nonexistent.yaml") == {}

    def test_empty_file_returns_empty(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("")
        assert load_config_file(cfg) == {}

    def test_valid_yaml(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text(
            textwrap.dedent("""\
                model: anthropic/claude-sonnet-4-20250514
                temperature: 0.5
            """)
        )
        data = load_config_file(cfg)
        assert data["model"] == "anthropic/claude-sonnet-4-20250514"
        assert data["temperature"] == 0.5


class TestBuildConfig:
    def test_defaults(self) -> None:
        config = build_config(config_path="/nonexistent/path.yaml")
        assert config.model == DEFAULT_MODEL
        assert config.temperature == 0.0
        assert config.system_prompt == DEFAULT_SYSTEM_PROMPT

    def test_cli_overrides_file(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("model: openai/gpt-4o\ntemperature: 0.9\n")

        config = build_config(
            config_path=str(cfg),
            model="anthropic/claude-sonnet-4-20250514",
            temperature=0.1,
        )
        assert config.model == "anthropic/claude-sonnet-4-20250514"
        assert config.temperature == 0.1

    def test_file_values_used_when_no_cli(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("model: openai/gpt-4o\ntemperature: 0.7\n")

        config = build_config(config_path=str(cfg))
        assert config.model == "openai/gpt-4o"
        assert config.temperature == 0.7

    def test_env_var_override(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LLM_GREP_MODEL", "ollama/llama3")
        config = build_config(config_path="/nonexistent/path.yaml")
        assert config.model == "ollama/llama3"

    def test_cli_beats_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_GREP_MODEL", "ollama/llama3")
        config = build_config(
            config_path="/nonexistent/path.yaml",
            model="openai/gpt-4o",
        )
        assert config.model == "openai/gpt-4o"

    def test_extra_keys_passed_through(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("model: openai/gpt-4o\nmax_tokens: 1024\n")

        config = build_config(config_path=str(cfg))
        assert config.extra == {"max_tokens": 1024}


class TestConfigDataclass:
    def test_defaults(self) -> None:
        c = Config()
        assert c.model == DEFAULT_MODEL
        assert c.temperature == 0.0
        assert c.extra == {}
