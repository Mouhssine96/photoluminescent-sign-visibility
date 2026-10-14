"""Angular behaviour of an emitting surface.

For a Lambertian emitter the *radiance* does not depend on the viewing angle
(it is the intensity of the whole surface that falls as cos beta). The
reference ratio L(beta)/L(0) is therefore 1, not cos(beta).
"""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


def angular_ratios(curves: Dict[float, Tuple[np.ndarray, np.ndarray]],
                   reference_angle: float = 0.0) -> Dict[float, np.ndarray]:
    """Ratio L(beta, t) / L(reference, t) on the time grid of the reference curve.

    ``curves`` maps an angle in degrees to (time_s, radiance).
    """
    t_ref, l_ref = (np.asarray(a, float) for a in curves[reference_angle])
    out = {}
    for angle, (t, l) in curves.items():
        if angle == reference_angle:
            continue
        out[angle] = np.interp(t_ref, np.asarray(t, float), np.asarray(l, float)) / l_ref
    return out


def max_relative_spread(values) -> float:
    """(max - min) / max of a set of values, e.g. initial radiances at several angles."""
    v = np.asarray(values, float)
    return float((v.max() - v.min()) / v.max())
