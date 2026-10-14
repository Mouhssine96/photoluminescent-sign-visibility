"""Compare simulated monochromatic radiances with measured spectra.

    python scripts/compare_simulation.py simulated.csv measured_spectra.csv --nm 550

simulated.csv: columns region, radiance (W m^-2 sr^-1 um^-1 at --nm).
measured_spectra.csv: column wavelength_nm, then one column per region.
"""
import argparse
import csv

import numpy as np

import _common  # noqa: F401
from plvis.comparison import compare_at_wavelength


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("simulated")
    p.add_argument("measured")
    p.add_argument("--nm", type=float, default=550.0)
    a = p.parse_args()

    with open(a.simulated) as f:
        sim = {r["region"]: float(r["radiance"]) for r in csv.DictReader(f)}
    with open(a.measured) as f:
        rows = list(csv.DictReader(f))
    wl = np.array([float(r["wavelength_nm"]) for r in rows])
    spectra = {k: np.array([float(r[k]) for r in rows]) for k in rows[0] if k != "wavelength_nm"}

    res = compare_at_wavelength(sim, spectra, wl, a.nm)
    for name, r in res.items():
        print(f"{name:12s} sim {r['simulated']:.4g}  meas {r['measured']:.4g}  "
              f"diff {100 * r['relative_difference']:+.1f} %  (band {r['band_nm']:.0f} nm)")


if __name__ == "__main__":
    main()
