# Datasets — real transaction-category data

## `transaction_categories_real.jsonl` — rajeshradhakrishnan/fin-transaction-category

A **real**, public dataset of bank- and card-transaction descriptions labelled
with an expense category, used to validate the expense categoriser on real spend
captured from statements (not only the synthetic anchors).

| | |
|---|---|
| **Origin** | `rajeshradhakrishnan/fin-transaction-category` (Hugging Face), train + test splits merged |
| **Contents** | 282 transactions (train 225 / test 57) across 8 expense categories, one JSON object per line: `{"merchant", "category"}` |
| **Categories** | Shopping, Dining Out, Entertainment, Transportation, Housing, Payments/Credits, Utilities, Service Subscriptions |
| **Retrieved** | 2026-10-09, via the Hugging Face datasets-server |
| **License** | not declared on the dataset card; used here for research/educational benchmarking. The `category` field is a `ClassLabel` on the hub and is resolved to its string name when vendored. |

The descriptions are real transaction memos (for example `Uber 072515 SFPOOL`,
`Starbucks`, `INTRST PYMNT`, `ACH Electronic CreditGUSTO PAY 123456`) — the short,
noisy text an accounts-payable categoriser meets in practice.

Vendored so the benchmark and its tests run offline and deterministically;
`invoiceiq.real_data.fetch_transaction_categories()` refreshes it.
`invoiceiq.real_benchmark` trains the same word+char TF-IDF + logistic categoriser
on it and reports **0.75 accuracy / 0.74 macro-F1** (cross-validated, 8 categories,
chance 0.125) — real spend, well-fit, six times the chance rate and not a memorised
1.0.
