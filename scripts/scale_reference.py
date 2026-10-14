"""Scale a sparse reference decay curve onto a dense measured one.

    python scripts/scale_reference.py decay_series.csv reference.csv

reference.csv: columns time_s, luminance_cd_m2 (a few points). Prints the
ratio K at each reference time, its mean and its coefficient of variation.
"""
import argparse
import csv

import numpy as np

import _common  # noqa: F401
from plvis.comparison import scale_to_reference


def load(path, col):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    return np.array([float(r["time_s"]) for r in rows]), np.array([float(r[col]) for r in rows])


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("measured")
    p.add_argument("reference")
    a = p.parse_args()
    res = scale_to_reference(*load(a.measured, "luminance_cd_m2"),
                             *load(a.reference, "luminance_cd_m2"))
    for t, k in zip(res["t_ref"], res["k"]):
        print(f"t = {t:7.0f} s   K = {k:.4f}")
    print(f"K mean = {res['k_mean']:.4f}, CV = {100 * res['k_cv']:.1f} %")


if __name__ == "__main__":
    main()
