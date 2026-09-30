# PharmaTriage AI

AI-assisted case triage and routing platform for pharmaceutical operations
(Drug Safety, Product Quality, Medical Information, Regulatory Affairs).

See [CLAUDE.md](./CLAUDE.md) for product principles and engineering rules.

**Status: Phase 1 (foundation) only.** No extraction, triage, rules-engine,
or RAG functionality exists yet.

## Running locally

### With Docker

```bash
docker compose up --build
```

- Backend: http://localhost:8000/health
- Frontend: http://localhost:5173

### Without Docker

Backend:

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Testing

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test
```

## Project layout

```
backend/   FastAPI app, SQLAlchemy models, Alembic migrations
frontend/  React + TypeScript + Vite app
```

Additional directories (`rules/`, `prompts/`, `knowledge/`, `evaluation/`,
`docs/`) will be added in later phases as those features are implemented.
