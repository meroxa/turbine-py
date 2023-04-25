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

.PHONY: core_proto
core_proto:
	python3 -m grpc_tools.protoc \
     --proto_path=$(CURDIR)/pkg/turbine/proto/ \
     --python_out=$(CURDIR)/pkg/turbine/src/turbine_app/proto_gen/  \
     --grpc_python_out=$(CURDIR)/pkg/turbine/src/turbine_app/proto_gen/ \
	 --pyi_out=$(CURDIR)/pkg/turbine/src/turbine_app/proto_gen/  \
     turbine.proto 

.PHONY: validate_proto
validate_proto:
	python3 -m grpc_tools.protoc \
     --proto_path=$(CURDIR)/pkg/turbine/proto/ \
     --python_out=$(CURDIR)/pkg/turbine/src/turbine_app/proto_gen/  \
     --grpc_python_out=$(CURDIR)/pkg/turbine/src/turbine_app/proto_gen/ \
	 --pyi_out=$(CURDIR)/pkg/turbine/src/turbine_app/proto_gen/  \
     validate.proto 


.PHONY: service_proto
service_proto:
	python3 -m grpc_tools.protoc  \
     --proto_path=$(CURDIR)/pkg/turbine/proto/ \
     --python_out=$(CURDIR)/pkg/turbine/src/function_app/proto_gen/  \
     --grpc_python_out=$(CURDIR)/pkg/turbine/src/function_app/proto_gen/ \
	 --pyi_out=$(CURDIR)/pkg/turbine/src/function_app/proto_gen/  \
     service.proto 


