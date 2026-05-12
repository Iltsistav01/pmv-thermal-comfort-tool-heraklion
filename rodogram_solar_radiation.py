"""
Rodogram – Polar hourly solar irradiance diagram  (Εικόνα 2)
-------------------------------------------------------------
Two polar subplots side-by-side:
    Left  : Summer period  (Jun–Sep 2023)
    Right : Winter period  (Oct 2022 – Mar 2023)

Polar axes:
    Angular axis  → hour of the day (0–23 h, clockwise from top)
    Radial axis   → mean solar irradiance (kWh/m²) for that hour
    Colour        → irradiance magnitude  ('YlOrRd' palette)
                    yellow = low,  red = high
    Colourbar     → on the right, shared scale

Data source:  SARAH-2 / SARAH-3 satellite product, Heraklion location.
              Provide a CSV/Excel file with hourly columns:
                  datetime   – hourly timestamp
                  GHI        – global horizontal irradiance (kWh/m²)
              Set FILE_RADIATION below.

              If the file is not found the script runs with synthetic data
              so you can verify the plot style immediately.

Libraries: pandas, numpy, matplotlib  (Anaconda environment)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION  ← set your radiation file here
# ─────────────────────────────────────────────────────────────────────────────
FILE_RADIATION = "solar_radiation_heraklion.csv"   # columns: datetime, GHI

# Monitoring periods (adjust years to match your actual data)
SUMMER_START = "2023-06-01"
SUMMER_END   = "2023-09-30"
WINTER_START = "2022-10-26"
WINTER_END   = "2023-03-31"

# ─────────────────────────────────────────────────────────────────────────────
# LOAD RADIATION DATA
# ─────────────────────────────────────────────────────────────────────────────
try:
    df_rad = pd.read_csv(FILE_RADIATION)
    df_rad["datetime"] = pd.to_datetime(df_rad["datetime"], errors="coerce")
    df_rad["GHI"]      = pd.to_numeric(df_rad["GHI"], errors="coerce").fillna(0)
    df_rad = df_rad.dropna(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)
    print(f"Loaded radiation data: {len(df_rad)} rows.")
except FileNotFoundError:
    print(f"⚠  '{FILE_RADIATION}' not found.  Running with synthetic demo data.")
    hours  = pd.date_range("2022-10-26", "2023-09-30 23:00", freq="h")
    h_arr  = hours.hour
    doy    = hours.dayofyear
    amp    = 0.8 + 0.4 * np.cos(2 * np.pi * (doy - 172) / 365)
    ghi    = np.clip(amp * np.sin(np.pi * np.clip(h_arr - 5, 0, 14) / 14), 0, None) * 0.9
    df_rad = pd.DataFrame({"datetime": hours, "GHI": ghi})

df_rad["hour"] = df_rad["datetime"].dt.hour

# ─────────────────────────────────────────────────────────────────────────────
# SEASON MASKS
# ─────────────────────────────────────────────────────────────────────────────
mask_s = (df_rad["datetime"] >= SUMMER_START) & (df_rad["datetime"] <= SUMMER_END + " 23:59")
mask_w = (df_rad["datetime"] >= WINTER_START) & (df_rad["datetime"] <= WINTER_END + " 23:59")

seasons = [
    (f"Summer  ({SUMMER_START[:7]} – {SUMMER_END[:7]})",  df_rad[mask_s].copy()),
    (f"Winter  ({WINTER_START[:7]} – {WINTER_END[:7]})",  df_rad[mask_w].copy()),
]

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL COLOUR SCALE  (shared across both subplots)
# ─────────────────────────────────────────────────────────────────────────────
gmax = 0
for _, df_s in seasons:
    hm = df_s.groupby("hour")["GHI"].mean()
    if len(hm) and hm.max() > gmax:
        gmax = hm.max()
norm_global = mcolors.Normalize(vmin=0, vmax=gmax if gmax > 0 else 1)
cmap        = cm.get_cmap("YlOrRd")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                          subplot_kw={"projection": "polar"})

bar_width = 2 * np.pi / 24   # one bar per hour

for ax, (title, df_s) in zip(axes, seasons):
    hourly_mean = df_s.groupby("hour")["GHI"].mean().reindex(range(24), fill_value=0)
    h_vals = hourly_mean.index.values.astype(float)
    r_vals = hourly_mean.values

    # Angle: 0 h at top, clockwise
    theta_plot = np.pi / 2 - 2 * np.pi * h_vals / 24
    colours    = [cmap(norm_global(v)) for v in r_vals]

    for th, rad, col in zip(theta_plot, r_vals, colours):
        ax.bar(th, rad, width=bar_width, color=col, edgecolor="none", alpha=0.95)

    # Axis styling
    ax.set_theta_zero_location("N")   # 0 h at top
    ax.set_theta_direction(-1)         # clockwise
    hour_ticks = np.arange(0, 24, 3)
    ax.set_thetagrids(
        [h_ * 360 / 24 for h_ in hour_ticks],
        labels=[f"{int(h_):02d}:00" for h_ in hour_ticks],
        fontsize=8)
    ax.set_ylabel("kWh/m²", labelpad=30, fontsize=8)
    ax.set_title(title, va="bottom", fontsize=10, fontweight="bold", pad=18)

# Shared colourbar
sm = cm.ScalarMappable(cmap="YlOrRd", norm=norm_global)
sm.set_array([])
cbar = fig.colorbar(sm, ax=axes, orientation="vertical",
                    fraction=0.025, pad=0.08, shrink=0.75)
cbar.set_label("Mean Solar Irradiance (kWh/m²)", fontsize=9)

fig.suptitle(
    "Rodogram – Hourly Incident Solar Irradiance  |  Heraklion, Crete",
    fontsize=12, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("Rodogram_solar_radiation.jpg", dpi=300, bbox_inches="tight")
plt.show()
