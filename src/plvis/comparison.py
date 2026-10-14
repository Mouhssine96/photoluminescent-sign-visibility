"""Comparison of measured radiance with simulated values or a reference curve."""
from __future__ import annotations

from typing import Dict

import numpy as np

from .envi_io import band_index


def compare_at_wavelength(simulated: Dict[str, float], spectra: Dict[str, np.ndarray],
                          wl_nm: np.ndarray, nm: float = 550.0) -> Dict[str, dict]:
    """Compare a monochromatic simulated radiance with the measured spectrum of the
    same region, taken at the measured band closest to ``nm``."""
    i = band_index(wl_nm, nm)
    out = {}
    for name in sorted(set(simulated) & set(spectra)):
        sim, meas = float(simulated[name]), float(spectra[name][i])
        out[name] = {"band_nm": float(wl_nm[i]), "simulated": sim, "measured": meas,
                     "relative_difference": (sim - meas) / meas, "ratio": sim / meas}
    return out


def scale_to_reference(t_meas, l_meas, t_ref, l_ref) -> dict:
    """Ratio K between a measured decay curve and a sparse reference curve.

    The measurement is interpolated at the reference times inside its own time
    range (no extrapolation). If K is roughly constant, ``l_meas / K`` gives an
    estimate of the reference curve at every measured time. The coefficient of
    variation of K tells whether that assumption holds.
    """
    t_meas, l_meas = np.asarray(t_meas, float), np.asarray(l_meas, float)
    t_ref, l_ref = np.asarray(t_ref, float), np.asarray(l_ref, float)
    inside = (t_ref >= t_meas.min()) & (t_ref <= t_meas.max())
    if not inside.any():
        raise ValueError("no reference time inside the measured time range")
    k = np.interp(t_ref[inside], t_meas, l_meas) / l_ref[inside]
    k_mean = float(k.mean())
    return {"t_ref": t_ref[inside], "k": k, "k_mean": k_mean,
            "k_cv": float(k.std() / k_mean), "scaled_reference": l_meas / k_mean}
