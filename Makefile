SHELL=/bin/bash -o pipefail

install: requirements.txt
	pip install -r requirements.txt

install-dev: requirements-dev.txt funtime
	pip install -r requirements-dev.txt

funtime: ./src/turbine/function_deploy/function_app/requirements.txt
	pip install -r ./src/turbine/function_deploy/function_app/requirements.txt

run-hooks:
	pre-commit run --all-files

install-hooks:
	pre-commit install

test:
	tox

.PHONY: lint
lint:
	black src
	flake8 src
