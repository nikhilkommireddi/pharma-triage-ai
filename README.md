# PharmaTriage AI

AI-assisted case triage and routing platform for pharmaceutical operations
(Drug Safety, Product Quality, Medical Information, Regulatory Affairs).

See [CLAUDE.md](./CLAUDE.md) for product principles and engineering rules.

**Status: Phase 4 (AI extraction).** Case CRUD, the audit trail, document
ingestion, and AI-assisted structured-field extraction exist. No
completeness checks, deterministic rules engine, triage, RAG, or human
review exist yet.

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

- `POST /cases/{id}/documents/{document_id}/extractions` — run AI
  extraction on a document's extracted text (requires `ANTHROPIC_API_KEY`;
  422 if the document has no extracted text). Returns structured fields
  (product/patient/event/reporter/signals) plus source-text evidence for
  each populated field; fields the text doesn't state come back `null`,
  never guessed. Each run is stored as a new, immutable, versioned record
  (model, prompt version, timestamp) — nothing is ever overwritten.
- `GET /cases/{id}/documents/{document_id}/extractions` — list all
  extraction runs for a document

Extraction is advisory input for a human reviewer, not a routing or
disposition decision — see [CLAUDE.md](./CLAUDE.md).

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

Extraction quality (requires a real `ANTHROPIC_API_KEY`; not part of the
above — calls a real model and costs money):

```bash
export ANTHROPIC_API_KEY=sk-...
cd backend
python ../evaluation/run_extraction_eval.py
```

## Project layout

```
backend/     FastAPI app, SQLAlchemy models, Alembic migrations
frontend/    React + TypeScript + Vite app
prompts/     Versioned, git-tracked LLM prompts (e.g. extraction_v1.txt)
evaluation/  Extraction-quality evaluation harness and dataset
```

Additional directories (`rules/`, `knowledge/`, `docs/`) will be added in
later phases as those features are implemented.
