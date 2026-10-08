from __future__ import annotations

from invoiceiq.models import Invoice, LineItem, Severity
from invoiceiq.validate import validate_invoice


def _codes(issues):
    return {i.code for i in issues}


def test_clean_invoice_has_no_errors():
    inv = Invoice(
        vendor="Acme",
        invoice_number="INV-1",
        issue_date="2026-02-03",
        due_date="2026-03-05",
        line_items=[
            LineItem("chairs", 4, 12000, 48000),
            LineItem("desk", 1, 35000, 35000),
        ],
        subtotal_cents=83000,
        tax_cents=15770,
        total_cents=98770,
    )
    issues = validate_invoice(inv)
    assert not any(i.severity is Severity.ERROR for i in issues)


def test_line_amount_mismatch_is_error():
    inv = Invoice(
        line_items=[LineItem("widget", 3, 1000, 9999)],
        subtotal_cents=9999,
        tax_cents=0,
        total_cents=9999,
    )
    assert "line_amount_mismatch" in _codes(validate_invoice(inv))


def test_total_mismatch_is_error():
    inv = Invoice(
        line_items=[LineItem("x", 1, 57000, 57000)],
        subtotal_cents=57000,
        tax_cents=10830,
        total_cents=70000,  # should be 67830
    )
    codes = _codes(validate_invoice(inv))
    assert "total_mismatch" in codes


def test_subtotal_mismatch_is_error():
    inv = Invoice(
        line_items=[LineItem("a", 1, 100, 100), LineItem("b", 1, 100, 100)],
        subtotal_cents=500,  # should be 200
        tax_cents=0,
        total_cents=500,
    )
    assert "subtotal_mismatch" in _codes(validate_invoice(inv))


def test_rounding_tolerance_allows_small_differences():
    # Per-line rounding can make the sum differ by a cent or two; that is not an error.
    inv = Invoice(
        line_items=[LineItem("a", 3, 333, 1000)],  # 3*333=999, stated 1000
        subtotal_cents=1000,
        tax_cents=0,
        total_cents=1000,
    )
    assert not any(i.severity is Severity.ERROR for i in validate_invoice(inv, tolerance_cents=2))


def test_missing_total_and_due_before_issue():
    inv = Invoice(issue_date="2026-03-10", due_date="2026-03-01")
    codes = _codes(validate_invoice(inv))
    assert "missing_total" in codes
    assert "due_before_issue" in codes
