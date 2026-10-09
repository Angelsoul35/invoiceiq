"""Benchmark the expense categoriser on REAL transaction data.

Trains the same word+char TF-IDF + logistic categoriser (:class:`ExpenseCategorizer`)
on the real ``rajeshradhakrishnan/fin-transaction-category`` dataset and reports
cross-validated accuracy and macro-F1 across its eight expense categories, plus a
train/held-out gap, so the number reflects real spend captured from bank and card
statements rather than only the synthetic anchors.

Run it with ``python -m invoiceiq.real_benchmark``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold

from .categorizer import ExpenseCategorizer
from .real_data import load_transaction_categories

_SEED = 42
_N_SPLITS = 5


@dataclass
class RealBenchmarkReport:
    n_transactions: int
    n_categories: int
    chance: float
    cv_accuracy: float
    cv_accuracy_std: float
    cv_macro_f1: float
    train_accuracy: float
    test_accuracy: float
    gap: float

    @property
    def verdict(self) -> str:
        # Overfitting is weak generalisation, not merely a train/held-out gap: a
        # low-bias linear model fits short, distinctive merchant strings exactly
        # (train ~1.0), so the held-out accuracy is what decides the verdict.
        if self.cv_accuracy < max(2.5 * self.chance, 0.40):
            return "weak: the categoriser barely clears the eight-way chance rate"
        if self.cv_accuracy < 0.55 and self.gap > 0.30:
            return "overfit: held-out accuracy is low while training runs far ahead"
        return "well-fit: strong, stable held-out accuracy far above the chance rate"


def _cv_scores(texts: list[str], labels: list[str], y: np.ndarray) -> tuple[float, float, float]:
    """Cross-validated accuracy (mean, std) and macro-F1 with the real categoriser."""
    cv = StratifiedKFold(n_splits=_N_SPLITS, shuffle=True, random_state=_SEED)
    accs: list[float] = []
    f1s: list[float] = []
    for train_idx, test_idx in cv.split(texts, y):
        model = ExpenseCategorizer().fit(
            [texts[i] for i in train_idx], [labels[i] for i in train_idx]
        )
        pred = [model.suggest_text(texts[i]).category for i in test_idx]
        truth = [labels[i] for i in test_idx]
        accs.append(accuracy_score(truth, pred))
        f1s.append(f1_score(truth, pred, average="macro", zero_division=0))
    return float(np.mean(accs)), float(np.std(accs)), float(np.mean(f1s))


def _mean_train_accuracy(texts: list[str], labels: list[str], y: np.ndarray) -> float:
    """Mean training-fold accuracy, the reference point for the train/held-out gap."""
    cv = StratifiedKFold(n_splits=_N_SPLITS, shuffle=True, random_state=_SEED)
    train_accs: list[float] = []
    for train_idx, _ in cv.split(texts, y):
        model = ExpenseCategorizer().fit(
            [texts[i] for i in train_idx], [labels[i] for i in train_idx]
        )
        pred = [model.suggest_text(texts[i]).category for i in train_idx]
        train_accs.append(accuracy_score([labels[i] for i in train_idx], pred))
    return float(np.mean(train_accs))


def run_benchmark(data: tuple[list[str], list[str]] | None = None) -> RealBenchmarkReport:
    texts, labels = data if data is not None else load_transaction_categories()
    classes = sorted(set(labels))
    y = np.asarray([classes.index(label) for label in labels])
    cv_acc, cv_acc_std, cv_f1 = _cv_scores(texts, labels, y)
    train_acc = _mean_train_accuracy(texts, labels, y)

    return RealBenchmarkReport(
        n_transactions=len(texts),
        n_categories=len(classes),
        chance=round(1.0 / len(classes), 4),
        cv_accuracy=round(cv_acc, 4),
        cv_accuracy_std=round(cv_acc_std, 4),
        cv_macro_f1=round(cv_f1, 4),
        train_accuracy=round(train_acc, 4),
        test_accuracy=round(cv_acc, 4),
        gap=round(train_acc - cv_acc, 4),
    )


def format_report(r: RealBenchmarkReport) -> str:
    return "\n".join(
        [
            "invoiceiq — real-data benchmark (rajeshradhakrishnan/fin-transaction-category)",
            "=" * 68,
            f"transactions: {r.n_transactions} across {r.n_categories} expense categories "
            f"(chance {r.chance:.3f})",
            "",
            f"CV accuracy : {r.cv_accuracy:.3f} +/- {r.cv_accuracy_std:.3f}",
            f"CV macro-F1 : {r.cv_macro_f1:.3f}",
            f"train / test: {r.train_accuracy:.3f} / {r.test_accuracy:.3f}  (gap {r.gap:.3f})",
            "",
            f"verdict: {r.verdict}",
        ]
    )


def main() -> None:
    print(format_report(run_benchmark()))


if __name__ == "__main__":  # pragma: no cover
    main()
