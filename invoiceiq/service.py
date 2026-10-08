"""Application service: extract -> validate -> scan for fraud -> categorise."""

from __future__ import annotations

from .categorizer import ExpenseCategorizer
from .config import Settings, get_settings
from .extract import extract_invoice
from .fraud import FraudScanner
from .models import InvoiceAssessment
from .validate import validate_invoice


class InvoiceService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.categorizer = ExpenseCategorizer(
            min_confidence=self.settings.categoriser_min_confidence
        ).fit()
        self.scanner = FraudScanner(
            approval_limit_cents=self.settings.approval_limit_cents,
            expected_tax_rate=self.settings.expected_tax_rate,
            tax_rate_tolerance=self.settings.tax_rate_tolerance,
        )

    def assess(self, text: str, *, remember: bool = True) -> InvoiceAssessment:
        invoice = extract_invoice(text)
        issues = validate_invoice(invoice, tolerance_cents=self.settings.arithmetic_tolerance_cents)
        flags = self.scanner.scan(invoice, remember=remember)
        suggestion = self.categorizer.suggest(invoice)
        return InvoiceAssessment(
            invoice=invoice,
            issues=issues,
            flags=flags,
            category=suggestion.category,
            category_confidence=suggestion.confidence,
            category_needs_review=suggestion.needs_review,
        )
