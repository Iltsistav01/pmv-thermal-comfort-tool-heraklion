"""
data_loader.py  –  shared data loading utilities
-------------------------------------------------
Reads file paths from config.py.
All diagram scripts import from here – do not edit paths here directly,
edit config.py instead.

Column layout returned
──────────────────────
Shared:   datetime | T_amb (°C, yellow column) | RH_amb (%)

Summer:   S1_Elec_kWh  S1_Elec_kWh_m2  S1_Tair  S1_RH  S1_PMV  (×4 residences)
Winter:   W1_Elec_kWh  W1_Tair  W1_RH  W1_PMV                   (×4 residences)
"""

import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from config import SUMMER_FILE, WINTER_FILE

# ── Column position maps (0-indexed) ──────────────────────────────────────────
_SUMMER_COLS = {
    0:  "datetime",
    1:  "T_amb",           # ← yellow column: Ambient air temperature (°C)
    2:  "RH_amb",
    3:  "S1_Elec_kWh",
    4:  "S1_Elec_kWh_m2",
    5:  "S1_Tair",
    6:  "S1_RH",
    7:  "S1_PMV",
    8:  "S2_Elec_kWh",
    9:  "S2_Elec_kWh_m2",
    10: "S2_Tair",
    11: "S2_RH",
    12: "S2_PMV",
    13: "S3_Elec_kWh",
    14: "S3_Elec_kWh_m2",
    15: "S3_Tair",
    16: "S3_RH",
    17: "S3_PMV",
    18: "S4_Elec_kWh",
    19: "S4_Elec_kWh_m2",
    20: "S4_Tair",
    21: "S4_RH",
    22: "S4_PMV",
}

_WINTER_COLS = {
    0:  "datetime",
    1:  "T_amb",           # ← yellow column: Ambient air temperature (°C)
    2:  "RH_amb",
    3:  "W1_Elec_kWh",
    4:  "W1_Tair",
    5:  "W1_RH",
    6:  "W1_PMV",
    7:  "W2_Elec_kWh",
    8:  "W2_Tair",
    9:  "W2_RH",
    10: "W2_PMV",
    11: "W3_Elec_kWh",
    12: "W3_Tair",
    13: "W3_RH",
    14: "W3_PMV",
    15: "W4_Elec_kWh",
    16: "W4_Tair",
    17: "W4_RH",
    18: "W4_PMV",
}


def _load(fpath, sheet_name, col_map):
    df = pd.read_excel(fpath, sheet_name=sheet_name, header=0)
    df = df.iloc[1:].reset_index(drop=True)   # row 0 contains the real headers
    rename = {df.columns[i]: name for i, name in col_map.items()
              if i < len(df.columns)}
    df = df.rename(columns=rename)
    df = df[[c for c in col_map.values() if c in df.columns]].copy()
    df["datetime"] = pd.to_datetime(df["datetime"], dayfirst=True, errors="coerce")
    for c in df.columns[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return (df.dropna(subset=["datetime"])
              .sort_values("datetime")
              .reset_index(drop=True))


def load_summer(fpath=None):
    """Return the summer consolidated DataFrame."""
    return _load(fpath or SUMMER_FILE, "Summer period", _SUMMER_COLS)


def load_winter(fpath=None):
    """Return the winter consolidated DataFrame."""
    return _load(fpath or WINTER_FILE, "Winter period", _WINTER_COLS)
