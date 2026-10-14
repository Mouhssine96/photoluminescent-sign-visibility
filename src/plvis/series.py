"""Time series of a region of interest over a sequence of radiance cubes."""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from . import photometry as ph
from .envi_io import open_cube


def region_statistics(block: np.ndarray, wl_nm: np.ndarray,
                      pl_band=(500.0, 560.0)) -> Dict[str, float]:
    """Statistics of a (rows, cols, bands) radiance block."""
    mean_spectrum = block.mean(axis=(0, 1))
    i_peak = int(np.argmax(mean_spectrum))
    return {
        "peak_nm": float(wl_nm[i_peak]),
        "peak_radiance": float(mean_spectrum[i_peak]),
        "mean_radiance": float(mean_spectrum.mean()),
        "pl_band_radiance": float(ph.band_integral(mean_spectrum, wl_nm, *pl_band)),
        "luminance_cd_m2": float(ph.luminance(mean_spectrum, wl_nm)),
        "n_pixels": int(block.shape[0] * block.shape[1]),
    }


def roi_time_series(cubes: List[Dict], roi, default_wavelengths: Optional[np.ndarray] = None,
                    pl_band=(500.0, 560.0)) -> List[Dict]:
    """One row of statistics per cube for the region ``roi`` = (row0, row1, col0, col1).

    Only the region is read from disk, so long sequences fit in a small memory.
    """
    rows = []
    for c in cubes:
        cube = open_cube(c["hdr"], default_wavelengths)
        stats = region_statistics(cube.roi(*roi), cube.wavelengths, pl_band)
        rows.append({"index": c["index"], "time_s": c["t_s"], "cube": c["name"], **stats})
    return rows
