.PHONY: checks

checks:
	uv run ruff format
	uv run ruff check . --fix
