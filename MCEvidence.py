#!/usr/bin/env python
"""Backward-compatible entry module.

This thin wrapper keeps historical imports working:

    from MCEvidence import MCEvidence

while the implementation now lives in ``mcevidence.core``.
"""

from mcevidence.core import *  # noqa: F401,F403
from mcevidence.core import main

__version__ = "2.2.0"


if __name__ == "__main__":
    main()
