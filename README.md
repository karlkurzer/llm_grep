# llm_grep

Pipe any command output through an LLM for intelligent text processing.

### Extract errors from noisy logs

![Log analysis demo](assets/demo_logs.gif)

### Transform JSON into clean tables

![JSON transform demo](assets/demo_json.gif)

### Analyze processes with natural language

![Process analysis demo](assets/demo_process.gif)

## Installation

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
# Install as a global CLI tool (recommended)
uv tool install .

# For AWS Bedrock support, include the bedrock extra
uv tool install ".[bedrock]"

# Now use it anywhere
cat logs.txt | llm_grep "find errors"
```

To update after making changes to the source:

```bash
uv tool install . --force
# or with Bedrock support:
uv tool install ".[bedrock]" --force
```

To uninstall:

```bash
uv tool uninstall llm-grep
```

## Configuration

The default model is `bedrock/global.amazon.nova-2-lite-v1:0`. It uses
[litellm](https://docs.litellm.ai/) under the hood, so any provider litellm
supports works — including local models via [Ollama](https://ollama.com/).

### Config file

Create `~/.config/llm_grep/config.yaml` for persistent settings:

```yaml
model: bedrock/global.amazon.nova-2-lite-v1:0
temperature: 0.0
# Optional: override AWS credential resolution
aws_profile_name: my-profile
aws_region_name: us-east-1
```

Any key not recognized by llm_grep (`model`, `temperature`, `system_prompt`)
is forwarded directly to `litellm.completion()` as a keyword argument. This
is how `aws_*` keys, `max_tokens`, and other provider-specific options work.

### Model selection

Override the default model in three ways (highest precedence first):

1. **CLI flag**: `--model` / `-m`
2. **Environment variable**: `LLM_GREP_MODEL`
3. **Config file**

Models use litellm's `provider/model-name` convention, e.g.:

- `bedrock/global.amazon.nova-2-lite-v1:0`
- `bedrock/anthropic.claude-sonnet-4-20250514-v1:0`
- `openai/gpt-4o`
- `anthropic/claude-sonnet-4-20250514`
- `ollama/gemma3:1b`

For cloud providers, set the appropriate API key env var
(e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) — see the
[litellm docs](https://docs.litellm.ai/). For AWS Bedrock, any standard
credential chain works (env vars, `~/.aws/credentials`, instance role, etc.).

### Local models (Ollama)

Run any model locally with [Ollama](https://ollama.com/) — no API keys required.

```bash
# 1. Install Ollama (https://ollama.com/download)
# 2. Pull a model
ollama pull gemma3:1b

# 3. Use it with llm_grep (ollama serve starts automatically)
cat logs.txt | llm_grep -m ollama/gemma3:1b "show only error lines"
```

To make an Ollama model the default, set it in your config file:

```yaml
model: ollama/gemma3:1b
```

If Ollama is running on a non-default host or port, add `api_base`:

```yaml
model: ollama/gemma3:1b
api_base: http://my-host:11434
```

## Usage

```
usage: llm_grep [-h] [-m MODEL] [-t TEMPERATURE] [-s SYSTEM_PROMPT] [-c PATH] [-V] prompt
```

| Flag | Description |
|---|---|
| `prompt` | Instruction for the LLM (positional, required) |
| `-m`, `--model` | LLM model to use |
| `-t`, `--temperature` | Sampling temperature (default: 0.0) |
| `-s`, `--system-prompt` | Override the default system prompt |
| `-c`, `--config` | Path to config file |
| `-V`, `--version` | Show version |

### Examples

```bash
# Extract errors from logs
tail -100 /var/log/syslog | llm_grep "show only error and warning lines"

# Summarize a diff
git diff HEAD~3 | llm_grep "summarize what changed and why it matters"

# Filter and transform JSON
curl -s https://api.example.com/data | llm_grep "extract all email addresses as a plain list"

# Use a different cloud model
ps aux | llm_grep -m bedrock/anthropic.claude-sonnet-4-20250514-v1:0 "which processes are using the most memory?"

# Use a local Ollama model
ps aux | llm_grep -m ollama/gemma3:1b "which processes are using the most CPU?"
```