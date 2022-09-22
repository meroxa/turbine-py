SHELL=/bin/bash -o pipefail

install: requirements.txt
	pip install -r requirements.txt

install-dev: requirements-dev.txt
	pip install -r requirements-dev.txt

funtime: ./src/turbine/function-deploy/function-app/requirements.txt
	pip install -r ./src/turbine/function-deploy/function-app/requirements.txt

run-hooks:
	pre-commit run --all-files

install-hooks: install-dev
	pre-commit install

test:
	pytest

.PHONY: lint
lint:
	black src
	flake8 src
