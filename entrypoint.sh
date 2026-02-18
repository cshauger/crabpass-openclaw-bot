#!/bin/sh
set -e

echo "=== CrabPass OpenClaw Bot ==="
echo "Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo "Owner ID: $OWNER_TELEGRAM_ID"
echo "Model: ${MODEL:-groq/llama-3.3-70b-versatile}"

# Create config directory
mkdir -p /home/node/.openclaw

# Generate config file
cat > /home/node/.openclaw/config.yaml << YAML
model: ${MODEL:-groq/llama-3.3-70b-versatile}

channels:
  telegram:
    token: ${TELEGRAM_BOT_TOKEN}
    allowedUsers:
      - "${OWNER_TELEGRAM_ID}"
YAML

echo "Config created:"
cat /home/node/.openclaw/config.yaml

echo ""
echo "Starting gateway..."
exec node /app/dist/index.js gateway
