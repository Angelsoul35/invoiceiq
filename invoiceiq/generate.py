"""Synthetic, labelled invoice line-item descriptions for the categoriser.

Same honesty discipline as the rest of the portfolio: each expense category has
recurring **anchor keywords** (which share partial stems, the way real line items
do) plus generic **context** filler. The evaluation holds out whole anchor
keywords, so the test vocabulary is unseen and the reported accuracy reflects real
generalisation, not template memorisation. Everything is synthetic.
"""

from __future__ import annotations

import numpy as np

# Expense category -> recurring anchor keywords (with partial shared stems).
ANCHORS: dict[str, list[str]] = {
    "office_supplies": [
        "office paper supplies",
        "printer ink cartridges",
        "stationery and pens",
        "desk organiser supplies",
        "whiteboard markers",
        "office supplies restock",
    ],
    "software_subscriptions": [
        "software subscription",
        "saas software license",
        "cloud software hosting",
        "developer software tool",
        "software api subscription",
        "productivity software seat",
    ],
    "professional_services": [
        "consulting services fee",
        "legal services retainer",
        "accounting services",
        "professional services engagement",
        "advisory consulting fee",
        "audit professional services",
    ],
    "travel": [
        "flight airfare",
        "hotel travel lodging",
        "taxi travel ride",
        "travel rental car",
        "train travel fare",
        "business travel trip",
    ],
    "utilities": [
        "electricity utility",
        "water utility service",
        "internet broadband utility",
        "gas heating utility",
        "telecom utility bill",
        "power utility charge",
    ],
    "marketing": [
        "online advertising campaign",
        "marketing advertising spend",
        "social media advertising",
        "advertising creative design",
        "marketing campaign services",
        "search advertising budget",
    ],
    "shipping_logistics": [
        "freight shipping charge",
        "courier delivery shipping",
        "logistics freight service",
        "parcel shipping cost",
        "warehouse logistics handling",
        "shipping and freight",
    ],
    "hardware_equipment": [
        "laptop hardware equipment",
        "server hardware purchase",
        "monitor display equipment",
        "networking hardware switch",
        "workstation equipment",
        "hardware peripheral equipment",
    ],
}

CONTEXT_FRAGMENTS: list[str] = [
    "monthly",
    "annual",
    "quarterly",
    "invoice",
    "charge",
    "billed",
    "for the quarter",
    "renewal",
    "recurring",
    "service",
    "purchase",
    "order",
    "fee",
    "payment",
]

ALL_CATEGORIES = list(ANCHORS.keys())


def _compose(rng: np.random.Generator, anchors: list[str], contexts: list[str]) -> str:
    anchor = str(rng.choice(anchors))
    k = int(rng.integers(1, 3))
    frags = list(rng.choice(contexts, size=min(k, len(contexts)), replace=False))
    parts = [anchor, *frags]
    rng.shuffle(parts)
    return " ".join(parts)


def _generate(
    rng: np.random.Generator, n: int, anchor_pool: dict[str, list[str]], context_pool: list[str]
) -> tuple[list[str], list[str]]:
    cats = list(anchor_pool.keys())
    texts, labels = [], []
    for _ in range(n):
        cat = cats[int(rng.integers(len(cats)))]
        texts.append(_compose(rng, anchor_pool[cat], context_pool))
        labels.append(cat)
    return texts, labels


def make_dataset(n: int = 1600, seed: int = 7) -> tuple[list[str], list[str]]:
    rng = np.random.default_rng(seed)
    return _generate(rng, n, ANCHORS, CONTEXT_FRAGMENTS)


def _split_anchors(rng: np.random.Generator, holdout_frac: float):
    train, test = {}, {}
    for cat, anchors in ANCHORS.items():
        idx = rng.permutation(len(anchors))
        cut = max(1, round(len(anchors) * (1 - holdout_frac)))
        train[cat] = [anchors[i] for i in idx[:cut]]
        test[cat] = [anchors[i] for i in idx[cut:]] or [anchors[idx[-1]]]
    return train, test


def make_split_datasets(
    n: int = 1600, seed: int = 7, holdout_frac: float = 0.35
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Anchor-disjoint train/test: whole anchor keywords are held out of training."""
    rng = np.random.default_rng(seed)
    a_train, a_test = _split_anchors(rng, holdout_frac)
    tr_t, tr_y = _generate(rng, n, a_train, CONTEXT_FRAGMENTS)
    te_t, te_y = _generate(rng, n // 3, a_test, CONTEXT_FRAGMENTS)
    return tr_t, tr_y, te_t, te_y
