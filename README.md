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

On first use the solver builds cached files (gitignored, regenerated automatically):

- `words_5.pickle` — normalized word list
- `word_5_dict.pickle` — pattern lookup matrix (~25 MB, ~45 s to build once)

By default these live under `data/`. On Railway, set `WORDLE_CACHE_DIR=/app/data/cache` with a volume mounted there.

## Dictionary

Word list: [`lemario-general-del-espanol.txt`](https://github.com/olea/lemarios/blob/master/lemario-general-del-espanol.txt) from [olea/lemarios](https://github.com/olea/lemarios) (public domain).

Bundled copy: `data/lemario-general-del-espanol.txt`.

## Deploy (Railway)

One service serves the React UI and `/api/*` from the same URL (see `backend/app/main.py` static mount).

### Railway

1. Push this repo to GitHub.
2. [Railway](https://railway.app) → **New Project** → **Deploy from GitHub** → select the repo.
3. Railway reads [`railway.toml`](railway.toml) and [`nixpacks.toml`](nixpacks.toml).
4. **Volume (recommended):** Service → **Volumes** → mount at **`/app/data/cache`**  
   Set env **`WORDLE_CACHE_DIR=/app/data/cache`**.  
   Persists pickles across deploys; lemario stays in the image at `data/lemario-general-del-espanol.txt`.
5. **Environment variables** (optional):

   | Variable | Value |
   |----------|--------|
   | `WORDLE_CACHE_DIR` | `/app/data/cache` (when using a volume) |
   | `CORS_ORIGINS` | Leave empty unless you need extra allowed origins |

6. Deploy. Open the generated public URL (e.g. `https://wordle-solver-production.up.railway.app`).
7. Verify: `/api/health` → `{"status":"ok"}`, `/` → app menu.

**Cost:** Railway Hobby plan (~$5/month) for always-on + volume.

- **Build:** `scripts/railway-build.sh` — npm build, copy to `backend/static`, `uv sync`
- **Start:** `scripts/railway-start.sh` — warm pickle cache, then uvicorn

### Environment variables

| Variable | Where | Purpose |
|----------|--------|---------|
| `WORDLE_CACHE_DIR` | Railway | Pickle cache directory on a mounted volume |
| `CORS_ORIGINS` | Railway / local backend | Extra allowed browser origins (comma-separated) |
| `VITE_API_URL` | Local frontend only | Leave empty; Vite proxies `/api` to port 9000 |

See [`backend/.env.example`](backend/.env.example). Local frontend dev does not need a `.env` file.

## License

MIT — see [LICENSE](LICENSE).

Word list data from [olea/lemarios](https://github.com/olea/lemarios) (public domain), not covered by MIT.
