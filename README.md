# PMV Thermal Comfort & Energy Analysis — Heraklion, Crete

> **Thesis:** *Investigation of Energy Performance and Thermal Comfort in Residential Buildings through Processing of Energy Consumption and Indoor Air Property Time Series*  
> **Author:** Stavros Iltsidis ·  
> **Institution:** Hellenic Mediterranean University (ΕΛΜΕΠΑ) — Department of Mechanical Engineering  
> **Supervisor:** Assoc. Prof. Georgios M. Stavrakakis  

---

## Overview

This repository contains all Python code used to produce the diagrams in the above thesis. The study analyses **hourly time-series data** from 8 residential dwellings in Heraklion, Crete (4 summer, 4 winter) to investigate the relationship between the **PMV/PPD thermal-comfort index** (Fanger / ISO 7730 / ASHRAE 55) and **electricity consumption**, under real Mediterranean climate conditions.

---

## Diagrams Produced

| Script | Diagram | Description |
|--------|---------|-------------|
| `diagram_A_timeseries.py` | Fig. 2α/β | Indoor temperature (left Y) + RH & PMV (right Y) time series |
| `diagram_C_PMV_PPD.py` | Fig. 1α/β | PPD % (left Y, green) + PMV index (right Y, purple) |
| `diagram_B_weekly_bar.py` | Fig. 5–6 | Weekly electricity bars + outdoor temperature + PMV |
| `heatmap_PMV_temporal.py` | Fig. 3A–3H | Temporal PMV heatmap — hour × week — all 8 residences |
| `rodogram_solar_radiation.py` | Fig. 2 (Εικόνα 2) | Polar hourly solar irradiance — YlOrRd, summer vs winter |
| `global_bell_PMV_electricity.py` | Fig. 7–16 | Bell-shaped PMV–electricity curves, 3 temperature bands |

---

## Repository Structure

```
pmv-thermal-comfort/
├── config.py                        ← edit this once with your file paths
├── data_loader.py                   ← shared loading utilities
├── diagram_A_timeseries.py
├── diagram_B_weekly_bar.py
├── diagram_C_PMV_PPD.py
├── heatmap_PMV_temporal.py
├── rodogram_solar_radiation.py
├── global_bell_PMV_electricity.py
├── requirements.txt
├── .gitignore
├── data/                            ← NOT included — add your own files here
│   ├── summer.xlsx
│   ├── Winter_period.xlsx
│   └── PMV_time_series_macros_S1.xlsm  (Diagram C only)
└── outputs/                         ← created automatically, diagrams saved here
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/pmv-thermal-comfort.git
cd pmv-thermal-comfort

# 2. Create and activate a conda environment
conda create -n pmv_env python=3.11
conda activate pmv_env

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Quick Start

**Step 1 — Add your data**

Create a `data/` folder and place your files inside. The folder is listed in `.gitignore` so your data will never be pushed to GitHub.

```
data/
├── summer.xlsx
├── Winter_period.xlsx
└── PMV_time_series_macros_S1.xlsm   (only needed for Diagram C)
```

**Step 2 — Edit `config.py` once**

```python
SUMMER_FILE = "data/summer.xlsx"
WINTER_FILE = "data/Winter_period.xlsx"
OUTPUT_DIR  = "outputs"
```

**Step 3 — Run any diagram**

```bash
python heatmap_PMV_temporal.py          # all 8 heatmaps
python diagram_B_weekly_bar.py          # weekly bar chart
python global_bell_PMV_electricity.py   # bell-curve / global plots
```

Saved images appear in `outputs/` at 300 DPI.

---

## Changing Residence or Season

Every diagram script has a small **CONFIGURATION block** at the top — the only lines you need to change per run:

```python
# ── CONFIGURATION ──────────────────────────────
RESIDENCE = "S1"      # "S1" | "S2" | "S3" | "S4"  (summer)
                      # "W1" | "W2" | "W3" | "W4"  (winter)
SEASON    = "Summer"  # "Summer" or "Winter"
# ───────────────────────────────────────────────
```

---

## Methodology Summary

- **PMV/PPD** computed with Fanger's model (ISO 7730 / ASHRAE 55) inside Excel workbooks.
- **Outdoor temperature** from meteorological data — stored in the yellow-highlighted column of the consolidated Excel files.
- **Solar irradiance** from the SARAH-2/SARAH-3 satellite product (CM SAF), Heraklion location.
- **Polynomial regression** (2nd degree) fitted to PMV–electricity pairs grouped by three equal-count outdoor-temperature bands.
- **Two normalisations**: per-residence (Norm 1) and per-band (Norm 2).

---

## Citation

If you use this code, please cite:

> Iltsidis, S. (2025). *Investigation of Energy Performance and Thermal Comfort in Residential Buildings through Processing of Energy Consumption and Indoor Air Property Time Series*. Undergraduate Thesis, Department of Mechanical Engineering, Hellenic Mediterranean University.

---

## License

MIT — see [LICENSE](LICENSE) for details.
