import numpy as np

from plvis import decay


def test_fit_recovers_two_time_constants():
    t = np.arange(0, 900, 1.0)
    y = 0.004 * np.exp(-t / 100) + 0.002 * np.exp(-t / 580) + 0.0003
    fit = decay.fit_biexp(t, y)
    assert fit is not None and fit.r2 > 0.9999
    assert abs(fit.tau1 - 100) < 1 and abs(fit.tau2 - 580) < 5


def test_time_to_half():
    t = np.linspace(0, 10, 1001)
    y = np.exp(-t)
    assert abs(decay.time_to_fraction(t, y, 0.5) - np.log(2)) < 1e-3
    assert decay.time_to_fraction(t, np.ones_like(t)) is None
