VENV := $(PWD)/.venv

export PATH := $(VENV)/bin:$(PATH)

ifeq ($(filter undefine,$(value .FEATURES)),)
SHELL = env PATH="$(PATH)" /bin/bash
endif

.PHONY: build
build:
	@python3 -m build
	@twine check dist/*

.PHONY: .venv
.venv:
	@python3 -m venv $(VENV)
	@pip install --upgrade pip

.PHONY: install
install: .venv
	@pip install -r requirements.txt

.PHONY: lint
lint:
	@ruff check
	@ruff format --check

.PHONY: format
format:
	@ruff check --select I --fix
	@ruff format

.PHONY: test
test:
	@coverage run -m unittest -b

.PHONY: coverage
coverage: test
	@coverage report -m

.PHONY: clean
clean:
	@rm -rf .ruff_cache .coverage dist
	@find . -name __pycache__ | xargs rm -rf
