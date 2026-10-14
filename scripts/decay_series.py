"""Decay of a region of interest over a sequence of radiance cubes.

    python scripts/decay_series.py CUBE_FOLDER --roi 500:600,750:800 --out results/

Writes results/decay_series.csv (one row per cube), results/decay_fit.json
(two-exponential fit of the luminance) and results/decay.png.
"""
import argparse
import csv
import json
from pathlib import Path

import _common
from plvis import decay
from plvis.envi_io import find_cubes
from plvis.series import roi_time_series


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("folder")
    p.add_argument("--roi", type=_common.roi_arg, required=True, help="row0:row1,col0:col1")
    p.add_argument("--dt", type=float, default=1.0, help="time step between cubes (s)")
    p.add_argument("--pl-band", type=float, nargs=2, default=(500, 560), metavar=("MIN", "MAX"))
    p.add_argument("--out", default="results")
    a = p.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cubes = find_cubes(a.folder, a.dt)
    if not cubes:
        raise SystemExit("no radiance cube found")
    rows = roi_time_series(cubes, a.roi, _common.DEFAULT_WAVELENGTHS, tuple(a.pl_band))
    with open(out / "decay_series.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    t = [r["time_s"] for r in rows]
    lv = [r["luminance_cd_m2"] for r in rows]
    fit = decay.fit_biexp(t, lv)
    summary = {"n_cubes": len(rows), "luminance_t0_cd_m2": lv[0],
               "t_half_s": decay.time_to_fraction(t, lv, 0.5),
               "fit": None if fit is None else vars(fit)}
    (out / "decay_fit.json").write_text(json.dumps(summary, indent=2))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t, lv, "o", ms=2, label="measured")
    if fit is not None:
        ax.plot(t, fit([x - t[0] for x in t]), "-",
                label=f"fit: tau1={fit.tau1:.0f} s, tau2={fit.tau2:.0f} s, R2={fit.r2:.4f}")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("luminance (cd/m2)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "decay.png", dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
