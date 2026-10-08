from __future__ import annotations

from invoiceiq.fraud import FraudScanner
from invoiceiq.models import Invoice


def _inv(**kw) -> Invoice:
    base = dict(vendor="Acme", invoice_number="INV-1", issue_date="2026-02-03", total_cents=10000)
    base.update(kw)
    return Invoice(**base)


def _codes(flags):
    return {f.code for f in flags}


def test_duplicate_invoice_number_flagged_on_resubmission():
    scanner = FraudScanner()
    assert _codes(scanner.scan(_inv())) == set()  # first time: clean
    flags = scanner.scan(_inv())  # same vendor + number again
    assert "duplicate_invoice_number" in _codes(flags)


def test_possible_duplicate_payment_different_number():
    scanner = FraudScanner()
    scanner.scan(_inv(invoice_number="INV-1"))
    flags = scanner.scan(_inv(invoice_number="INV-2"))  # same vendor/amount/date
    assert "possible_duplicate_payment" in _codes(flags)


def test_over_approval_limit():
    scanner = FraudScanner(approval_limit_cents=500_000)
    flags = scanner.scan(_inv(invoice_number="BIG", total_cents=600_000))
    assert "over_approval_limit" in _codes(flags)


def test_unexpected_tax_rate():
    scanner = FraudScanner(expected_tax_rate=0.19, tax_rate_tolerance=0.03)
    flags = scanner.scan(
        _inv(invoice_number="TAX", subtotal_cents=500_000, tax_cents=25_000, total_cents=525_000)
    )
    assert "unexpected_tax_rate" in _codes(flags)


def test_normal_tax_rate_not_flagged():
    scanner = FraudScanner(expected_tax_rate=0.19, tax_rate_tolerance=0.03)
    flags = scanner.scan(
        _inv(invoice_number="OK", subtotal_cents=100_000, tax_cents=19_000, total_cents=119_000)
    )
    assert "unexpected_tax_rate" not in _codes(flags)
