import numpy as np

from conftest import WL, gaussian_spectrum
from plvis import photometry as ph


def test_v_lambda_peak_and_range():
    assert ph.v_lambda(555) == 1.0
    assert ph.v_lambda(900) == 0.0
    assert 0.86 < ph.v_lambda(530) < 0.87


def test_luminance_of_a_flat_spectrum():
    # Flat 1 W m-2 sr-1 um-1 on a fine grid: L_v = 683 * integral V d(lambda in um)
    wl = np.arange(360, 831, 1.0)
    lv = ph.luminance(np.ones_like(wl), wl)
    assert abs(lv - 683.002 * 0.10686) / lv < 5e-3   # integral of V ~ 106.86 nm


def test_luminance_is_linear_and_works_per_pixel():
    s = gaussian_spectrum()
    cube = np.stack([s, 2 * s])[None, :, :]
    lv = ph.luminance(cube, WL)
    assert lv.shape == (1, 2)
    np.testing.assert_allclose(lv[0, 1], 2 * lv[0, 0])
    assert np.isclose(lv[0, 0], ph.luminance(s, WL))


def test_band_integral_of_constant():
    val = ph.band_integral(np.full(WL.size, 2.0), WL, 502, 558)
    assert np.isclose(val, 2.0 * (558 - 502) / 1000)
