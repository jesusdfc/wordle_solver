# Palabra Solver

Optimal entropy-based assistant for **La Palabra del Día** (Spanish Wordle).

- **Play** — mark gray / yellow / green feedback from your real game and get the next best guess.
- **Benchmark** — enter a secret word and watch the solver play it out.

## Stack

| Part | Tech |
|------|------|
| Solver | Python (`wordle-solver` package) |
| API | FastAPI |
| UI | React + Vite |

## Run locally

**Quick start (Git Bash on Windows):**

```bash
./init.sh
```

Opens the app at `http://127.0.0.1:5173` and prints LAN URLs for devices on the same Wi‑Fi.

**Manual:**

```bash
# Solver tests
make test

# Backend (port 9000)
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 9000

# Frontend (port 5173, proxies /api → backend)
cd frontend && npm install && npm run dev
```

**CLI solver:**

```bash
cd solver && uv sync
uv run palabra suggest --guess audio02201
uv run palabra solve abril
```

### First run / caches

On first use the solver builds cached files under `data/`:

- `words_5.pickle` — normalized word list
- `word_5_dict.pickle` — pattern lookup matrix (~25 MB, ~45 s to build once)

These are gitignored and regenerated automatically.

## Dictionary

Word list: [`lemario-general-del-espanol.txt`](https://github.com/olea/lemarios/blob/master/lemario-general-del-espanol.txt) from [olea/lemarios](https://github.com/olea/lemarios) (public domain).

Bundled copy: `data/lemario-general-del-espanol.txt`.

## Deploy

The UI and API are split: **Netlify** serves the static frontend; the **Python API** must run elsewhere (e.g. [Render](https://render.com)).

### 1. API (Render)

1. Push this repo to GitHub.
2. [Render](https://render.com) → **New Blueprint** → connect the repo (uses [`render.yaml`](render.yaml)).
3. Set **`CORS_ORIGINS`** to your Netlify URL, e.g. `https://your-app.netlify.app`.
4. Note the API URL, e.g. `https://palabra-api.onrender.com`.

The build step pre-warms the pattern cache so the first request is fast.

### 2. Frontend (Netlify)

1. Netlify → **Add new site** → Import from Git.
2. Build settings are read from [`netlify.toml`](netlify.toml).
3. Set environment variable:
   - **`VITE_API_URL`** = your Render API origin (no trailing slash), e.g. `https://palabra-api.onrender.com`
4. Deploy.

Local dev leaves `VITE_API_URL` empty; Vite proxies `/api` to `127.0.0.1:9000`.

### Environment variables

| Variable | Where | Purpose |
|----------|--------|---------|
| `VITE_API_URL` | Netlify | Production API base URL |
| `CORS_ORIGINS` | Render / backend | Comma-separated allowed browser origins |

See [`frontend/.env.example`](frontend/.env.example) and [`backend/.env.example`](backend/.env.example).

## License

MIT — see [LICENSE](LICENSE).

Word list data from [olea/lemarios](https://github.com/olea/lemarios) (public domain), not covered by MIT.
