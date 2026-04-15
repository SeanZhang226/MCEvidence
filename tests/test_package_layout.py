"""Packaging/layout compatibility tests."""

import importlib


def test_legacy_import_still_works():
    legacy = importlib.import_module("MCEvidence")
    assert hasattr(legacy, "MCEvidence")
    assert hasattr(legacy, "main")


def test_package_import_works():
    pkg = importlib.import_module("mcevidence")
    assert hasattr(pkg, "MCEvidence")


def test_versions_match():
    legacy = importlib.import_module("MCEvidence")
    core = importlib.import_module("mcevidence.core")
    assert legacy.__version__ == core.__version__
