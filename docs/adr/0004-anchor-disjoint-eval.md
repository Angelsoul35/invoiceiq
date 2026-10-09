# ADR 0004 — Evaluate the categoriser on an anchor-disjoint split and real data

## Status
Accepted.

## Context
Trained and tested on the same synthetic templates, a categoriser reports a
meaningless ~1.0 accuracy because it memorises phrasings. That number would
misrepresent how it behaves on real, unseen invoice wording.

## Decision
`invoiceiq.evaluation` holds out **whole anchor keywords** from training (not just
surrounding phrasing), so test line items centre on vocabulary never seen in
training. The headline figure averages several seeds. Measured: ~0.93 ± 0.06 over
eight categories (chance ~0.125), with a bounded ~0.07 train-test gap.

A second, complementary check runs the **same** categoriser on real labelled data:
`invoiceiq.real_benchmark` trains it on the public
`rajeshradhakrishnan/fin-transaction-category` dataset (282 real bank- and card-
transaction descriptions across eight expense categories) and reports 0.75
cross-validated accuracy / 0.74 macro-F1 — six times the 0.125 chance rate, stable
across folds, and collapsing to chance under shuffled labels.

## Consequences
- The reported number reflects generalisation to new wording, not recall of
  templates, and is confirmed on real transaction text.
- The harder case — a category keyword with no stem relative in training — is where
  errors land; the real benchmark quantifies how the approach holds up there, and
  training on an organisation's own labelled invoices extends it further.
- Because the categoriser can be wrong, the pipeline never lets it decide alone.
