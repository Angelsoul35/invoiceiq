"""Tests for the real fin-transaction expense-category benchmark.

They prove the vendored data is the real fin-transaction set, that the categoriser
is well fit on real transactions (strong and stable on held-out folds, far above the
eight-way chance rate), and that the signal is real (shuffling the labels collapses
it to chance).
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from invoiceiq.real_benchmark import run_benchmark
from invoiceiq.real_data import load_transaction_categories

_CATEGORIES = {
    "Shopping",
    "Dining Out",
    "Entertainment",
    "Transportation",
    "Housing",
    "Payments/Credits",
    "Utilities",
    "Service Subscriptions",
}


@pytest.fixture(scope="module")
def data():
    return load_transaction_categories()


@pytest.fixture(scope="module")
def report(data):
    return run_benchmark(data)


def test_loads_the_real_transactions(data):
    texts, labels = data
    assert len(texts) == 282
    assert len(labels) == 282
    assert set(labels) == _CATEGORIES  # the eight real expense categories, as strings
    # Real memos, not synthetic templates: short, noisy merchant strings.
    assert any("Uber" in t for t in texts)
    assert any("Starbucks" in t for t in texts)


def test_categoriser_is_well_fit_on_real_transactions(report):
    # Strong and stable on held-out real transactions, far above the 0.125 chance
    # rate, and not a fake ~1.0: real spend is varied.
    assert report.n_categories == 8
    assert report.cv_accuracy >= 5 * report.chance, report  # >= 0.625, measured 0.752
    assert report.cv_accuracy <= 0.90, report
    assert report.cv_macro_f1 >= 0.62, report
    assert report.cv_accuracy_std <= 0.10, report
    assert report.train_accuracy >= 0.90, report
    assert report.verdict.startswith("well-fit")


def test_shuffled_labels_collapse_to_chance(data):
    texts, labels = data
    shuffled = np.random.default_rng(0).permutation(labels).tolist()
    r = run_benchmark((texts, shuffled))
    assert r.cv_accuracy <= 0.30, r.cv_accuracy  # near the 0.125 chance rate
    assert r.verdict.startswith("weak")


def test_verdict_branches():
    from invoiceiq.real_benchmark import RealBenchmarkReport

    def rep(cv, gap):
        train = round(cv + gap, 4)
        return RealBenchmarkReport(282, 8, 0.125, cv, 0.03, cv, train, cv, gap)

    assert rep(0.30, 0.20).verdict.startswith("weak")
    assert rep(0.50, 0.35).verdict.startswith("overfit")
    assert rep(0.75, 0.24).verdict.startswith("well-fit")


def test_loader_rejects_a_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_transaction_categories(tmp_path / "nope.jsonl")


def test_loader_skips_blank_lines(tmp_path):
    dest = tmp_path / "tx.jsonl"
    dest.write_text(
        '{"merchant": "Uber", "category": "Transportation"}\n\n'
        '{"merchant": "Starbucks", "category": "Dining Out"}\n',
        encoding="utf-8",
    )
    texts, labels = load_transaction_categories(dest)
    assert texts == ["Uber", "Starbucks"]
    assert labels == ["Transportation", "Dining Out"]


def _fake_urlopen_factory(page):
    empty = {"num_rows_total": 0, "rows": []}
    calls = {"n": 0}

    class _Resp:
        def __init__(self, body):
            self._b = body

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return self._b

    def fake_urlopen(url, timeout=0):
        # First call (train split) returns rows; later calls return empty.
        calls["n"] += 1
        return _Resp(json.dumps(page if calls["n"] == 1 else empty).encode())

    return fake_urlopen


def test_fetch_writes_the_dataset_and_resolves_class_labels(tmp_path, monkeypatch):
    page = {
        "num_rows_total": 2,
        "features": [
            {"name": "merchant", "type": {"dtype": "string", "_type": "Value"}},
            {
                "name": "category",
                "type": {
                    "names": [
                        "Shopping",
                        "Dining Out",
                        "Entertainment",
                        "Transportation",
                        "Housing",
                        "Payments/Credits",
                        "Utilities",
                        "Service Subscriptions",
                    ],
                    "_type": "ClassLabel",
                },
            },
        ],
        "rows": [
            {"row": {"merchant": "Uber 072515 SFPOOL", "category": 3}},
            {"row": {"merchant": "Starbucks", "category": 1}},
        ],
    }
    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen_factory(page))
    from invoiceiq.real_data import fetch_transaction_categories

    dest = tmp_path / "tx.jsonl"
    n = fetch_transaction_categories(dest)
    assert n == 2
    texts, labels = load_transaction_categories(dest)
    assert texts[0] == "Uber 072515 SFPOOL"
    # The ClassLabel integers are resolved to their human-readable names.
    assert labels == ["Transportation", "Dining Out"]


def test_fetch_skips_an_unreachable_split(tmp_path, monkeypatch):
    def boom(url, timeout=0):
        raise OSError("network down")

    monkeypatch.setattr("urllib.request.urlopen", boom)
    from invoiceiq.real_data import fetch_transaction_categories

    dest = tmp_path / "tx.jsonl"
    n = fetch_transaction_categories(dest)
    assert n == 0
    assert dest.exists()


def test_format_and_main(report, capsys, monkeypatch):
    import invoiceiq.real_benchmark as rb

    text = rb.format_report(report)
    assert "fin-transaction-category" in text
    assert f"{report.cv_accuracy:.3f}" in text
    monkeypatch.setattr(rb, "run_benchmark", lambda data=None: report)
    rb.main()
    assert "real-data benchmark" in capsys.readouterr().out
