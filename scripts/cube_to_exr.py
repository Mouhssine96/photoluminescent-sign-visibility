"""Export the radiance of one cube region as an EXR texture.

    python scripts/cube_to_exr.py CUBE.hdr --roi 375:750,0:1080 --bands 630 532 465 --out sign.exr

Each output channel is the radiance (W m^-2 sr^-1 um^-1) of the band closest to
the requested wavelength. A single band (e.g. --bands 550) gives a one-channel
file named Y. Also writes the luminance map (cd/m2) next to it with --luminance.
"""
import argparse

import _common
from plvis import photometry as ph
from plvis.envi_io import band_index, open_cube
from plvis.exr import write_exr


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("hdr")
    p.add_argument("--roi", type=_common.roi_arg, required=True)
    p.add_argument("--bands", type=float, nargs="+", default=[630, 532, 465])
    p.add_argument("--luminance", action="store_true", help="also export L_v (cd/m2)")
    p.add_argument("--out", default="radiance.exr")
    a = p.parse_args()

    cube = open_cube(a.hdr, _common.DEFAULT_WAVELENGTHS)
    idx = [band_index(cube.wavelengths, nm) for nm in a.bands]
    image = cube.roi(*a.roi, bands=idx)
    names = ("R", "G", "B") if len(idx) == 3 else ("Y",) if len(idx) == 1 else \
        tuple(f"B{int(cube.wavelengths[i])}" for i in idx)
    meta = {"unit": "W m-2 sr-1 um-1",
            "bands_nm": " ".join(f"{cube.wavelengths[i]:.0f}" for i in idx)}
    print("written", write_exr(a.out, image, names, meta))
    if a.luminance:
        lum = ph.luminance(cube.roi(*a.roi), cube.wavelengths)
        path = a.out.replace(".exr", "_luminance.exr")
        print("written", write_exr(path, lum, ("Y",), {"unit": "cd m-2"}))


if __name__ == "__main__":
    main()
