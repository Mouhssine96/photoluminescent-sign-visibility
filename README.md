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
src/                                   Python processing code (being added)
data/                                  small sample data (being added)
figures/                               main figures (being added)
docs/                                  notes on the method
```

SWEET is Cerema's software and is not included. The full hyperspectral
dataset (more than 700 GB) was handed over to the laboratory and is not
published here.

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
