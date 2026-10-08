"""Arithmetic and structural validation of an extracted invoice.

This is the part an accounts-payable team actually trusts: it does not guess, it
*checks*. Every rule is deterministic and explains itself, and amounts are
compared in integer cents with a small rounding tolerance so legitimate per-line
rounding does not raise a false error.
"""

from __future__ import annotations

from .models import Finding, Invoice, Severity


def _approx(a: int, b: int, tol: int) -> bool:
    return abs(a - b) <= tol


def validate_invoice(invoice: Invoice, *, tolerance_cents: int = 2) -> list[Finding]:
    issues: list[Finding] = []

    # --- line-level arithmetic: quantity * unit price == amount ---
    for i, item in enumerate(invoice.line_items, start=1):
        expected = round(item.quantity * item.unit_price_cents)
        if not _approx(expected, item.amount_cents, tolerance_cents):
            issues.append(
                Finding(
                    code="line_amount_mismatch",
                    severity=Severity.ERROR,
                    message=(
                        f"line {i} ({item.description!r}): {item.quantity} x "
                        f"{item.unit_price_cents / 100:.2f} = {expected / 100:.2f}, "
                        f"but amount is {item.amount_cents / 100:.2f}"
                    ),
                )
            )
        if item.amount_cents < 0 or item.unit_price_cents < 0 or item.quantity < 0:
            issues.append(
                Finding("negative_value", Severity.WARNING, f"line {i} has a negative value")
            )

    # --- subtotal == sum of line amounts ---
    if invoice.line_items and invoice.subtotal_cents is not None:
        line_sum = sum(it.amount_cents for it in invoice.line_items)
        if not _approx(line_sum, invoice.subtotal_cents, tolerance_cents):
            issues.append(
                Finding(
                    code="subtotal_mismatch",
                    severity=Severity.ERROR,
                    message=(
                        f"line items sum to {line_sum / 100:.2f}, "
                        f"but subtotal is {invoice.subtotal_cents / 100:.2f}"
                    ),
                )
            )

    # --- subtotal + tax == total ---
    if (
        invoice.subtotal_cents is not None
        and invoice.tax_cents is not None
        and invoice.total_cents is not None
    ):
        expected_total = invoice.subtotal_cents + invoice.tax_cents
        if not _approx(expected_total, invoice.total_cents, tolerance_cents):
            issues.append(
                Finding(
                    code="total_mismatch",
                    severity=Severity.ERROR,
                    message=(
                        f"subtotal {invoice.subtotal_cents / 100:.2f} + tax "
                        f"{invoice.tax_cents / 100:.2f} = {expected_total / 100:.2f}, "
                        f"but total is {invoice.total_cents / 100:.2f}"
                    ),
                )
            )

    # --- required fields ---
    if invoice.total_cents is None:
        issues.append(Finding("missing_total", Severity.ERROR, "no total amount found"))
    if invoice.invoice_number is None:
        issues.append(
            Finding("missing_invoice_number", Severity.WARNING, "no invoice number found")
        )
    if invoice.vendor is None:
        issues.append(Finding("missing_vendor", Severity.WARNING, "no vendor found"))

    # --- dates ---
    if invoice.issue_date and invoice.due_date and invoice.due_date < invoice.issue_date:
        issues.append(
            Finding(
                code="due_before_issue",
                severity=Severity.WARNING,
                message=f"due date {invoice.due_date} is before issue date {invoice.issue_date}",
            )
        )

    return issues
