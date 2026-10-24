"""Local-only regression check (RE-047): rebuild every reference image.

Skipped unless the untouched source image is present and ``MSHVSF_REGRESSION=1``
is set, because the four builds take about a minute. References whose local
specs are absent are skipped by the script itself.
"""

from __future__ import annotations

import os

import pytest

from tools.regression.reference_builds import SOURCE_DIR, TRACK01, main

pytestmark = pytest.mark.skipif(
    not (SOURCE_DIR / TRACK01).exists() or os.environ.get("MSHVSF_REGRESSION") != "1",
    reason="needs the local source image and MSHVSF_REGRESSION=1",
)


def test_reference_builds_match_baseline() -> None:
    # The image builder only writes under build/ (patch_image).
    assert main(["--out-root", "build/regression_test"]) == 0
