# PharmaTriage AI

AI-assisted case triage and routing platform for pharmaceutical operations
(Drug Safety, Product Quality, Medical Information, Regulatory Affairs).

See [CLAUDE.md](./CLAUDE.md) for product principles and engineering rules.

**Status: Phase 3 (document ingestion).** Case CRUD, the audit trail, and
document upload/extraction exist. No AI extraction of structured fields,
completeness checks, triage, rules-engine, or RAG functionality exists yet.

## API (current)

- `POST /cases` — create a case (source/product/patient/event/reporter info)
- `GET /cases` — list cases (`limit`, `offset`)
- `GET /cases/{id}` — retrieve a case
- `PATCH /cases/{id}` — update structured fields and/or status; every
  changed field produces a separate audit event, and `status` changes
  require/record a `reason`
- `GET /cases/{id}/audit` — full audit trail for a case
- `POST /cases/{id}/documents` — upload a document (`text/plain`,
  `application/json`, or `application/pdf`; 10MB limit). Content is
  validated against its declared type before anything is persisted, hashed
  (SHA-256), stored, and text-extracted; extraction failures (e.g. a scanned
  PDF with no text layer) are recorded on the document rather than failing
  the request.
- `GET /cases/{id}/documents` — list documents attached to a case
- `GET /cases/{id}/documents/{document_id}` — retrieve a document's metadata
  and extracted text

Document content is always treated as untrusted data — it is stored and
returned verbatim, never interpreted as instructions.

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
