# =============================================================================
#  config.py  –  USER CONFIGURATION
#  Fill in the paths below once, then all diagram scripts will work.
# =============================================================================

# ── Data files ────────────────────────────────────────────────────────────────
# Path to your consolidated summer data file (summer.xlsx)
SUMMER_FILE = "data/summer.xlsx"

# Path to your consolidated winter data file (Winter_period.xlsx)
WINTER_FILE = "data/Winter_period.xlsx"

# Path to the solar radiation CSV (SARAH-2/3 data, for the Rodogram only)
# Columns required:  datetime  |  GHI  (kWh/m²)
# Leave as "" if you do not have this file – the rodogram will use demo data.
SOLAR_FILE = "data/solar_radiation_heraklion.csv"

# ── Individual xlsm model files (needed only for Diagram C – PPD) ─────────────
# Key = residence ID,  Value = (file_path, sheet_name, header_row)
XLSM_FILES = {
    "S1": ("data/PMV_time_series_macros_S1.xlsm", "Model-S_1",      3),
    "S2": ("data/PMV_time_series_macros_S2.xlsm", "Model-example",  3),
    "S3": ("data/PMV_time_series_macros_S3.xlsm", "Model-example",  3),
    "S4": ("data/PMV_time_series_macros_S4.xlsm", "Model-example",  3),
    "W1": ("data/PMV_time_series_macros_W1.xlsm", "Model-example",  3),
    "W2": ("data/PMV_time_series_macros_W2.xlsm", "Model-example",  3),
    "W3": ("data/PMV_time_series_macros_W3.xlsm", "Model-example",  3),
    "W4": ("data/pmv_time_series_macros_w4.xlsm", "Model-example",  3),
}

# ── Output folder ─────────────────────────────────────────────────────────────
# All saved diagrams (.jpg) will go here.  Created automatically if missing.
OUTPUT_DIR = "outputs"

# ── Monitoring periods ────────────────────────────────────────────────────────
SUMMER_START = "2023-06-01"
SUMMER_END   = "2023-09-30"
WINTER_START = "2022-10-26"
WINTER_END   = "2023-03-31"
