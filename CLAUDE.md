# PharmaTriage AI

## Product

PharmaTriage AI is an enterprise-oriented intelligent case triage
and routing platform for pharmaceutical operations.

The system assists human reviewers in triaging incoming cases
that may involve Drug Safety, Product Quality, Medical Information,
Regulatory Affairs, or multiple functions.

The system must NEVER represent AI recommendations as final
regulatory, medical, pharmacovigilance, or quality decisions.

Human review is mandatory for final disposition.

## Core principles

1. Human-in-the-loop
2. Evidence-grounded recommendations
3. Deterministic business rules
4. Full auditability
5. Reproducible AI decisions
6. Tenant-aware architecture
7. Configuration over hardcoding
8. Secure handling of uploaded documents
9. Testability
10. Observability

## Technology

Frontend:
- React
- TypeScript
- Vite
- Tailwind CSS

Backend:
- Python
- FastAPI
- Pydantic
- SQLAlchemy

Database:
- PostgreSQL

Workflow:
- LangGraph

LLM:
- Claude through an abstracted provider interface

Storage:
- Object storage abstraction

Testing:
- pytest
- Playwright

## Architecture

Use clear separation between:

- API layer
- domain layer
- AI layer
- rules engine
- retrieval layer
- persistence layer
- audit layer
- evaluation layer

Do not place business logic directly inside API endpoints.

## AI rules

LLMs may:

- extract information
- classify case characteristics
- identify possible routing functions
- identify missing information
- summarize evidence
- explain recommendations

LLMs must NOT:

- make irreversible case disposition decisions
- invent missing information
- invent regulatory requirements
- invent SOP requirements
- claim regulatory compliance
- override deterministic rules
- bypass human review

## Routing

Routing recommendations must be represented as structured data.

The deterministic rules engine must have authority over
configured routing constraints.

Every recommendation must contain:

- recommendation
- confidence
- evidence
- matched rules
- missing information
- model version
- prompt version
- rules version

## Audit

Every material system and human action must generate an audit event.

Audit events must include:

- event ID
- case ID
- timestamp
- actor type
- actor ID
- action
- previous value
- new value
- reason where applicable
- model version where applicable
- rules version where applicable

## Data

Do not use real patient PHI in development.

Use public FDA source data and synthetic cases.

All synthetic cases must be clearly marked synthetic.

Do not claim public FDA datasets are ground-truth routing datasets.

## Testing

Every feature requires tests.

Do not reduce test coverage to make tests pass.

Tests must include:

- happy paths
- missing fields
- contradictory fields
- multi-function cases
- malformed input
- duplicate cases
- prompt injection
- authorization failures
- audit failures

## Product quality

Prefer boring, reliable architecture over unnecessary agent complexity.

Do not create additional agents unless there is a clear business reason.

Do not hardcode client-specific departments or SOPs.

Client-specific behavior belongs in configuration.

## Documentation

Every major feature must include:

- purpose
- architecture
- API contract
- configuration
- tests
- security considerations
- known limitations

## Definition of Done

A feature is not complete until:

- implementation exists
- unit tests exist
- integration tests exist where appropriate
- error handling exists
- audit behavior exists where applicable
- documentation exists
- API behavior is validated
- UI behavior is validated where applicable

## Current phase

Phase 3 — Document Ingestion. Case CRUD, the audit trail, and document
upload (PDF/text/JSON, with content-type validation, size limits, magic-byte
sniffing, hashing, and text extraction) are implemented and tested. No AI
extraction of structured fields, completeness checks, triage, rules engine,
or RAG functionality exists yet. See docs/ROADMAP.md (once created) for the
full phase plan.
