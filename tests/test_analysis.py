import numpy as np
import pytest

from conftest import WL, gaussian_spectrum
from plvis import decay
from plvis.angular import angular_ratios, max_relative_spread
from plvis.comparison import compare_at_wavelength, scale_to_reference
from plvis.envi_io import find_cubes
from plvis.regression import compare_models
from plvis.series import roi_time_series


def test_series_follows_the_injected_decay(decay_folder):
    folder, t, amp = decay_folder
    rows = roi_time_series(find_cubes(folder), (2, 8, 1, 9))
    lv = np.array([r["luminance_cd_m2"] for r in rows])
    np.testing.assert_allclose(lv / lv[0], amp / amp[0], rtol=1e-5)
    assert rows[0]["peak_nm"] == 518 and rows[0]["n_pixels"] == 48


def test_regression_ranks_linear_data():
    x = np.linspace(0.001, 0.01, 50)
    best = compare_models(x, 46.0 * x + 0.01)[0]
    assert best["r2"] > 0.999999


def test_lambertian_reference_is_one():
    t = np.arange(10.0)
    l0 = np.exp(-t / 5)
    r = angular_ratios({0.0: (t, l0), 40.0: (t, 1.05 * l0)})
    np.testing.assert_allclose(r[40.0], 1.05)
    assert np.isclose(max_relative_spread([1.0, 0.95, 1.02]), 0.07 / 1.02)


def test_compare_at_550():
    spectra = {"A": gaussian_spectrum(550, 30, 0.01)}
    res = compare_at_wavelength({"A": 0.011, "B": 1.0}, spectra, WL, 550)
    assert list(res) == ["A"]
    assert res["A"]["band_nm"] == 550
    assert np.isclose(res["A"]["relative_difference"], 0.1)


def test_scale_to_reference_constant_ratio():
    t = np.arange(0, 600, 1.0)
    meas = np.exp(-t / 200)
    t_ref = np.array([60, 120, 300, 900])
    res = scale_to_reference(t, meas, t_ref, np.exp(-t_ref / 200) / 0.7)
    assert np.isclose(res["k_mean"], 0.7, rtol=1e-3) and res["k_cv"] < 1e-3
    assert res["t_ref"].size == 3
    with pytest.raises(ValueError):
        scale_to_reference(t, meas, np.array([1000.0]), np.array([1.0]))
