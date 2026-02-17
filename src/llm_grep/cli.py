"""CLI entry point for llm_grep.

Usage:
    some_command | llm_grep "your prompt here"
    some_command | llm_grep --model anthropic/claude-sonnet-4-20250514 "summarize this"
"""

from __future__ import annotations

import argparse
import sys

from llm_grep import __version__
from llm_grep.config import build_config
from llm_grep.llm import run


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm_grep",
        description="Pipe command output through an LLM for intelligent text processing.",
        epilog=(
            "Examples:\n"
            '  cat logs.txt | llm_grep "extract all error messages"\n'
            '  kubectl get pods | llm_grep "which pods are failing?"\n'
            '  git diff | llm_grep --model anthropic/claude-sonnet-4-20250514 "summarize changes"\n'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "prompt",
        help="Instruction for the LLM describing how to process the input.",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=None,
        help="LLM model to use (litellm format, e.g. openai/gpt-4o, anthropic/claude-sonnet-4-20250514). "
        "Overrides config file and LLM_GREP_MODEL env var.",
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=None,
        help="Sampling temperature (0.0 = deterministic). Default: 0.0.",
    )
    parser.add_argument(
        "-s",
        "--system-prompt",
        default=None,
        help="Override the default system prompt.",
    )
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        metavar="PATH",
        help="Path to config file. Default: ~/.config/llm_grep/config.yaml",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    """Main entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Ensure we're receiving piped input.
    if sys.stdin.isatty():
        parser.error(
            'No piped input detected. Usage: some_command | llm_grep "your prompt"'
        )

    stdin_text = sys.stdin.read()

    if not stdin_text.strip():
        parser.error("Received empty input from stdin.")

    config = build_config(
        config_path=args.config,
        model=args.model,
        temperature=args.temperature,
        system_prompt=args.system_prompt,
    )

    exit_code = run(config, args.prompt, stdin_text)
    raise SystemExit(exit_code)
