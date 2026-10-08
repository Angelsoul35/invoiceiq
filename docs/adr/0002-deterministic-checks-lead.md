# ADR 0002 — Deterministic checks lead; ML only suggests the category

## Status
Accepted.

## Context
"AI invoice processing" often means a model that outputs fields and a category
with no guarantee the numbers are consistent. For accounts payable the costly
errors (total mismatch, duplicate payment, over-limit spend) are matters of fact
that must be *caught*, not *predicted*.

## Decision
Validation and fraud detection are deterministic, rule-based and explained. The
only machine-learning component is the expense-category suggestion, and it (a)
routes low confidence to a human and (b) has no effect on `is_valid` or the fraud
flags.

## Consequences
- The trustworthy outputs do not depend on a model's mood or training data.
- A model error can mis-*suggest* a category but can never pass a bad total or
  hide a duplicate.
- Each issue and flag carries a stable machine code and a human-readable message,
  so the system is auditable and easy to integrate with a review queue.
