#!/bin/bash
set -e

CONFIG_DIR="${OPENCLAW_STATE_DIR:-/data/.openclaw}"
CONFIG_FILE="$CONFIG_DIR/config.yaml"

echo "=== CrabPass OpenClaw Bot ==="
echo "Config dir: $CONFIG_DIR"
echo "Workspace: $OPENCLAW_WORKSPACE_DIR"

# Create config from template
mkdir -p "$CONFIG_DIR"
envsubst < /home/openclaw/config.template.yaml > "$CONFIG_FILE"

echo "Generated config:"
cat "$CONFIG_FILE"
echo ""

# Validate required vars
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "ERROR: TELEGRAM_BOT_TOKEN not set"
    exit 1
fi

if [ -z "$OWNER_TELEGRAM_ID" ]; then
    echo "ERROR: OWNER_TELEGRAM_ID not set"
    exit 1
fi

# Need at least one API key
if [ -z "$GROQ_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: No API key set (need GROQ_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY)"
    exit 1
fi

echo "Starting OpenClaw gateway..."
exec node dist/index.js gateway --config "$CONFIG_FILE"
