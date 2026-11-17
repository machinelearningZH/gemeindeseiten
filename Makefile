.DEFAULT_GOAL := help
CONFIG ?= config.yaml

.PHONY: help sync build-site check-links format lint test check

help:
	@echo "Targets: sync, build-site, check-links, format, lint, test, check"
	@echo "Override checker configuration: make check-links CONFIG=path/config.yaml"

sync:
	uv sync

build-site:
	uv run build-site

check-links:
	uv run check-links --config "$(CONFIG)"

format:
	uv run ruff format .

lint:
	uv run ruff check .

test:
	uv run pytest
	node tests/test_search.cjs

check: lint test
	uv run ruff format --check .
