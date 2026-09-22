.PHONY: test test-unit test-integration check

test-unit:
	uv run pytest -m "not integration"

test-integration:
	uv run pytest -m integration

test:
	uv run pytest

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy
	uv run pytest -m "not integration"
