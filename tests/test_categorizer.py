from __future__ import annotations

import pytest

from invoiceiq.categorizer import ExpenseCategorizer
from invoiceiq.evaluation import anchor_disjoint_eval


@pytest.fixture(scope="session")
def categorizer() -> ExpenseCategorizer:
    return ExpenseCategorizer().fit()


def test_unfitted_raises():
    with pytest.raises(RuntimeError):
        ExpenseCategorizer().suggest_text("anything")


def test_suggests_sensible_categories(categorizer: ExpenseCategorizer):
    cases = {
        "annual cloud software hosting subscription renewal": "software_subscriptions",
        "flight and hotel for the client trip": "travel",
        "electricity and water utility bill": "utilities",
        "freight courier delivery shipping charge": "shipping_logistics",
        "legal advisory consulting services fee": "professional_services",
    }
    for text, expected in cases.items():
        s = categorizer.suggest_text(text)
        assert s.category == expected, f"{text!r} -> {s.category}, expected {expected}"
        assert s.top_terms


def test_anchor_disjoint_generalises_without_overfitting():
    # Whole anchor keywords are held out of training, so the test vocabulary is
    # unseen and a near-1.0 within-distribution score cannot hide memorisation.
    report = anchor_disjoint_eval()
    assert report.accuracy >= 0.70  # eight categories; chance ~0.125
    assert report.train_accuracy >= 0.95
    assert report.gap <= 0.28


def test_low_confidence_flagged(categorizer: ExpenseCategorizer):
    # An ambiguous line with no category anchor yields low confidence and is
    # routed to review rather than auto-assigned.
    s = categorizer.suggest_text("payment rendered")
    assert s.confidence < categorizer.min_confidence
    assert s.needs_review
