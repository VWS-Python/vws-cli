SHELL := /bin/bash -euxo pipefail

include lint.mk

.PHONY: lint
lint: \
    check-manifest \
    doc8 \
    flake8 \
    isort \
    linkcheck \
    mypy \
    pip-extra-reqs \
    pip-missing-reqs \
    pylint \
    pyroma \
    shellcheck \
    spelling \
    vulture \
    yapf

.PHONY: fix-lint
fix-lint:
	# Move imports to a single line so that autoflake can handle them.
	# See https://github.com/myint/autoflake/issues/8.
	# Then later we put them back.
	isort --force-single-line --recursive --apply
	autoflake \
	    --in-place \
	    --recursive \
	    --remove-all-unused-imports \
	    --remove-unused-variables \
	    --exclude src/vws/_version.py,versioneer.py \
	    .
	yapf \
	    --in-place \
	    --recursive \
	    --exclude versioneer.py  \
	    --exclude src/vws/_version.py \
	    .
	isort --recursive --apply

.PHONY: docs
docs:
	make -C docs clean html SPHINXOPTS=$(SPHINXOPTS)

.PHONY: open-docs
open-docs:
	python -c 'import os, webbrowser; webbrowser.open("file://" + os.path.abspath("docs/build/html/index.html"))'
