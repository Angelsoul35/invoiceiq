# ADR 0004 — Evaluate the categoriser on an anchor-disjoint split

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

## Consequences
- The reported number reflects real generalisation, not recall of templates.
- It is honest about the harder case: a category keyword with no stem relative in
  training is where errors land; closing that needs real labelled invoices.
- Because the categoriser can be wrong, the pipeline never lets it decide alone.
