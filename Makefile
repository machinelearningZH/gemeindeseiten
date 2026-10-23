.DEFAULT_GOAL := help
CONFIG ?= config.yaml

.PHONY: help sync check-links format lint test check

help:
	@echo "Targets: sync, check-links, format, lint, test, check"
	@echo "Override checker configuration: make check-links CONFIG=path/config.yaml"

sync:
	uv sync

check-links:
	uv run check-links --config "$(CONFIG)"

format:
	uv run ruff format .

lint:
	uv run ruff check .

test:
	uv run pytest

check: lint test
	uv run ruff format --check .
