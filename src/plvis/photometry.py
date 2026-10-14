"""Radiometric to photometric conversion.

Spectral radiance is expected in W m^-2 sr^-1 um^-1 and wavelengths in nm.
Luminance:  L_v = K_m * integral L_e(lambda) V(lambda) d(lambda),  lambda in um,
K_m = 683.002 lm/W, V = CIE 1931 photopic luminous efficiency (5 nm steps).
"""
from __future__ import annotations

import numpy as np

KM = 683.002  # lm/W

V_NM = np.arange(360, 831, 5, dtype=float)
V_VAL = np.array([
    3.917e-6, 6.965e-6, 1.239e-5, 2.202e-5, 3.900e-5, 6.400e-5, 1.200e-4, 2.170e-4,
    3.960e-4, 6.400e-4, 1.210e-3, 2.180e-3, 4.000e-3, 7.300e-3, 1.160e-2, 1.684e-2,
    2.300e-2, 2.980e-2, 3.800e-2, 4.800e-2, 6.000e-2, 7.390e-2, 9.098e-2, 1.126e-1,
    1.390e-1, 1.693e-1, 2.080e-1, 2.586e-1, 3.230e-1, 4.073e-1, 5.030e-1, 6.082e-1,
    7.100e-1, 7.932e-1, 8.620e-1, 9.149e-1, 9.540e-1, 9.803e-1, 9.950e-1, 1.0000,
    9.950e-1, 9.786e-1, 9.520e-1, 9.154e-1, 8.700e-1, 8.163e-1, 7.570e-1, 6.949e-1,
    6.310e-1, 5.668e-1, 5.030e-1, 4.412e-1, 3.810e-1, 3.210e-1, 2.650e-1, 2.170e-1,
    1.750e-1, 1.382e-1, 1.070e-1, 8.160e-2, 6.100e-2, 4.458e-2, 3.200e-2, 2.320e-2,
    1.700e-2, 1.192e-2, 8.210e-3, 5.723e-3, 4.102e-3, 2.929e-3, 2.091e-3, 1.484e-3,
    1.047e-3, 7.400e-4, 5.200e-4, 3.611e-4, 2.492e-4, 1.719e-4, 1.200e-4, 8.480e-5,
    6.000e-5, 4.240e-5, 3.000e-5, 2.120e-5, 1.499e-5, 1.060e-5, 7.466e-6, 5.260e-6,
    3.704e-6, 2.609e-6, 1.839e-6, 1.297e-6, 9.150e-7, 6.460e-7, 4.560e-7])
assert V_VAL.size == V_NM.size == 95


def v_lambda(wl_nm) -> np.ndarray:
    """CIE 1931 V(lambda), linearly interpolated, zero outside 360-830 nm."""
    return np.interp(np.asarray(wl_nm, float), V_NM, V_VAL, left=0.0, right=0.0)


def _trapz(y, x, axis=-1):
    f = getattr(np, "trapezoid", None) or np.trapz
    return f(y, x, axis=axis)


def luminance(radiance, wl_nm, axis: int = -1):
    """Luminance in cd/m2 of a spectrum (or of every pixel of a cube, axis=-1)."""
    radiance = np.asarray(radiance, float)
    shape = [1] * radiance.ndim
    shape[axis] = -1
    v = v_lambda(wl_nm).reshape(shape)
    return KM * _trapz(radiance * v, np.asarray(wl_nm, float) / 1000.0, axis=axis)


def spectral_luminance(radiance, wl_nm):
    """K_m V(lambda) L_e(lambda), in cd m^-2 um^-1 (not integrated)."""
    return KM * v_lambda(wl_nm) * np.asarray(radiance, float)


def band_integral(radiance, wl_nm, nm_min: float, nm_max: float, axis: int = -1):
    """Integral of the radiance between two wavelengths (W m^-2 sr^-1)."""
    wl = np.asarray(wl_nm, float)
    sel = (wl >= nm_min) & (wl <= nm_max)
    return _trapz(np.compress(sel, np.asarray(radiance, float), axis=axis),
                  wl[sel] / 1000.0, axis=axis)
