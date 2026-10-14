# Visibility of a photoluminescent evacuation sign in smoke

Hyperspectral measurement, Monte Carlo radiative transfer simulation and a
visibility model.

Master's internship (6 months, March–August 2026) at **Cerema**
(Clermont-Ferrand), in partnership with **CETU** (Centre d'études des
tunnels). Master's in Photonics, Signal and Imaging, University of Angers.

*Version française du résumé plus bas.*

## Question

In a tunnel fire, users must reach an emergency exit on their own during the
first minutes. Smoke first hides the lighting, and therefore the signs that
only reflect it. A photoluminescent sign emits its own light without any
power supply, but French regulations do not yet provide for it. The question
was whether such a sign remains visible in smoke. Standards characterise these
signs after charging under 1000 lx, whereas a tunnel wall receives only 20 to
50 lx.

## Approach

```
 hyperspectral measurement ──► radiance map of the sign ──► emissive texture
                                                                  │
 visibility model (Adrian) ◄── luminance maps ◄── Monte Carlo simulation in smoke
```

1. **Measurement.** Snapshot hyperspectral camera (61 bands, 430–910 nm),
   LED source with a diffuser, charging illuminance of 31–36 lx checked at
   eight points. Five recordings of the decay, one image per second, for three
   charging times and three viewing angles.
2. **Processing (Python).** From hyperspectral cubes to spectra, decay curves
   and radiance maps; radiance-to-luminance conversion; EXR textures for the
   simulator, with an EXR encoder written in standard Python.
3. **Simulation.** Scene built in Blender; the measured radiance map is used
   as the emissive texture of the sign. More than 500 simulations run with
   SWEET, Cerema's Monte Carlo radiative transfer simulator, used as is
   (code not modified). 6000 samples per pixel, chosen from a convergence
   study.
4. **Visibility.** Adrian's visibility model implemented from the original
   publication and applied to seven regions of the sign, taking the smallest
   dimension of each region (worst case).

## Main results

| | Result |
|---|---|
| Sign (measured) | Emission peak at 518 nm. Same initial level after 5, 7 and 10 h of charging. Decay over 15 min fitted by two exponentials, time constants close to 100 s and 580 s. At most 8.6% difference between 0° and 40°. |
| No smoke (simulated) | Whole sign comfortably visible at the three observer positions (12.7 to 18.5 m). The arrow is at the detection threshold at the furthest position. |
| Smoke (simulated) | For a visibility of 2 to 10 m, no region of the sign reaches the detection threshold. At the closest position, the whole sign becomes detectable again at about 20 m of visibility in white smoke and 25 m in black smoke. |
| Attenuation law | The visibility level decreases exponentially with optical depth up to about 5; beyond, the simulated values stay above this law, especially in white smoke (attributed to multiple scattering, not demonstrated separately). |

## Validation and limits

- Without smoke, the simulation reproduces the measured map within 2.5% per
  region, with a statistical error of about 1%. This checks the input and
  output of the chain, **not** the calculation in smoke, which was not
  compared with any measurement.
- Assumptions: homogeneous smoke, single wavelength (550 nm), no tunnel walls
  or residual lighting, 23-year-old observer, smoke optical properties taken
  from studies of developed fires.
- The radiance-to-luminance conversion relies on a regression (R² = 0.925)
  valid within the measured range.
- Tests in real smoke belong to a later phase of the project.

## Repository contents

```
report/internship-report-2026-fr.pdf   full internship report (French, 97 pages)
src/plvis/                             processing library
    envi_io.py      memory-mapped reading of ENVI cubes, sequence ordering
    photometry.py   CIE V(lambda), luminance, band integrals
    decay.py        two-exponential fit, time to half level
    exr.py          minimal OpenEXR writer and reader (float, uncompressed)
    regression.py   radiance-luminance regressions
    angular.py      comparison of viewing angles
    comparison.py   simulation vs measurement, scaling to a reference curve
    series.py       time series of a region over a sequence of cubes
scripts/                               command-line tools built on the library
examples/make_synthetic_data.py        synthetic cubes to try the tools
tests/                                 automatic tests (synthetic data)
docs/notes-on-the-code.md              changes and corrections made for publication
```

The radiative transfer simulator used in the project belongs to Cerema and is
not included. No measured data is published here: the full hyperspectral
dataset (more than 700 GB) was handed over to the laboratory.

## Running the tools

```bash
pip install -r requirements.txt
python examples/make_synthetic_data.py demo_cubes
python scripts/decay_series.py demo_cubes --roi 10:30,12:48 --out results
python scripts/cube_to_exr.py demo_cubes/demo_0000.hdr --roi 0:40,0:60 --luminance --out results/sign.exr
python scripts/radiance_vs_luminance.py demo_cubes/demo_0000.hdr --roi 0:40,0:60
python -m pytest -q tests
```

Regions are given as `row0:row1,col0:col1` in pixels. Wavelengths are read
from the ENVI header; if missing, a 61-band grid from 430 to 910 nm is used.

## My role

I carried out the experimental and numerical work on my own, with weekly
meetings at Cerema and meetings every two to three weeks with both teams.
The sign studied, the observer positions and the overall project framework
were set by the project specification.

## Résumé en français

Stage de Master 2 au Cerema (Clermont-Ferrand), avec le CETU, de mars à
août 2026. Mesure hyperspectrale d'un panneau d'évacuation photoluminescent,
simulation Monte Carlo du transfert radiatif dans la fumée (plus de 500
simulations avec SWEET) et application du modèle de visibilité d'Adrian.
Sans fumée, le panneau est visible aux trois positions ; pour une visibilité
de 2 à 10 m, aucune région n'atteint le seuil de détection. Le rapport complet
est dans `report/`.

## Author

Mouhssine Ait Said — [LinkedIn](https://www.linkedin.com/in/mouhssine-ait-said-111b03186/)

Publication of the report authorised by Cerema and CETU.

## Licence

Code: MIT (see `LICENSE`). The report and figures remain the work of the
author within the Cerema/CETU project; they may be read and cited, not reused
without permission.
