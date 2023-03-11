SHELL := /bin/bash -euxo pipefail

include lint.mk

# Treat Sphinx warnings as errors
SPHINXOPTS := -W

.PHONY: lint
lint: \
    black \
    check-manifest \
    doc8 \
    ruff \
    linkcheck \
    mypy \
    pip-extra-reqs \
    pip-missing-reqs \
    pyroma \
	shellcheck \
    spelling \
    vulture \
    pylint

.PHONY: fix-lint
fix-lint: \
    fix-black \
    fix-ruff

.PHONY: docs
docs:
	make -C docs clean html SPHINXOPTS=$(SPHINXOPTS)

.PHONY: open-docs
open-docs:
	python -c 'import os, webbrowser; webbrowser.open("file://" + os.path.abspath("docs/build/html/index.html"))'
