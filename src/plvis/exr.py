"""Minimal OpenEXR writer and reader, standard library + NumPy only.

Scope: single-part scanline images, 32-bit float channels, no compression.
This is enough to hand a radiance map to a renderer as an emissive texture
when the OpenEXR bindings cannot be installed.
"""
from __future__ import annotations

import struct
from pathlib import Path
from typing import Dict, Optional, Sequence

import numpy as np

MAGIC = 20000630
_FLOAT = 2


def _attr(name: str, typ: str, payload: bytes) -> bytes:
    return name.encode() + b"\0" + typ.encode() + b"\0" + struct.pack("<i", len(payload)) + payload


def write_exr(path, image: np.ndarray, channels: Sequence[str] = ("R", "G", "B"),
              metadata: Optional[Dict[str, str]] = None) -> Path:
    """Write ``image`` (H, W, C) as float32 EXR. Channel names follow ``channels``."""
    img = np.asarray(image, dtype="<f4")
    if img.ndim == 2:
        img = img[:, :, None]
    h, w, n = img.shape
    if len(channels) != n:
        raise ValueError("one channel name per image plane is required")
    order = sorted(range(n), key=lambda i: channels[i])  # EXR stores channels sorted by name
    chlist = b"".join(channels[i].encode() + b"\0" + struct.pack("<i", _FLOAT) + b"\0" * 4
                      + struct.pack("<ii", 1, 1) for i in order) + b"\0"
    box = struct.pack("<iiii", 0, 0, w - 1, h - 1)
    header = (struct.pack("<ii", MAGIC, 2)
              + _attr("channels", "chlist", chlist)
              + _attr("compression", "compression", b"\0")
              + _attr("dataWindow", "box2i", box)
              + _attr("displayWindow", "box2i", box)
              + _attr("lineOrder", "lineOrder", b"\0")
              + _attr("pixelAspectRatio", "float", struct.pack("<f", 1.0))
              + _attr("screenWindowCenter", "v2f", struct.pack("<ff", 0.0, 0.0))
              + _attr("screenWindowWidth", "float", struct.pack("<f", 1.0)))
    for k, v in (metadata or {}).items():
        header += _attr(str(k), "string", str(v).encode("ascii", "replace"))
    header += b"\0"
    line_bytes = w * 4 * n
    start = len(header) + 8 * h
    offsets = b"".join(struct.pack("<Q", start + y * (8 + line_bytes)) for y in range(h))
    body = bytearray()
    for y in range(h):
        body += struct.pack("<ii", y, line_bytes)
        for i in order:
            body += img[y, :, i].tobytes()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + offsets + bytes(body))
    return path


def read_exr(path) -> Dict[str, np.ndarray]:
    """Read an EXR written by :func:`write_exr` (uncompressed float only)."""
    data = Path(path).read_bytes()
    if struct.unpack_from("<i", data, 0)[0] != MAGIC:
        raise ValueError("not an OpenEXR file")
    pos, attrs = 8, {}
    while data[pos] != 0:
        end = data.index(b"\0", pos); name = data[pos:end].decode(); pos = end + 1
        end = data.index(b"\0", pos); typ = data[pos:end].decode(); pos = end + 1
        size = struct.unpack_from("<i", data, pos)[0]; pos += 4
        attrs[name] = (typ, data[pos:pos + size]); pos += size
    pos += 1
    if attrs["compression"][1] != b"\0":
        raise ValueError("only uncompressed files are supported")
    x0, y0, x1, y1 = struct.unpack("<iiii", attrs["dataWindow"][1])
    w, h = x1 - x0 + 1, y1 - y0 + 1
    names, raw = [], attrs["channels"][1]
    p = 0
    while raw[p] != 0:
        end = raw.index(b"\0", p); names.append(raw[p:end].decode()); p = end + 1 + 16
    offsets = struct.unpack_from(f"<{h}Q", data, pos)
    out = {n: np.empty((h, w), np.float32) for n in names}
    for y, off in enumerate(offsets):
        line = np.frombuffer(data, "<f4", count=w * len(names), offset=off + 8)
        for i, n in enumerate(names):
            out[n][y] = line[i * w:(i + 1) * w]
    return out
