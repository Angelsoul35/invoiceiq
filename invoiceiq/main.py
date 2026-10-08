"""FastAPI surface over the invoice service."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .models import InvoiceAssessment
from .service import InvoiceService

app = FastAPI(title="InvoiceIQ", version="1.0.0")
_service: InvoiceService | None = None


def service() -> InvoiceService:
    global _service
    if _service is None:
        _service = InvoiceService()
    return _service


class InvoiceRequest(BaseModel):
    text: str = Field(min_length=1)
    remember: bool = True


def _assessment_dict(a: InvoiceAssessment) -> dict:
    inv = a.invoice
    return {
        "invoice": {
            "vendor": inv.vendor,
            "invoice_number": inv.invoice_number,
            "issue_date": inv.issue_date,
            "due_date": inv.due_date,
            "currency": inv.currency,
            "line_items": [
                {
                    "description": it.description,
                    "quantity": it.quantity,
                    "unit_price_cents": it.unit_price_cents,
                    "amount_cents": it.amount_cents,
                }
                for it in inv.line_items
            ],
            "subtotal_cents": inv.subtotal_cents,
            "tax_cents": inv.tax_cents,
            "total_cents": inv.total_cents,
        },
        "is_valid": a.is_valid,
        "risk_level": a.risk_level,
        "issues": [
            {"code": i.code, "severity": i.severity, "message": i.message} for i in a.issues
        ],
        "flags": [{"code": f.code, "severity": f.severity, "message": f.message} for f in a.flags],
        "category": a.category,
        "category_confidence": round(a.category_confidence, 4),
        "category_needs_review": a.category_needs_review,
    }


@app.post("/invoice/assess")
def assess(req: InvoiceRequest) -> dict:
    return _assessment_dict(service().assess(req.text, remember=req.remember))
