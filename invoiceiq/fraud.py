"""Deterministic fraud and anomaly signals for an invoice.

These are not a fraud *verdict*; they are explainable signals that route an
invoice to a reviewer. The scanner keeps a small history so it can catch the most
common accounts-payable fraud — the **duplicate invoice** (the same bill paid
twice, by resubmission or a changed number) — alongside stateless heuristics
(an unusual tax rate, an amount over the approval limit).
"""

from __future__ import annotations

from .models import Finding, Invoice, Severity


class FraudScanner:
    def __init__(
        self,
        *,
        approval_limit_cents: int = 500_000,
        expected_tax_rate: float = 0.19,
        tax_rate_tolerance: float = 0.03,
    ) -> None:
        self.approval_limit_cents = approval_limit_cents
        self.expected_tax_rate = expected_tax_rate
        self.tax_rate_tolerance = tax_rate_tolerance
        self._seen_numbers: set[tuple[str, str]] = set()
        self._seen_fingerprints: set[tuple[str, int, str]] = set()

    def _fingerprint(self, invoice: Invoice) -> tuple[str, int, str]:
        return (
            (invoice.vendor or "").strip().lower(),
            invoice.total_cents or 0,
            invoice.issue_date or "",
        )

    def scan(self, invoice: Invoice, *, remember: bool = True) -> list[Finding]:
        flags: list[Finding] = []
        vendor = (invoice.vendor or "").strip().lower()

        # --- duplicate by (vendor, invoice number): the same bill resubmitted ---
        if invoice.invoice_number is not None:
            key = (vendor, invoice.invoice_number.strip().lower())
            if key in self._seen_numbers:
                flags.append(
                    Finding(
                        code="duplicate_invoice_number",
                        severity=Severity.ERROR,
                        message=(
                            f"invoice {invoice.invoice_number} from {invoice.vendor} "
                            "was already submitted"
                        ),
                    )
                )

        # --- near-duplicate: same vendor, amount and date under a different number ---
        fp = self._fingerprint(invoice)
        if invoice.total_cents and fp in self._seen_fingerprints:
            flags.append(
                Finding(
                    code="possible_duplicate_payment",
                    severity=Severity.WARNING,
                    message=(
                        f"an invoice from {invoice.vendor} for "
                        f"{(invoice.total_cents or 0) / 100:.2f} on {invoice.issue_date} "
                        "was already seen (possible resubmission)"
                    ),
                )
            )

        # --- over the approval limit ---
        if invoice.total_cents is not None and invoice.total_cents >= self.approval_limit_cents:
            flags.append(
                Finding(
                    code="over_approval_limit",
                    severity=Severity.WARNING,
                    message=(
                        f"total {invoice.total_cents / 100:.2f} is at or above the approval "
                        f"limit {self.approval_limit_cents / 100:.2f}"
                    ),
                )
            )

        # --- implied tax rate far from expected ---
        if invoice.subtotal_cents and invoice.tax_cents is not None and invoice.subtotal_cents > 0:
            rate = invoice.tax_cents / invoice.subtotal_cents
            if abs(rate - self.expected_tax_rate) > self.tax_rate_tolerance:
                flags.append(
                    Finding(
                        code="unexpected_tax_rate",
                        severity=Severity.WARNING,
                        message=(
                            f"implied tax rate {rate:.1%} differs from the expected "
                            f"{self.expected_tax_rate:.1%}"
                        ),
                    )
                )

        if remember:
            self.remember(invoice)
        return flags

    def remember(self, invoice: Invoice) -> None:
        vendor = (invoice.vendor or "").strip().lower()
        if invoice.invoice_number is not None:
            self._seen_numbers.add((vendor, invoice.invoice_number.strip().lower()))
        if invoice.total_cents:
            self._seen_fingerprints.add(self._fingerprint(invoice))
