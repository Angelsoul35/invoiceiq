from __future__ import annotations

from fastapi.testclient import TestClient

from invoiceiq.cli import BAD_MATH, CLEAN
from invoiceiq.main import app
from invoiceiq.service import InvoiceService

client = TestClient(app)


def test_assess_clean_invoice_endpoint():
    r = client.post("/invoice/assess", json={"text": CLEAN, "remember": False})
    assert r.status_code == 200
    body = r.json()
    assert body["is_valid"] is True
    assert body["invoice"]["total_cents"] == 98770
    assert body["category"] == "office_supplies"


def test_assess_bad_math_endpoint():
    r = client.post("/invoice/assess", json={"text": BAD_MATH, "remember": False})
    body = r.json()
    assert body["is_valid"] is False
    assert any(i["code"] == "total_mismatch" for i in body["issues"])


def test_service_detects_duplicate_on_resubmission():
    svc = InvoiceService()
    first = svc.assess(CLEAN)
    assert all(f.code != "duplicate_invoice_number" for f in first.flags)
    second = svc.assess(CLEAN)
    assert any(f.code == "duplicate_invoice_number" for f in second.flags)


def test_empty_text_rejected():
    assert client.post("/invoice/assess", json={"text": ""}).status_code == 422
