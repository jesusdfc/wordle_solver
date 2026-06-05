# palabra-solver

Optimal theoretical player for [**La Palabra del Día**](https://lapalabradeldia.com/) (Spanish Wordle). Monorepo with a Python solver, FastAPI backend, and React frontend for live play.

## Structure

```
Wordle/
├── data/lemario-general-del-espanol.txt
├── solver/          # Python package (`from solver.agent import ...`)
├── backend/         # FastAPI API
├── frontend/        # React + Vite UI
└── Makefile
```

See [`solver/diagram.mmd`](solver/diagram.mmd) for the architecture diagram.

## Setup

### Solver

```bash
cd solver
uv sync --all-extras
uv run pytest
uv run palabra stats
uv run palabra suggest
```

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies `/api` to the backend.

Or from the repo root:

```bash
make test
make backend    # terminal 1
make frontend   # terminal 2
```

## Live play (web)

1. Click **Suggest** for the optimal first guess.
2. Type the word you played and click each tile to cycle gray → yellow → green.
3. Click **Confirm row** to lock in feedback and get the next suggestion.
4. Repeat until solved.

## CLI (offline)

```bash
cd solver
uv run palabra solve abril
uv run palabra suggest --guess audio02201
```

Pattern digits: `0` gray, `1` yellow, `2` green (left to right).

## API

```http
POST /api/suggest
Content-Type: application/json

{
  "history": [
    { "word": "cario", "pattern": [2, 0, 2, 0, 1] }
  ],
  "strategy": "entropy",
  "length": 5
}
```

## Modules (solver)

| Module | Class | Role |
|--------|-------|------|
| `data.py` | `WordleWordsHandler` | Dictionary / action space |
| `env.py` | `WordleEnv` | POMDP environment |
| `belief.py` | `BeliefState` | Belief over secrets |
| `model.py` | `WordleModel` | Scoring / inference |
| `agent.py` | `WordleAgent` | Actor |
