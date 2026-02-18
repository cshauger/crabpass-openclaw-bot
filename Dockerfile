# Simple OpenClaw wrapper for CrabPass
FROM ghcr.io/openclaw/openclaw:latest

# Copy startup script
COPY entrypoint.sh /entrypoint.sh

USER root
RUN chmod +x /entrypoint.sh

USER node

ENTRYPOINT ["/entrypoint.sh"]
