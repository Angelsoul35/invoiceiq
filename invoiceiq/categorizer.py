"""An explainable expense-category classifier for an invoice's line items.

A ``FeatureUnion`` of word (1-2 gram) and character (``char_wb`` 3-5) TF-IDF views
feeds a logistic regression that maps the invoice's line-item text to an expense
category. Linear by design, so each suggestion comes with the words that drove it.
It never decides on its own: a low-confidence suggestion is marked for review.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from .generate import make_dataset
from .models import Invoice


@dataclass
class CategorySuggestion:
    category: str
    confidence: float
    needs_review: bool
    top_terms: list[tuple[str, float]]


def _build_features() -> FeatureUnion:
    return FeatureUnion(
        [
            ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2)),
        ]
    )


class ExpenseCategorizer:
    def __init__(self, min_confidence: float = 0.45) -> None:
        self.min_confidence = min_confidence
        self._pipeline: Pipeline | None = None

    def fit(self, texts: list[str] | None = None, labels: list[str] | None = None):
        if texts is None or labels is None:
            texts, labels = make_dataset()
        pipeline = Pipeline(
            [("features", _build_features()), ("clf", LogisticRegression(max_iter=2000, C=4.0))]
        )
        pipeline.fit(texts, labels)
        self._pipeline = pipeline
        return self

    def _require_fitted(self) -> Pipeline:
        if self._pipeline is None:
            raise RuntimeError("categoriser is not fitted; call fit() first")
        return self._pipeline

    @staticmethod
    def invoice_text(invoice: Invoice) -> str:
        parts = [invoice.vendor or ""]
        parts += [item.description for item in invoice.line_items]
        return " ".join(p for p in parts if p).strip()

    def suggest_text(self, text: str) -> CategorySuggestion:
        pipeline = self._require_fitted()
        clf: LogisticRegression = pipeline.named_steps["clf"]
        proba = pipeline.predict_proba([text])[0]
        best = int(np.argmax(proba))
        return CategorySuggestion(
            category=str(clf.classes_[best]),
            confidence=float(proba[best]),
            needs_review=float(proba[best]) < self.min_confidence,
            top_terms=self._explain(pipeline, text, best),
        )

    def suggest(self, invoice: Invoice) -> CategorySuggestion:
        return self.suggest_text(self.invoice_text(invoice))

    def _explain(
        self, pipeline: Pipeline, text: str, class_index: int, k: int = 5
    ) -> list[tuple[str, float]]:
        features: FeatureUnion = pipeline.named_steps["features"]
        clf: LogisticRegression = pipeline.named_steps["clf"]
        x = features.transform([text])
        names = features.get_feature_names_out()
        coef = clf.coef_[class_index] if clf.coef_.shape[0] > 1 else clf.coef_[0]
        contributions = x.multiply(coef).toarray()[0]
        order = np.argsort(contributions)[::-1]
        out: list[tuple[str, float]] = []
        for idx in order[:k]:
            if contributions[idx] <= 0:
                break
            raw = str(names[idx])
            term = raw.split("__", 1)[1] if "__" in raw else raw
            out.append((term, round(float(contributions[idx]), 4)))
        return out
