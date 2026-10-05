from uuid import uuid4


def _create_case_with_document(client, text: bytes = b"Patient experienced nausea after lot ABC123.") -> tuple[str, str]:
    case_id = client.post("/cases", json={}).json()["id"]
    document = client.post(
        f"/cases/{case_id}/documents",
        files={"file": ("note.txt", text, "text/plain")},
    ).json()
    return case_id, document["id"]


def test_create_extraction_returns_structured_data(client, fake_llm_provider):
    case_id, document_id = _create_case_with_document(client)

    response = client.post(f"/cases/{case_id}/documents/{document_id}/extractions")
    assert response.status_code == 201
    body = response.json()
    assert body["extracted_data"]["product"]["lot_number"] == "ABC123"
    assert body["extracted_data"]["signals"]["adverse_event_detected"] is True
    assert body["model_provider"] == "fake"
    assert body["model_version"] == "fake-v1"
    assert body["prompt_version"] == "extraction-v1"


def test_extraction_passes_document_text_to_provider(client, fake_llm_provider):
    case_id, document_id = _create_case_with_document(client, text=b"exact source text")
    client.post(f"/cases/{case_id}/documents/{document_id}/extractions")
    assert fake_llm_provider.calls == ["exact source text"]


def test_extraction_records_audit_event_with_ai_actor(client, fake_llm_provider):
    case_id, document_id = _create_case_with_document(client)
    client.post(f"/cases/{case_id}/documents/{document_id}/extractions")

    audit_events = client.get(f"/cases/{case_id}/audit").json()
    extraction_event = next(e for e in audit_events if e["action"] == "EXTRACTION_COMPLETED")
    assert extraction_event["actor_type"] == "AI"
    assert extraction_event["model_version"] == "fake-v1"


def test_extraction_without_extracted_text_returns_422(client, fake_llm_provider):
    case_id = client.post("/cases", json={}).json()["id"]
    # An empty-looking PDF with no text layer — document is stored but has
    # no extracted_text, so AI extraction has nothing to work from.
    from pypdf import PdfWriter
    import io

    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)

    document = client.post(
        f"/cases/{case_id}/documents",
        files={"file": ("scan.pdf", buf.getvalue(), "application/pdf")},
    ).json()
    assert document["extracted_text"] is None

    response = client.post(f"/cases/{case_id}/documents/{document['id']}/extractions")
    assert response.status_code == 422


def test_rerunning_extraction_creates_new_versioned_record(client, fake_llm_provider):
    case_id, document_id = _create_case_with_document(client)

    first = client.post(f"/cases/{case_id}/documents/{document_id}/extractions").json()
    second = client.post(f"/cases/{case_id}/documents/{document_id}/extractions").json()
    assert first["id"] != second["id"]

    extractions = client.get(f"/cases/{case_id}/documents/{document_id}/extractions").json()
    assert len(extractions) == 2


def test_extraction_for_missing_document_returns_404(client, fake_llm_provider):
    case_id = client.post("/cases", json={}).json()["id"]
    response = client.post(f"/cases/{case_id}/documents/{uuid4()}/extractions")
    assert response.status_code == 404


def test_extraction_never_invents_unset_fields(client, fake_llm_provider):
    """The fake provider's canned result leaves patient/reporter null — the
    pipeline must pass that through as null, not fill in placeholder data."""
    case_id, document_id = _create_case_with_document(client)
    response = client.post(f"/cases/{case_id}/documents/{document_id}/extractions")
    data = response.json()["extracted_data"]
    assert data["patient"]["age"] is None
    assert data["patient"]["sex"] is None
    assert data["reporter"]["name"] is None
