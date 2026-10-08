from __future__ import annotations

from invoiceiq import cli


def test_demo_runs(capsys):
    cli.demo()
    out = capsys.readouterr().out
    assert "InvoiceIQ demo" in out
    assert "total_mismatch" in out  # the bad-math invoice
    assert "duplicate_invoice_number" in out  # the resubmitted invoice
    assert "over_approval_limit" in out  # the big invoice


def test_main_usage(capsys):
    assert cli.main() == 1
    assert "usage" in capsys.readouterr().out
