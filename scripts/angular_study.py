"""Compare decay curves recorded at several viewing angles.

    python scripts/angular_study.py 0:series_0deg.csv 12:series_12deg.csv 40:series_40deg.csv

Each CSV is a decay_series.csv. For a Lambertian emitter the radiance ratio
L(beta)/L(0) is 1 at all times.
"""
import argparse
import csv

import numpy as np

import _common  # noqa: F401
from plvis.angular import angular_ratios, max_relative_spread


def load(path, column):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    return (np.array([float(r["time_s"]) for r in rows]),
            np.array([float(r[column]) for r in rows]))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("curves", nargs="+", help="ANGLE:FILE.csv")
    p.add_argument("--column", default="peak_radiance")
    a = p.parse_args()

    curves = {float(s.split(":", 1)[0]): load(s.split(":", 1)[1], a.column) for s in a.curves}
    initial = {ang: float(c[1][0]) for ang, c in curves.items()}
    print("initial values:", {k: round(v, 6) for k, v in initial.items()})
    print(f"max relative spread at t=0: {100 * max_relative_spread(list(initial.values())):.1f} %")
    for ang, r in angular_ratios(curves).items():
        print(f"L({ang:g})/L(0): mean {r.mean():.3f}, min {r.min():.3f}, max {r.max():.3f}")


if __name__ == "__main__":
    main()
