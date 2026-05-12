"""
Diagram C – PMV / PPD time-series  (Σχήμα 1α / 1β)
-----------------------------------------------------
Left  Y-axis : PPD index (%)  – green line     (reads from .xlsm model files)
Right Y-axis : PMV index      – purple line

NOTE: PPD is available in the individual xlsm calculation workbooks only.
      Make sure the relevant .xlsm file is in the same folder as this script.

Data source  : PMV_time_series_macros_S1.xlsm  (sheet "Model-S_1",  header row 3)
               PMV_time_series_macros_W1.xlsm  (sheet "Model-example", header row 3)
               etc.

Libraries    : pandas, matplotlib  (Anaconda environment)

Usage: set FILE_PATH, SHEET_NAME, RESIDENCE_LABEL, SEASON and run.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
FILE_PATH       = "PMV_time_series_macros_S1.xlsm"
SHEET_NAME      = "Model-S_1"       # "Model-example" for S2-S4, W1-W4
HEADER_ROW      = 3                 # 0-indexed
RESIDENCE_LABEL = "S-1"
SEASON          = "Summer"

# ─────────────────────────────────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────────────────────────────────
df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME, header=HEADER_ROW)

# Map columns by exact name match
col_map = {}
for c in df.columns:
    if "date" in str(c).strip().lower():
        col_map[c] = "datetime"
    if str(c).strip() == "PMV":
        col_map[c] = "PMV"
    if str(c).strip() == "PPD":
        col_map[c] = "PPD"

df = df.rename(columns=col_map)
df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
df["PMV"]      = pd.to_numeric(df["PMV"], errors="coerce")
df["PPD"]      = pd.to_numeric(df["PPD"], errors="coerce")
df = df.dropna(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)

# ─────────────────────────────────────────────────────────────────────────────
# PLOT
# ─────────────────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(14, 5))

# Left Y: PPD (green)
ax1.set_xlabel("Date", fontsize=11)
ax1.set_ylabel("PPD (%)", color="green", fontsize=11)
ax1.plot(df["datetime"], df["PPD"], color="green", linewidth=0.9, label="PPD (%)")
ax1.tick_params(axis="y", labelcolor="green")
ax1.set_ylim(0, 105)
ax1.axhline(y=10, color="green", linestyle=":", linewidth=0.8, alpha=0.7)  # 10% threshold
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right")
ax1.yaxis.set_minor_locator(AutoMinorLocator())
ax1.grid(axis="x", linestyle="--", linewidth=0.4, alpha=0.6)

# Right Y: PMV (purple)
ax2 = ax1.twinx()
ax2.set_ylabel("PMV index", color="purple", fontsize=11)
ax2.plot(df["datetime"], df["PMV"], color="purple", linewidth=0.9, label="PMV index")
ax2.tick_params(axis="y", labelcolor="purple")
ax2.set_ylim(-3.5, 3.5)
ax2.axhline(y=0,    color="gray",   linestyle=":",  linewidth=0.8)
ax2.axhline(y=0.5,  color="orange", linestyle="--", linewidth=0.6, alpha=0.7)
ax2.axhline(y=-0.5, color="orange", linestyle="--", linewidth=0.6, alpha=0.7)

# Legend
l1, lb1 = ax1.get_legend_handles_labels()
l2, lb2 = ax2.get_legend_handles_labels()
ax1.legend(l1 + l2, lb1 + lb2, loc="upper center", bbox_to_anchor=(0.5, -0.22),
           ncol=2, fontsize=10, fancybox=True, shadow=True)

ax1.set_title(
    f"Residence {RESIDENCE_LABEL} – {SEASON}  |  PMV & PPD Thermal Comfort Indices",
    fontsize=12, fontweight="bold")
fig.tight_layout()
plt.savefig(f"Diagram_C_{RESIDENCE_LABEL}_{SEASON}.jpg", dpi=300, bbox_inches="tight")
plt.show()
