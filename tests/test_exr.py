import numpy as np

from plvis.exr import read_exr, write_exr


def test_round_trip_rgb(tmp_path):
    img = np.random.default_rng(1).random((7, 5, 3)).astype(np.float32)
    path = write_exr(tmp_path / "a.exr", img, ("R", "G", "B"), {"unit": "W m-2 sr-1 um-1"})
    assert path.read_bytes()[:4] == b"\x76\x2f\x31\x01"
    back = read_exr(path)
    for i, ch in enumerate("RGB"):
        np.testing.assert_array_equal(back[ch], img[:, :, i])


def test_single_channel(tmp_path):
    img = np.arange(12, dtype=np.float32).reshape(3, 4)
    back = read_exr(write_exr(tmp_path / "y.exr", img, ("Y",)))
    np.testing.assert_array_equal(back["Y"], img)
