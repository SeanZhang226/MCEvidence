"""Reporting output tests."""

import json
from pathlib import Path

from MCEvidence import MCEvidence


def test_api_write_json_report(tmp_path):
    report = tmp_path / "run_report.json"
    mce = MCEvidence("tests/data/cobaya_multi", kmax=3, verbose=0)
    lnz = mce.evidence()
    written = mce.write_report(str(report), lnz_values=lnz, report_format="json")
    assert Path(written).exists()
    payload = json.loads(report.read_text())
    assert "selected_param_names" in payload
    assert "lnz_values" in payload


def test_api_write_txt_report(tmp_path):
    report = tmp_path / "run_report.txt"
    mce = MCEvidence("tests/data/cobaya_multi", kmax=3, verbose=0, param_names=["p1", "p2"])
    lnz = mce.evidence()
    mce.write_report(str(report), lnz_values=lnz, report_format="txt")
    txt = report.read_text()
    assert "selected_param_names" in txt
    assert "lnz_values" in txt
