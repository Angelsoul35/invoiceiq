"""Deterministic field extraction from structured invoice text.

Real invoices arrive as PDFs or scans; a production system puts an OCR / layout
model in front of this step. What this module owns is the part that must be
*exact and auditable*: once the text is available, pull out the header fields,
the line items and the totals with explicit rules, so the numbers that feed
validation are traceable to the source text rather than hallucinated.

The parser targets a common labelled-text layout (see ``docs/architecture.md``):

    Vendor: Acme Supplies Ltd
    Invoice Number: INV-2026-0042
    Issue Date: 2026-02-03
    Due Date: 2026-03-05

    - Office chairs: 4 x 120.00 = 480.00
    - Standing desk: 1 x 350.00 = 350.00

    Subtotal: 830.00
    Tax (19%): 157.70
    Total: 987.70
"""

from __future__ import annotations

import re

from .models import Invoice, LineItem

_CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP"}

_MONEY = r"[-+]?\s*[$€£]?\s*[\d][\d,]*(?:\.\d{1,2})?"


def money_to_cents(text: str) -> int:
    """Parse a money string ('1,234.56', '$350', '-20.00') into integer cents."""
    cleaned = re.sub(r"[^\d.\-]", "", text.replace(",", ""))
    if cleaned in ("", "-", ".", "-."):
        raise ValueError(f"not a money value: {text!r}")
    return round(float(cleaned) * 100)


def _search(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def _detect_currency(text: str) -> str:
    for sym, code in _CURRENCY_SYMBOLS.items():
        if sym in text:
            return code
    m = re.search(r"\b(USD|EUR|GBP|COP|MXN)\b", text)
    return m.group(1) if m else "USD"


# "- Office chairs: 4 x 120.00 = 480.00"  (qty x unit = amount)
_LINE_ITEM = re.compile(
    r"^[\-*•]?\s*(?P<desc>.+?):\s*"
    r"(?P<qty>\d+(?:\.\d+)?)\s*[x×*]\s*"
    r"(?P<unit>" + _MONEY + r")\s*=\s*"
    r"(?P<amount>" + _MONEY + r")\s*$",
    re.IGNORECASE,
)


def _parse_line_items(text: str) -> list[LineItem]:
    items: list[LineItem] = []
    for line in text.splitlines():
        m = _LINE_ITEM.match(line.strip())
        if not m:
            continue
        items.append(
            LineItem(
                description=m.group("desc").strip(),
                quantity=float(m.group("qty")),
                unit_price_cents=money_to_cents(m.group("unit")),
                amount_cents=money_to_cents(m.group("amount")),
            )
        )
    return items


def _money_field(label_pattern: str, text: str) -> int | None:
    raw = _search(rf"{label_pattern}\s*[:]?\s*({_MONEY})", text)
    if raw is None:
        return None
    try:
        return money_to_cents(raw)
    except ValueError:
        return None


def extract_invoice(text: str) -> Invoice:
    """Parse labelled invoice text into a structured :class:`Invoice`."""
    return Invoice(
        vendor=_search(r"(?:vendor|supplier|bill\s*from|from)\s*[:]\s*(.+)", text),
        invoice_number=_search(r"invoice\s*(?:no\.?|number|#)\s*[:#]?\s*([A-Za-z0-9\-/]+)", text),
        issue_date=_search(r"(?:issue\s*date|invoice\s*date)\s*[:]\s*(\d{4}-\d{2}-\d{2})", text),
        due_date=_search(r"due\s*(?:date)?\s*[:]\s*(\d{4}-\d{2}-\d{2})", text),
        currency=_detect_currency(text),
        line_items=_parse_line_items(text),
        # Word boundaries matter: without \b, "total" would match inside "Subtotal".
        subtotal_cents=_money_field(r"\bsub\s*total\b", text),
        tax_cents=_money_field(r"\b(?:tax|vat|iva)\b(?:\s*\([^)]*\))?", text),
        total_cents=_money_field(r"\btotal\b(?:\s*due)?", text),
        raw_text=text,
    )
