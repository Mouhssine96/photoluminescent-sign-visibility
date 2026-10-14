"""Decay kinetics of a photoluminescent emission."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.optimize import curve_fit


def biexp(t, a1, tau1, a2, tau2, c):
    """Two exponentials plus a constant offset c (the offset absorbs the slow
    tail and the residual background over a finite recording)."""
    return a1 * np.exp(-t / tau1) + a2 * np.exp(-t / tau2) + c


@dataclass
class BiexpFit:
    a1: float
    tau1: float
    a2: float
    tau2: float
    c: float
    r2: float

    def __call__(self, t):
        return biexp(np.asarray(t, float), self.a1, self.tau1, self.a2, self.tau2, self.c)


def fit_biexp(t, y) -> Optional[BiexpFit]:
    """Fit y(t) with two exponentials and an offset; tau1 <= tau2 in the result."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    if t.size < 6:
        return None
    span = max(t[-1] - t[0], 1.0)
    p0 = [0.5 * (y[0] - y[-1]), span / 20, 0.5 * (y[0] - y[-1]), span / 3, y[-1]]
    lower = [-np.inf, 1e-6, -np.inf, 1e-6, -np.inf]
    try:
        p, _ = curve_fit(biexp, t - t[0], y, p0=p0, bounds=(lower, np.inf), maxfev=20000)
    except RuntimeError:
        return None
    a1, tau1, a2, tau2, c = p
    if tau1 > tau2:
        a1, tau1, a2, tau2 = a2, tau2, a1, tau1
    res = y - biexp(t - t[0], a1, tau1, a2, tau2, c)
    r2 = 1.0 - np.sum(res ** 2) / np.sum((y - y.mean()) ** 2)
    return BiexpFit(a1, tau1, a2, tau2, c, float(r2))


def normalise(y):
    y = np.asarray(y, float)
    return y / y[0]


def time_to_fraction(t, y, fraction: float = 0.5) -> Optional[float]:
    """First time at which y/y[0] drops to ``fraction`` (linear interpolation)."""
    t, yn = np.asarray(t, float), normalise(y)
    below = np.nonzero(yn <= fraction)[0]
    if below.size == 0:
        return None
    i = below[0]
    if i == 0:
        return float(t[0])
    return float(np.interp(fraction, [yn[i], yn[i - 1]], [t[i], t[i - 1]]))
