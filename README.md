# Nadocast (experimental)

Grid-based probabilistic tornado forecasting model.

## What this is
A research tornado forecasting pipeline inspired by SPC outlooks and NadoCast,
but trained and verified against confirmed tornado reports.

## Current status
- ✅ SPC tornado reports ingestion
- ✅ Point → grid labeling (25 mi radius)
- ✅ Baseline probabilistic model (v0)
- ⏳ Meteorological features (ERA5 / CAMs) — next

## Pipeline (v0)
```bash
python 01_fetch.py
python 02_compute_tpi.py
python 04_make_grid_and_labels.py
python 05_make_features_v0.py
python 06_train_model_v0.py
python 07_forecast_day_v0.py
