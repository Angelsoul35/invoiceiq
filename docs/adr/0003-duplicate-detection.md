# ADR 0003 — Catch duplicate invoices with two complementary keys

## Status
Accepted.

## Context
The single most common accounts-payable fraud (and the most common accidental
double payment) is paying the same invoice twice: a vendor resubmits the same
number, or resubmits the same bill under a new number.

## Decision
The `FraudScanner` keeps a short history and checks two keys:

- `(vendor, invoice_number)` — an exact resubmission → `duplicate_invoice_number`
  (error severity).
- `(vendor, total, issue_date)` — the same bill under a different number →
  `possible_duplicate_payment` (warning severity).

## Consequences
- Both the blatant and the disguised duplicate are caught, at different severities.
- It is in-memory and per-process here; production would back the history with a
  shared store so duplicates are caught across workers and over time.
- Normalisation is deliberately simple (lower-cased, trimmed); a production system
  would add fuzzy vendor matching to catch "Acme Ltd" vs "ACME Limited".
