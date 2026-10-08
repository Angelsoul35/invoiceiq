"""Typed data models shared across the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class LineItem:
    description: str
    quantity: float
    unit_price_cents: int
    amount_cents: int


@dataclass
class Invoice:
    vendor: str | None = None
    invoice_number: str | None = None
    issue_date: str | None = None  # ISO-8601 date
    due_date: str | None = None
    currency: str = "USD"
    line_items: list[LineItem] = field(default_factory=list)
    subtotal_cents: int | None = None
    tax_cents: int | None = None
    total_cents: int | None = None
    raw_text: str = ""


@dataclass
class Finding:
    """A validation issue or a fraud signal, with a stable machine-readable code."""

    code: str
    severity: Severity
    message: str


@dataclass
class InvoiceAssessment:
    invoice: Invoice
    issues: list[Finding] = field(default_factory=list)
    flags: list[Finding] = field(default_factory=list)
    category: str | None = None
    category_confidence: float = 0.0
    category_needs_review: bool = False

    @property
    def is_valid(self) -> bool:
        """True when no validation issue is an error (arithmetic adds up, dates sane)."""
        return not any(i.severity is Severity.ERROR for i in self.issues)

    @property
    def risk_level(self) -> str:
        sev = {f.severity for f in self.flags}
        if Severity.ERROR in sev:
            return "high"
        if Severity.WARNING in sev:
            return "medium"
        return "low"
