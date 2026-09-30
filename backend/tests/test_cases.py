from uuid import uuid4


def test_create_case_returns_defaults(client):
    response = client.post("/cases", json={})
    assert response.status_code == 201
    body = response.json()
    assert body["case_number"].startswith("CASE-")
    assert body["status"] == "OPEN"
    assert body["product"] == {
        "name": None,
        "strength": None,
        "dosage_form": None,
        "lot_number": None,
        "expiration_date": None,
    }


def test_create_case_with_structured_fields(client):
    payload = {
        "product": {"name": "Acme Tablet 50mg", "lot_number": "ABC123"},
        "event": {"description": "Patient experienced nausea"},
        "reporter": {"organization": "City Pharmacy", "contact_available": True},
    }
    response = client.post("/cases", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["product"]["lot_number"] == "ABC123"
    assert body["event"]["description"] == "Patient experienced nausea"
    assert body["reporter"]["contact_available"] is True


def test_get_case_not_found(client):
    response = client.get(f"/cases/{uuid4()}")
    assert response.status_code == 404


def test_get_case_invalid_uuid_returns_422(client):
    response = client.get("/cases/not-a-uuid")
    assert response.status_code == 422


def test_create_case_generates_audit_event(client):
    case = client.post("/cases", json={}).json()

    audit_events = client.get(f"/cases/{case['id']}/audit").json()
    assert len(audit_events) == 1
    assert audit_events[0]["action"] == "CASE_CREATED"
    assert audit_events[0]["actor_type"] == "HUMAN"
    assert audit_events[0]["new_value"]["source"] is not None


def test_audit_for_missing_case_returns_404(client):
    response = client.get(f"/cases/{uuid4()}/audit")
    assert response.status_code == 404


def test_update_case_status_records_audit_with_reason(client):
    case = client.post("/cases", json={}).json()

    response = client.patch(
        f"/cases/{case['id']}",
        json={"status": "CLOSED", "reason": "Investigation complete"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CLOSED"

    audit_events = client.get(f"/cases/{case['id']}/audit").json()
    status_event = next(e for e in audit_events if e["action"] == "CASE_STATUS_CHANGED")
    assert status_event["previous_value"] == {"status": "OPEN"}
    assert status_event["new_value"] == {"status": "CLOSED"}
    assert status_event["reason"] == "Investigation complete"


def test_update_case_invalid_status_returns_422(client):
    case = client.post("/cases", json={}).json()
    response = client.patch(f"/cases/{case['id']}", json={"status": "NOT_REAL"})
    assert response.status_code == 422


def test_update_case_field_tracks_previous_and_new_value(client):
    case = client.post("/cases", json={"product": {"lot_number": "OLD123"}}).json()

    client.patch(
        f"/cases/{case['id']}",
        json={"product": {"lot_number": "NEW456"}, "reason": "Correction from reporter"},
    )

    audit_events = client.get(f"/cases/{case['id']}/audit").json()
    product_event = next(e for e in audit_events if e["action"] == "CASE_PRODUCT_UPDATED")
    assert product_event["previous_value"]["lot_number"] == "OLD123"
    assert product_event["new_value"]["lot_number"] == "NEW456"
    assert product_event["reason"] == "Correction from reporter"


def test_update_case_with_unchanged_field_does_not_add_audit_event(client):
    case = client.post("/cases", json={"product": {"lot_number": "ABC123"}}).json()

    client.patch(f"/cases/{case['id']}", json={"product": {"lot_number": "ABC123"}})

    audit_events = client.get(f"/cases/{case['id']}/audit").json()
    assert len(audit_events) == 1  # only CASE_CREATED


def test_list_cases_returns_created_cases(client):
    client.post("/cases", json={})
    client.post("/cases", json={})

    response = client.get("/cases")
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_list_cases_respects_limit(client):
    for _ in range(3):
        client.post("/cases", json={})

    response = client.get("/cases", params={"limit": 1})
    assert response.status_code == 200
    assert len(response.json()) == 1
