import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

# Nominal band centres of a 61-band snapshot camera (430-910 nm, 8 nm steps),
# used only when the ENVI header has no wavelength list.
DEFAULT_WAVELENGTHS = np.arange(430, 911, 8, dtype=float)


def roi_arg(text):
    """'row0:row1,col0:col1' -> (row0, row1, col0, col1)."""
    rows, cols = text.split(",")
    r0, r1 = (int(v) for v in rows.split(":"))
    c0, c1 = (int(v) for v in cols.split(":"))
    return r0, r1, c0, c1
