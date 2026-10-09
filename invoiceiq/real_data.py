"""Load the real fin-transaction expense-category dataset.

The synthetic generator (:mod:`invoiceiq.generate`) gives a controlled, anchor-
disjoint evaluation of the categoriser; this module loads **real** bank- and card-
transaction descriptions labelled with an expense category (the public
``rajeshradhakrishnan/fin-transaction-category`` dataset, vendored under
``datasets/``) and runs the *same* categoriser on them, so the real benchmark
measures the same approach on real spend captured from statements rather than only
the synthetic anchors.

``fetch_transaction_categories`` refreshes the vendored copy from the Hugging Face
datasets-server.
"""

from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DATASET_PATH = _REPO_ROOT / "datasets" / "transaction_categories_real.jsonl"
_HF_ROWS_URL = (
    "https://datasets-server.huggingface.co/rows?dataset="
    "rajeshradhakrishnan%2Ffin-transaction-category"
    "&config=default&split={split}&offset={offset}&length=100"
)


def load_transaction_categories(
    path: str | Path | None = None,
) -> tuple[list[str], list[str]]:
    """Return ``(texts, labels)``: real transaction descriptions and their expense category."""
    p = Path(path) if path is not None else _DATASET_PATH
    if not p.exists():
        raise FileNotFoundError(
            f"Vendored transaction-category data not found at {p}. Run "
            "`python -c 'from invoiceiq.real_data import "
            "fetch_transaction_categories as f; f()'`."
        )
    texts: list[str] = []
    labels: list[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        texts.append(str(row["merchant"]))
        labels.append(str(row["category"]))
    return texts, labels


def fetch_transaction_categories(dest: str | Path | None = None) -> int:
    """Download the real fin-transaction-category dataset into ``datasets/``.

    Needs network access to the Hugging Face datasets-server. The ``category`` field
    is a ``ClassLabel`` integer on the hub; this resolves it to its human-readable
    name using the feature schema returned alongside the rows, so the vendored file
    stores the category as a string and the loader stays offline. Returns the number
    of rows written. Only needed to create or refresh the vendored file.
    """
    import urllib.request

    target = Path(dest) if dest is not None else _DATASET_PATH
    rows: list[dict] = []
    for split in ("train", "test"):
        offset = 0
        names: list[str] | None = None
        while True:
            url = _HF_ROWS_URL.format(split=split, offset=offset)
            try:
                with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 - fixed URL
                    payload = json.load(resp)
            except Exception:  # noqa: BLE001 - a missing split is simply skipped
                break
            if names is None:
                names = _class_label_names(payload)
            batch = payload.get("rows", [])
            if not batch:
                break
            for row in batch:
                raw = row["row"]
                category = raw["category"]
                if names is not None and isinstance(category, int):
                    category = names[category]
                rows.append({"merchant": raw["merchant"], "category": str(category)})
            offset += 100
            if offset >= payload.get("num_rows_total", 0):
                break

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    return len(rows)


def _class_label_names(payload: dict) -> list[str] | None:
    """Pull the ``category`` ClassLabel names from a datasets-server rows payload."""
    for feature in payload.get("features", []):
        if feature.get("name") == "category":
            return feature.get("type", {}).get("names")
    return None
