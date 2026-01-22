FROM python:3.13-slim

LABEL org.opencontainers.image.source="https://github.com/VWS-Python/vws-cli"
LABEL org.opencontainers.image.description="CLI for Vuforia Web Services"
LABEL org.opencontainers.image.licenses="MIT"

# Install the package from PyPI
# hadolint ignore=DL3013
RUN pip install --no-cache-dir vws-cli

# Set up entrypoint - users can override with vuforia-cloud-reco
ENTRYPOINT ["vws"]
