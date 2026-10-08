from __future__ import annotations

import pytest

from invoiceiq.extract import extract_invoice, money_to_cents

SAMPLE = """
Vendor: Acme Office Supplies Ltd
Invoice Number: INV-2026-0042
Issue Date: 2026-02-03
Due Date: 2026-03-05

- Office chairs: 4 x 120.00 = 480.00
- Standing desk: 1 x 350.00 = 350.00

Subtotal: 830.00
Tax (19%): 157.70
Total: 987.70
"""


def test_money_to_cents():
    assert money_to_cents("1,234.56") == 123456
    assert money_to_cents("$350") == 35000
    assert money_to_cents("-20.00") == -2000
    with pytest.raises(ValueError):
        money_to_cents("n/a")


def test_extract_header_fields():
    inv = extract_invoice(SAMPLE)
    assert inv.vendor == "Acme Office Supplies Ltd"
    assert inv.invoice_number == "INV-2026-0042"
    assert inv.issue_date == "2026-02-03"
    assert inv.due_date == "2026-03-05"


def test_extract_line_items_and_totals():
    inv = extract_invoice(SAMPLE)
    assert len(inv.line_items) == 2
    assert inv.line_items[0].description == "Office chairs"
    assert inv.line_items[0].quantity == 4
    assert inv.line_items[0].unit_price_cents == 12000
    assert inv.line_items[0].amount_cents == 48000
    assert inv.subtotal_cents == 83000
    assert inv.tax_cents == 15770
    # "Total" must not be captured from inside "Subtotal".
    assert inv.total_cents == 98770
