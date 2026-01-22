FROM python:3.13-slim

LABEL org.opencontainers.image.source="https://github.com/VWS-Python/vws-cli"
LABEL org.opencontainers.image.description="CLI for Vuforia Web Services"
LABEL org.opencontainers.image.licenses="MIT"

ARG VWS_CLI_VERSION

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install the package from PyPI with pinned version
RUN uv pip install --system --no-cache "vws-cli==${VWS_CLI_VERSION}"

# Set up entrypoint - users can override with vuforia-cloud-reco
ENTRYPOINT ["vws"]
