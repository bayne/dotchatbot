SHELL := /bin/bash

PYTHON=python
PIP=pip
PACKAGE_NAME=dotchatbot
ENTRY_COMMAND=dcb

# Default target
.PHONY: all
all: install

# Install dependencies in editable mode
.PHONY: install
install:
	$(PIP) install -e .

# Build the package using `build`
.PHONY: build
build:
	$(PYTHON) -m build

# Run the main script
.PHONY: run
run:
	$(PYTHON) dotchatbot/dcb.py

# Run the script via the entry point command
.PHONY: entry
entry:
	$(ENTRY_COMMAND)

# Clean build and dist directories
.PHONY: clean
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

# Run tests (example using pytest)
.PHONY: test
test:
	pytest tests/

# Lint the code (example using flake8)
.PHONY: lint
lint:
	flake8 .

# Use mypy to check type hints
.PHONY: check
check:
	mypy --namespace-packages --explicit-package-bases .

.PHONY: publish-test
publish-test:
	python -m twine upload --verbose --repository testpypi dist/*

.PHONY: publish
publish:
	python -m twine upload --verbose --repository pypi dist/*
