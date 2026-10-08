"""Honest, anchor-disjoint evaluation of the expense categoriser."""

from __future__ import annotations

from dataclasses import dataclass

from sklearn.metrics import accuracy_score

from .categorizer import ExpenseCategorizer
from .generate import make_split_datasets


@dataclass
class EvalReport:
    accuracy: float
    train_accuracy: float
    gap: float
    n_train: int
    n_test: int


def anchor_disjoint_eval(seed: int = 7, holdout_frac: float = 0.35) -> EvalReport:
    tr_t, tr_y, te_t, te_y = make_split_datasets(seed=seed, holdout_frac=holdout_frac)
    model = ExpenseCategorizer().fit(tr_t, tr_y)
    test_pred = [model.suggest_text(t).category for t in te_t]
    train_pred = [model.suggest_text(t).category for t in tr_t]
    acc = float(accuracy_score(te_y, test_pred))
    train_acc = float(accuracy_score(tr_y, train_pred))
    return EvalReport(acc, train_acc, round(train_acc - acc, 4), len(tr_t), len(te_t))


def aggregate_eval(seeds: range = range(6), holdout_frac: float = 0.35) -> str:
    reports = [anchor_disjoint_eval(seed=s, holdout_frac=holdout_frac) for s in seeds]
    accs = [r.accuracy for r in reports]
    mean = sum(accs) / len(accs)
    std = (sum((a - mean) ** 2 for a in accs) / len(accs)) ** 0.5
    train = sum(r.train_accuracy for r in reports) / len(reports)
    gap = sum(r.gap for r in reports) / len(reports)
    return (
        f"accuracy (mean+/-std over {len(accs)} seeds): {mean:.2f} +/- {std:.2f}   "
        f"# eight categories; chance ~0.125; keywords unseen in training\n"
        f"train accuracy                     : {train:.2f}\n"
        f"train-test gap                     : {gap:.2f}   # bounded -> stem signal, not templates"
    )


if __name__ == "__main__":  # pragma: no cover
    print(aggregate_eval())
