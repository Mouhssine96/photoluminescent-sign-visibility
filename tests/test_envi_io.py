import numpy as np
import pytest

from conftest import WL, gaussian_spectrum, write_envi
from plvis.envi_io import band_index, find_cubes, open_cube


@pytest.mark.parametrize("interleave", ["bip", "bil", "bsq"])
def test_interleaves_give_the_same_cube(tmp_path, interleave):
    rng = np.random.default_rng(0)
    cube = rng.random((5, 4, WL.size)).astype(np.float32)
    write_envi(tmp_path, "c", cube, interleave)
    c = open_cube(tmp_path / "c.hdr")
    assert c.shape == (5, 4, WL.size)
    np.testing.assert_allclose(c.roi(1, 4, 0, 3), cube[1:4, 0:3])


def test_roi_is_clipped_and_bands_selected(tmp_path):
    cube = np.ones((5, 4, WL.size))
    write_envi(tmp_path, "c", cube)
    c = open_cube(tmp_path / "c.hdr")
    assert c.roi(-3, 100, 2, 100, bands=[0, 5]).shape == (5, 2, 2)
    with pytest.raises(ValueError):
        c.roi(10, 20, 0, 2)


def test_default_wavelengths_when_header_has_none(tmp_path):
    write_envi(tmp_path, "c", np.ones((2, 2, WL.size)), with_wl=False)
    with pytest.raises(ValueError):
        open_cube(tmp_path / "c.hdr")
    assert open_cube(tmp_path / "c.hdr", WL).wavelengths[0] == 430


def test_find_cubes_orders_and_skips_calibration(decay_folder):
    folder, t, _ = decay_folder
    cubes = find_cubes(folder, dt_s=2.0)
    assert [c["name"] for c in cubes] == [f"run_{k:04d}" for k in range(20)]
    assert cubes[-1]["t_s"] == 38.0


def test_band_index():
    assert WL[band_index(WL, 550)] == 550
    assert WL[band_index(WL, 532)] == 534
