SHELL := /bin/bash -euxo pipefail

.PHONY: lint
lint:
	flake8 .
