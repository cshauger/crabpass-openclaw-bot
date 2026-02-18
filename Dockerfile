# Simple OpenClaw wrapper for CrabPass
FROM ghcr.io/openclaw/openclaw:latest

# Install envsubst for config templating
USER root
RUN apt-get update && apt-get install -y gettext-base && rm -rf /var/lib/apt/lists/*

# Create workspace and config directories
RUN mkdir -p /data/workspace /data/.openclaw && chown -R openclaw:openclaw /data

USER openclaw
WORKDIR /home/openclaw

# Copy startup script and config template
COPY --chown=openclaw:openclaw entrypoint.sh /home/openclaw/entrypoint.sh
COPY --chown=openclaw:openclaw config.template.yaml /home/openclaw/config.template.yaml
COPY --chown=openclaw:openclaw workspace/ /data/workspace/

RUN chmod +x /home/openclaw/entrypoint.sh

ENV OPENCLAW_STATE_DIR=/data/.openclaw
ENV OPENCLAW_WORKSPACE_DIR=/data/workspace

ENTRYPOINT ["/home/openclaw/entrypoint.sh"]
