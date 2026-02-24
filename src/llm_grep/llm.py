"""LLM interface for llm_grep.

Thin wrapper around litellm.completion() with streaming support.
"""

from __future__ import annotations

import sys
from collections.abc import Generator
from typing import TYPE_CHECKING

import litellm

if TYPE_CHECKING:
    from llm_grep.config import Config

# Suppress litellm's noisy default logging.
litellm.suppress_debug_info = True


def stream_completion(
    config: Config,
    prompt: str,
    stdin_text: str,
) -> Generator[str, None, None]:
    """Yield streamed text chunks from the LLM.

    The user message is constructed by combining the user's prompt with the
    piped stdin text.  The system message instructs the LLM to behave as a
    text-processing tool.
    """
    user_message = f"{prompt}\n\n---\n\n{stdin_text}"

    messages = [
        {"role": "system", "content": config.system_prompt},
        {"role": "user", "content": user_message},
    ]

    response = litellm.completion(
        model=config.model,
        messages=messages,
        temperature=config.temperature,
        stream=True,
        **config.extra,
    )

    for chunk in response:
        delta = chunk.choices[0].delta  # type: ignore[union-attr]
        if delta and delta.content:
            yield delta.content


def _is_ollama_model(model: str) -> bool:
    """Return True if the model string targets a local Ollama instance."""
    return model.startswith(("ollama/", "ollama_chat/"))


def run(config: Config, prompt: str, stdin_text: str) -> int:
    """Send the prompt + stdin to the LLM and stream the response to stdout.

    Returns 0 on success, 1 on error.
    """
    try:
        for text in stream_completion(config, prompt, stdin_text):
            sys.stdout.write(text)
            sys.stdout.flush()
        # Ensure output ends with a newline for clean shell behavior.
        sys.stdout.write("\n")
        return 0
    except litellm.AuthenticationError:
        if _is_ollama_model(config.model):
            print(
                "Error: Could not authenticate with Ollama. "
                "Ensure 'ollama serve' is running.",
                file=sys.stderr,
            )
        else:
            print(
                "Error: Authentication failed. "
                "Set the appropriate API key environment variable "
                "(e.g. OPENAI_API_KEY, ANTHROPIC_API_KEY).",
                file=sys.stderr,
            )
        return 1
    except litellm.BadRequestError as exc:
        print(f"Error: Bad request — {exc}", file=sys.stderr)
        return 1
    except litellm.APIConnectionError as exc:
        if _is_ollama_model(config.model):
            print(
                "Error: Could not connect to Ollama. "
                "Ensure 'ollama serve' is running on the expected host "
                "(default: http://localhost:11434). "
                "Set 'api_base' in your config file for a custom URL.",
                file=sys.stderr,
            )
        else:
            print(
                f"Error: Could not connect to the LLM API — {exc}",
                file=sys.stderr,
            )
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1
