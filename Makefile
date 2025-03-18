SHELL := /bin/bash

PYTHON=python
PIP=pip
SRC_DIR=src
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

# Install development dependencies if specified (example)
.PHONY: install-dev
install-dev:
	$(PIP) install -r requirements.txt -r requirements-dev.txt

# Run the main script
.PHONY: run
run:
	$(PYTHON) $(SRC_DIR)/dotchatbot/cli.py

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
	$(PIP) install pytest
	pytest tests/

# Lint the code (example using flake8)
.PHONY: lint
lint:
	$(PIP) install flake8
	flake8 $(SRC_DIR)

# Setup a virtual environment (if needed)
.PHONY: venv
venv:
	python3 -m venv venv
	source venv/bin/activate && $(PIP) install --upgrade pip
