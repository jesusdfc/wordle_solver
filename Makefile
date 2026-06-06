.PHONY: checks test backend frontend benchmark

checks:
	cd solver && uv sync --all-extras --quiet
	cd solver && uv run ruff format .
	cd solver && uv run ruff check . --fix

test:
	cd solver && uv run pytest -q

backend:
	cd backend && uv run uvicorn app.main:app --reload --port 9000

frontend:
	cd frontend && npm run dev

benchmark:
	cd solver && uv sync --extra benchmark --quiet
	cd solver && uv run palabra benchmark
