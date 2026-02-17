"""Tests for llm_grep CLI."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from llm_grep.cli import main


class TestCLIParsing:
    def test_version_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit, match="0"):
            main(["--version"])
        assert "llm_grep" in capsys.readouterr().out

    def test_help_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit, match="0"):
            main(["--help"])
        output = capsys.readouterr().out
        assert "Pipe command output" in output

    def test_rejects_tty_stdin(self) -> None:
        """When stdin is a tty (no pipe), the CLI should error."""
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            with pytest.raises(SystemExit, match="2"):
                main(["some prompt"])


class TestCLIWithPipedInput:
    def test_rejects_empty_stdin(self) -> None:
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = False
            mock_stdin.read.return_value = "   "
            with pytest.raises(SystemExit, match="2"):
                main(["some prompt"])

    def test_calls_llm_run(self) -> None:
        with (
            patch("sys.stdin") as mock_stdin,
            patch("llm_grep.cli.run", return_value=0) as mock_run,
        ):
            mock_stdin.isatty.return_value = False
            mock_stdin.read.return_value = "hello world"

            with pytest.raises(SystemExit, match="0"):
                main(["summarize this"])

            mock_run.assert_called_once()
            _config, prompt, stdin_text = mock_run.call_args[0]
            assert prompt == "summarize this"
            assert stdin_text == "hello world"
