# ADR 0001 — Represent and compare money as integer cents

## Status
Accepted.

## Context
Invoice validation is arithmetic: line totals, subtotals, taxes. Floating-point
money cannot represent most decimals exactly, so a float-based validator would
raise false mismatches (or miss real ones) from accumulated rounding error.

## Decision
Parse every money value to an `int` number of cents at extraction, and do all
validation in cents with an explicit rounding tolerance (`IQ_ARITHMETIC_TOLERANCE_CENTS`,
default 2) to absorb legitimate per-line rounding.

## Consequences
- Checks are exact; a real mismatch is a real mismatch.
- The tolerance is a single, documented dial rather than scattered epsilons.
- Sub-cent currencies are out of scope; they would need a different scale.
