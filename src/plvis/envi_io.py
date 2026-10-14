"""Reading ENVI hyperspectral cubes without loading them fully in memory.

Only the header keys needed for radiance cubes are supported (samples, lines,
bands, data type, interleave, byte order, header offset, wavelength). The
binary file is opened as a NumPy memory map, so reading a region of interest
costs only the memory of that region. If the optional ``spectral`` package is
installed it is not needed here: this reader has no dependency beyond NumPy.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

_DTYPES = {1: np.uint8, 2: np.int16, 3: np.int32, 4: np.float32, 5: np.float64,
           12: np.uint16, 13: np.uint32, 14: np.int64, 15: np.uint64}
_BINARY_EXT = (".raw", ".dat", ".img", ".bin", "")
EXCLUDED_WORDS = ("dark", "white", "calib", "reference", "ref", "background", "bg")


def parse_header(hdr_path: Path) -> Dict[str, str]:
    """Return the ENVI header as a dict of lower-case keys and raw string values."""
    text = Path(hdr_path).read_text(errors="ignore")
    out: Dict[str, str] = {}
    for m in re.finditer(r"^\s*([^=\n]+?)\s*=\s*(\{[^}]*\}|[^\n]*)", text, re.M):
        out[m.group(1).strip().lower()] = m.group(2).strip()
    return out


def _floats(value: str) -> np.ndarray:
    return np.array([float(v) for v in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", value)])


@dataclass
class Cube:
    """Memory-mapped ENVI cube, always exposed as (lines, samples, bands)."""
    hdr: Path
    data: np.ndarray
    wavelengths: np.ndarray
    header: Dict[str, str] = field(repr=False)

    @property
    def shape(self):
        return self.data.shape

    def roi(self, row0: int, row1: int, col0: int, col1: int,
            bands: Optional[Sequence[int]] = None) -> np.ndarray:
        """Return the region [row0:row1, col0:col1] as float64, bounds clipped."""
        n_l, n_s, _ = self.data.shape
        r0, r1 = max(0, row0), min(n_l, row1)
        c0, c1 = max(0, col0), min(n_s, col1)
        if r1 <= r0 or c1 <= c0:
            raise ValueError(f"empty region after clipping: rows {r0}:{r1}, cols {c0}:{c1}")
        block = self.data[r0:r1, c0:c1, :]
        if bands is not None:
            block = block[:, :, list(bands)]
        return np.asarray(block, dtype=np.float64)


def find_binary(hdr_path: Path) -> Optional[Path]:
    for ext in _BINARY_EXT:
        cand = hdr_path.with_suffix(ext) if ext else hdr_path.parent / hdr_path.stem
        if cand.exists() and cand != hdr_path:
            return cand
    return None


def open_cube(hdr_path, default_wavelengths: Optional[np.ndarray] = None) -> Cube:
    hdr_path = Path(hdr_path)
    h = parse_header(hdr_path)
    lines, samples, bands = int(h["lines"]), int(h["samples"]), int(h["bands"])
    dtype = np.dtype(_DTYPES[int(h.get("data type", "4"))])
    if int(h.get("byte order", "0")) == 1:
        dtype = dtype.newbyteorder(">")
    offset = int(h.get("header offset", "0"))
    interleave = h.get("interleave", "bip").lower()
    shapes = {"bip": (lines, samples, bands), "bil": (lines, bands, samples),
              "bsq": (bands, lines, samples)}
    binary = find_binary(hdr_path)
    if binary is None:
        raise FileNotFoundError(f"no binary file next to {hdr_path}")
    raw = np.memmap(binary, dtype=dtype, mode="r", offset=offset, shape=shapes[interleave])
    data = {"bip": raw, "bil": raw.transpose(0, 2, 1), "bsq": raw.transpose(1, 2, 0)}[interleave]
    wl = _floats(h["wavelength"]) if "wavelength" in h else None
    if wl is None or len(wl) != bands:
        if default_wavelengths is None or len(default_wavelengths) != bands:
            raise ValueError("wavelengths missing from header and no valid default given")
        wl = np.asarray(default_wavelengths, dtype=float)
    return Cube(hdr_path, data, wl, h)


def _sequence_number(stem: str) -> int:
    for pattern in (r"_(\d{4})(?:_|$)", r"\d{14,}"):
        m = re.search(pattern, stem)
        if m:
            return int(m.group(1) if m.groups() else m.group(0))
    nums = re.findall(r"\d+", stem)
    return int(nums[-1]) if nums else -1


def find_cubes(folder, dt_s: float = 1.0) -> List[Dict]:
    """List the float radiance cubes of a folder, in acquisition order.

    Calibration files (dark, white, reference...) are skipped. Order: the
    acquisition time in the header if present, then the sequence number in the
    file name. Each entry gets an index and a time ``index * dt_s``.
    """
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(folder)
    cubes = []
    for hdr in folder.glob("*.hdr"):
        if any(w in hdr.stem.lower() for w in EXCLUDED_WORDS):
            continue
        if find_binary(hdr) is None:
            continue
        h = parse_header(hdr)
        if int(h.get("data type", "0")) not in (4, 5):
            continue
        stamp = None
        text = hdr.read_text(errors="ignore")
        d = re.search(r"Date[^:=]*[:=]\s*([0-9\-]+)", text)
        t = re.search(r"Time[^:=]*[:=]\s*([0-9:\.]+)", text)
        if d and t:
            stamp = d.group(1) + "T" + t.group(1)
        cubes.append({"hdr": hdr, "name": hdr.stem, "seq": _sequence_number(hdr.stem),
                      "stamp": stamp})
    cubes.sort(key=lambda c: (0, c["stamp"], c["seq"]) if c["stamp"]
               else (1, "", c["seq"]) if c["seq"] >= 0 else (2, c["name"], 0))
    for k, c in enumerate(cubes):
        c["index"], c["t_s"] = k, k * dt_s
    return cubes


def band_index(wavelengths: np.ndarray, nm: float) -> int:
    """Index of the band closest to ``nm``."""
    return int(np.argmin(np.abs(np.asarray(wavelengths) - nm)))
