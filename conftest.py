"""Pytest configuration.

Puts the repository root on ``sys.path`` so tests can import ``src`` without
the project being installed. There is no packaging step yet and adding one to
run the tests would be premature.

Tests build what they need in memory or under ``tmp_path``. Nothing in the
suite reads ``data/``, so it runs on a clone with no data fetched and no
network reachable. The one exception is deliberate:
``tests/test_fetch_scidb.py`` reads ``config/sources.yml``, which is committed
and present in every clone, because a silent change to that file would break
the fetch layer in a way no other test would catch.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
