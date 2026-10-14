import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

WL = np.arange(430, 911, 8, dtype=float)


def gaussian_spectrum(peak=518.0, width=25.0, amplitude=0.0065):
    return amplitude * np.exp(-0.5 * ((WL - peak) / width) ** 2)


def write_envi(folder: Path, name: str, cube: np.ndarray, interleave="bip", with_wl=True,
               extra=""):
    lines, samples, bands = cube.shape
    order = {"bip": (0, 1, 2), "bil": (0, 2, 1), "bsq": (2, 0, 1)}[interleave]
    cube.astype("<f4").transpose(order).tofile(folder / f"{name}.raw")
    wl = "wavelength = {" + ", ".join(f"{w:.1f}" for w in WL) + "}\n" if with_wl else ""
    (folder / f"{name}.hdr").write_text(
        f"ENVI\nsamples = {samples}\nlines = {lines}\nbands = {bands}\n"
        f"header offset = 0\ndata type = 4\ninterleave = {interleave}\nbyte order = 0\n"
        + wl + extra)


@pytest.fixture
def decay_folder(tmp_path):
    """Twenty 12x10 cubes whose emission decays with two exponentials."""
    spec = gaussian_spectrum()
    t = np.arange(20.0)
    amp = 0.6 * np.exp(-t / 3.0) + 0.4 * np.exp(-t / 15.0)
    for k, a in enumerate(amp):
        cube = np.broadcast_to(a * spec, (12, 10, WL.size)).copy()
        write_envi(tmp_path, f"run_{k:04d}", cube)
    write_envi(tmp_path, "dark_0000", np.zeros((12, 10, WL.size)))
    return tmp_path, t, amp
