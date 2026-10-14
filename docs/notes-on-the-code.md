# Notes on the code

The modules in `src/plvis` are a reorganised version of the scripts written
during the internship. The physics and the processing steps are the same; the
changes below were made while preparing them for publication.

## What changed

| Topic | Internship scripts | This repository |
|---|---|---|
| Structure | One long script per analysis, paths and regions written in the code | A small library (`src/plvis`) and command-line scripts; paths and regions are arguments |
| ENVI reading | `spectral` package | Own memory-mapped reader (BIP, BIL, BSQ), no dependency beyond NumPy; only the region of interest is read |
| EXR writing | Encoder in standard Python | Same approach, plus a reader used to test that files round-trip exactly |
| Figures | Two colour themes per figure | One plain figure per analysis; styling left to the user |
| Data | Local file paths | No data published; `examples/make_synthetic_data.py` creates a synthetic sequence to try the scripts |
| Tests | None | 20 automatic tests on synthetic cubes, run on every push |

## Corrections

- **Angular reference.** One script compared L(beta)/L(0) with cos(beta). For a
  Lambertian emitter the *radiance* does not depend on the viewing angle; it is
  the intensity that falls as cos(beta). The reference ratio is therefore 1.
  This does not change the result reported (at most 8.6 % between 0 and 40
  degrees, compared with each other, not with cos(beta)).
- **Three-band "luminance".** One export computed a luminance from three single
  bands weighted by the sRGB coefficients. Spectral radiance at three
  wavelengths does not give a luminance; the luminance map is now computed with
  the full V(lambda) integral.
- **Column labels.** In one version, the RGB channel wavelengths had been
  changed but the CSV column names still showed the old ones. Labels are now
  generated from the bands actually used.
- **Simulation comparison.** An early version labelled a radiance as a
  luminance in the comparison with the simulation. Only radiance at 550 nm is
  compared, as in the final version.
- **V(lambda) table.** A few values at 400-405 nm and above 775 nm were
  replaced by the CIE 1931 values; the effect on the luminance is negligible.

## Units

Radiance is in W m-2 sr-1 um-1 and wavelengths in nm. The luminance integral
converts wavelengths to micrometres, so `L_v = 683.002 * integral(L_e V dlambda)`
is in cd m-2.

## Two-exponential fit

The decay model includes a constant offset c:
`L(t) = a1 exp(-t/tau1) + a2 exp(-t/tau2) + c`. The internship report gives the
formula without c; the time constants it reports were obtained with c.
