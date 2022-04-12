SHELL=/bin/bash -o pipefail

setup: requirements.txt
	pip install -r requirements.txt

setup-dev: requirements-dev.txt
	pip install -r requirements_dev.txt

funtime: ./src/turbine/function-deploy/function-app/requirements.txt
	pip install -r ./src/turbine/function-deploy/function-app/requirements.txt