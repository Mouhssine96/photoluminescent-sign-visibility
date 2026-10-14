"""Simple regressions between two quantities, with their coefficient of determination."""
from __future__ import annotations

import numpy as np


def _r2(y, y_pred) -> float:
    return float(1.0 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))


def fit_linear(x, y) -> dict:
    a, b = np.polyfit(x, y, 1)
    return {"model": "linear", "a": float(a), "b": float(b), "r2": _r2(y, a * np.asarray(x) + b)}


def fit_power(x, y) -> dict:
    """y = a x^n, fitted in log-log space on strictly positive data."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    keep = (x > 0) & (y > 0)
    n, log_a = np.polyfit(np.log(x[keep]), np.log(y[keep]), 1)
    a = float(np.exp(log_a))
    return {"model": "power", "a": a, "n": float(n), "r2": _r2(y[keep], a * x[keep] ** n)}


def fit_poly2(x, y) -> dict:
    c = np.polyfit(x, y, 2)
    return {"model": "poly2", "coeffs": c.tolist(), "r2": _r2(y, np.polyval(c, x))}


def compare_models(x, y) -> list:
    """Linear, power and quadratic fits, best R2 first."""
    return sorted((fit_linear(x, y), fit_power(x, y), fit_poly2(x, y)),
                  key=lambda r: r["r2"], reverse=True)
