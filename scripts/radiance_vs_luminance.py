"""Pixel-by-pixel relation between radiance at one band and luminance.

    python scripts/radiance_vs_luminance.py CUBE.hdr --roi 375:750,0:1080 --nm 550

Fits linear, power and quadratic models of L_v against L_e(nm) and prints them,
best R2 first. Such a relation is only valid within the radiance range measured.
"""
import argparse
import json

import _common
from plvis import photometry as ph
from plvis.envi_io import band_index, open_cube
from plvis.regression import compare_models


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("hdr")
    p.add_argument("--roi", type=_common.roi_arg, required=True)
    p.add_argument("--nm", type=float, default=550.0)
    a = p.parse_args()

    cube = open_cube(a.hdr, _common.DEFAULT_WAVELENGTHS)
    block = cube.roi(*a.roi)
    x = block[:, :, band_index(cube.wavelengths, a.nm)].ravel()
    y = ph.luminance(block, cube.wavelengths).ravel()
    keep = (x > 0) & (y > 0)
    result = {"n_pixels": int(keep.sum()), "models": compare_models(x[keep], y[keep])}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
