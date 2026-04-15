"""CLI tests for parameter-selection options."""

import subprocess
import sys


def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def test_cli_cosmo_mode_runs():
    out = run_cmd(
        [
            sys.executable,
            "MCEvidence.py",
            "tests/data/cobaya_multi",
            "--cosmo",
            "-k",
            "3",
            "-vb",
            "0",
        ]
    )
    assert "ln(B)[k]" in out.stdout


def test_cli_custom_param_list_runs():
    out = run_cmd(
        [
            sys.executable,
            "MCEvidence.py",
            "tests/data/cobaya_multi",
            "--select-params",
            "p1,p2,A_planck",
            "-k",
            "3",
            "-vb",
            "0",
        ]
    )
    assert "ln(B)[k]" in out.stdout


def test_cli_report_output_runs(tmp_path):
    report = tmp_path / "cli_report.json"
    out = run_cmd(
        [
            sys.executable,
            "MCEvidence.py",
            "tests/data/cobaya_multi",
            "--select-params",
            "p1,p2",
            "--report-file",
            str(report),
            "--report-format",
            "json",
            "-k",
            "3",
            "-vb",
            "0",
        ]
    )
    assert "Report written to" in out.stdout
    assert report.exists()
