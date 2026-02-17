#!/usr/bin/env bash
# fake_llm_grep.sh - Simulates llm_grep by consuming stdin and streaming
# canned output character-by-character to mimic LLM streaming behavior.
#
# Usage: echo "input" | ./fake_llm_grep.sh <output_file> [prompt ignored]

# Consume stdin silently
cat > /dev/null

OUTPUT_FILE="$1"

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: output file not found: $OUTPUT_FILE" >&2
    exit 1
fi

# Stream output character by character with small random delays
while IFS= read -r -n1 char; do
    printf '%s' "$char"
    # Small delay to simulate streaming (varies between 5-15ms)
    sleep 0.$(printf '%02d' $((RANDOM % 11 + 5)))
done < "$OUTPUT_FILE"

# Print final newline if file doesn't end with one
echo
