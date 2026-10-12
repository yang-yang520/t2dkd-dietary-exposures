# Dietary exposures and burden of type 2 diabetic kidney disease

Analysis code and derived data for the manuscript:

> **Dietary exposures and burden of type 2 diabetic kidney disease**
> (submitted to *Kidney International Reports*)

## Overview

Ecological analysis of 185 countries (1990–2018 dietary exposures; 1990–2023 comparative risk
assessment) linking national dietary exposures to type 2 diabetic kidney disease (T2DKD) burden,
using random forest models with SHAP interpretation, plus a GBD comparative risk assessment.

## Data sources (publicly available)

- **Dietary exposures** — Global Dietary Database (GDD), 2018 release, 185 countries, 1990–2018
  (https://www.globaldietarydatabase.org)
- **Burden, risk exposures, attributable fractions, SDI** — Global Burden of Disease (GBD) 2023,
  cause id 998 (chronic kidney disease due to type 2 diabetes mellitus)
  (https://vizhub.healthdata.org/gbd-results/)

Raw downloads are NOT redistributed here (they are freely available from the sources above).
`data/` contains the **derived datasets** used in the analyses.

## Environment

```
pip install -r requirements.txt
```
Python 3.9.13; scikit-learn 1.6.1; shap 0.49.1; numpy 2.0.2; pandas 2.3.3; joblib 1.5.3.

## Code

| Script | Purpose |
|---|---|
| `model_v2.py` | Primary random forest regression + SHAP/permutation, GroupKFold & LOCO |
| `rerun_metrics.py` | Recompute country-grouped cross-validation performance |
| `rank_stability2.py` | Bootstrap SHAP rank stability (100 country-level resamples) |
| `heldout_perm.py` | Permutation importance on held-out countries within CV folds |
| `boot_imp.py` | Bootstrap distributions of SHAP importance values |
| `perm_null2.py` | Country-level label-permutation null test |
| `cluster_boot.py` | Country-clustered bootstrap for the lead–lag association |
| `cra_master.py` / `cra_ui.py` / `total_burden.py` | GBD CRA data assembly, 95% UIs, total burden |
| `quadrant_table.py` | Quadrant classification (Figure 5 sensitivity) |
| `make_min_figs.py`, `make_fig2_min.py`, `make_fig45_upgrade.py` | Figures 1–5 |
| `make_v16_ekir.py` | Assembling the manuscript in the journal's format |

## Reproducibility

All random seeds are fixed at 123 for model fitting, permutation importance and the permutation
test, and 123 + i for the i-th bootstrap resample. Every model evaluation uses country-grouped
cross-validation so that all observations of a country are held out together.

## Citation

If you use this code, please cite the manuscript above. (DOI to be added upon publication.)
