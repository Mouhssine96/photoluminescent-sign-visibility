"""Create a small synthetic sequence of radiance cubes to try the scripts.

    python examples/make_synthetic_data.py demo_cubes/

The cubes imitate a green photoluminescent emission (peak near 518 nm) that
decays with two exponentials, on a 40 x 60 pixel scene with a darker frame.
They are NOT measured data.
"""
import sys
from pathlib import Path

import numpy as np

WL = np.arange(430, 911, 8, dtype=float)


def main(out="demo_cubes", n=120, dt=1.0):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    spectrum = 0.0065 * np.exp(-0.5 * ((WL - 518) / 25) ** 2)
    mask = np.full((40, 60), 0.15)
    mask[8:32, 10:50] = 1.0
    rng = np.random.default_rng(0)
    header = ("ENVI\nsamples = 60\nlines = 40\nbands = 61\nheader offset = 0\n"
              "data type = 4\ninterleave = bip\nbyte order = 0\nwavelength = {"
              + ", ".join(f"{w:.0f}" for w in WL) + "}\n")
    for k in range(n):
        t = k * dt
        a = 0.6 * np.exp(-t / 30) + 0.4 * np.exp(-t / 200) + 0.02
        cube = a * mask[:, :, None] * spectrum[None, None, :]
        cube *= 1 + 0.01 * rng.standard_normal(cube.shape)
        cube.astype("<f4").tofile(out / f"demo_{k:04d}.raw")
        (out / f"demo_{k:04d}.hdr").write_text(header)
    print(f"{n} cubes written to {out}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
