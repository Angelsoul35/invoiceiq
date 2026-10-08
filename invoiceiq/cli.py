"""Command-line demo and entry point."""

from __future__ import annotations

import sys

from .models import InvoiceAssessment
from .service import InvoiceService

CLEAN = """
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

# Same layout, but the stated total does not equal subtotal + tax.
BAD_MATH = """
Vendor: Beacon Hardware Inc
Invoice Number: INV-2026-0100
Issue Date: 2026-02-10
Due Date: 2026-03-10

- Laptop docking station: 3 x 150.00 = 450.00
- USB-C cables: 10 x 12.00 = 120.00

Subtotal: 570.00
Tax (19%): 108.30
Total: 700.00
"""

# A large consulting invoice: over the approval limit and an odd tax rate.
BIG = """
Vendor: Northwind Consulting
Invoice Number: NC-9931
Issue Date: 2026-02-14
Due Date: 2026-03-16

- Advisory consulting services: 50 x 100.00 = 5000.00

Subtotal: 5000.00
Tax: 250.00
Total: 5250.00
"""


def _print(label: str, a: InvoiceAssessment) -> None:
    inv = a.invoice
    total = f"{inv.total_cents / 100:.2f}" if inv.total_cents is not None else "?"
    print(f"\n{label}")
    print(f"   vendor={inv.vendor}  number={inv.invoice_number}  total={total} {inv.currency}")
    print(
        f"   category={a.category} (p={a.category_confidence:.2f}"
        f"{', REVIEW' if a.category_needs_review else ''})"
        f"   valid={a.is_valid}  risk={a.risk_level}"
    )
    for i in a.issues:
        print(f"     issue [{i.severity}] {i.code}: {i.message}")
    for f in a.flags:
        print(f"     flag  [{f.severity}] {f.code}: {f.message}")


def demo() -> None:
    svc = InvoiceService()
    print("InvoiceIQ demo\n" + "=" * 60)
    _print("1) A clean invoice:", svc.assess(CLEAN))
    _print("2) An invoice whose total does not add up:", svc.assess(BAD_MATH))
    _print("3) The clean invoice submitted a second time (duplicate):", svc.assess(CLEAN))
    _print("4) A large consulting invoice (approval limit + odd tax rate):", svc.assess(BIG))
    print("\nNote: extraction + arithmetic validation are deterministic and auditable;")
    print("the AI only suggests the expense category and routes low confidence to review.")


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "demo":
        demo()
        return 0
    print("usage: python -m invoiceiq.cli demo")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
