# Make commands for linting

SHELL := /bin/bash -euxo pipefail

.PHONY: actionlint
actionlint:
	actionlint

.PHONY: ruff
ruff:
	ruff check .
	ruff format --check .

.PHONY: fix-ruff
fix-ruff:
	ruff check --fix .
	ruff format .

.PHONY: mypy
mypy:
	mypy .

.PHONY: pyright
pyright:
	pyright .

.PHONY: pyright-verifytypes
pyright-verifytypes:
	pyright --verifytypes vws_cli

.PHONY: check-manifest
check-manifest:
	check-manifest .

.PHONY: doc8
doc8:
	doc8 .

TEMPFILE:= $(shell mktemp)

.PHONY: deptry
deptry:
	uv pip compile --no-deps pyproject.toml > $(TEMPFILE)
	mv pyproject.toml pyproject.bak.toml
	deptry --requirements-txt=$(TEMPFILE) src/ || (mv pyproject.bak.toml pyproject.toml && exit 1)
	mv pyproject.bak.toml pyproject.toml

.PHONY: pylint
pylint:
	pylint src/ tests/ admin/ docs/

.PHONY: pyroma
pyroma:
	pyroma --min 10 .

.PHONY: vulture
vulture:
	vulture --min-confidence 100 .

.PHONY: linkcheck
linkcheck:
	$(MAKE) -C docs/ linkcheck SPHINXOPTS=$(SPHINXOPTS)

.PHONY: spelling
spelling:
	$(MAKE) -C docs/ spelling SPHINXOPTS=$(SPHINXOPTS)

.PHONY: pyproject-fmt
 pyproject-fmt:
	pyproject-fmt --check pyproject.toml

 .PHONY: fix-pyproject-fmt
 fix-pyproject-fmt:
	pyproject-fmt pyproject.toml
