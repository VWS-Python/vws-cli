# Make commands for linting

SHELL := /bin/bash -euxo pipefail

.PHONY: black
black:
	black --check .

.PHONY: fix-black
fix-black:
	black .

.PHONY: ruff
ruff:
	ruff .

.PHONY: fix-ruff
fix-ruff:
	ruff --fix .

.PHONY: mypy
mypy:
	mypy .

.PHONY: pyright
pyright:
	pyright .

.PHONY: check-manifest
check-manifest:
	check-manifest .

.PHONY: doc8
doc8:
	doc8 .

.PHONY: pip-extra-reqs
pip-extra-reqs:
	pip-extra-reqs --requirements-file=<(pdm export --pyproject) src/

.PHONY: pip-missing-reqs
pip-missing-reqs:
	pip-missing-reqs --requirements-file=<(pdm export --pyproject) src/

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

.PHONY: shellcheck
shellcheck:
	shellcheck --exclude SC2164,SC1091 */*.sh
