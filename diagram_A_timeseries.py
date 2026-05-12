"""
Diagram A – Composite time-series  (Σχήμα 2α / 2β)
----------------------------------------------------
Left  Y-axis : Indoor air temperature (°C)   – red line
Right Y-axis : Indoor relative humidity (%)  – blue dashed
               PMV index                     – purple line

Data source  : summer.xlsx  /  Winter_period.xlsx
Libraries    : pandas, matplotlib  (Anaconda environment)

Usage: set RESIDENCE and SEASON, then run.
    Summer residences: "S1", "S2", "S3", "S4"
    Winter residences: "W1", "W2", "W3", "W4"
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator
from data_loader import load_summer, load_winter, SUMMER_FILE, WINTER_FILE

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
RESIDENCE = "S1"
SEASON    = "Summer"   # "Summer" or "Winter"

# ─────────────────────────────────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────────────────────────────────
df = load_summer(SUMMER_FILE) if SEASON == "Summer" else load_winter(WINTER_FILE)
tair_col = f"{RESIDENCE}_Tair"
rh_col   = f"{RESIDENCE}_RH"
pmv_col  = f"{RESIDENCE}_PMV"

# ─────────────────────────────────────────────────────────────────────────────
# PLOT
# ─────────────────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(14, 5))

# Left Y: Indoor Temperature (red)
ax1.set_xlabel("Date", fontsize=11)
ax1.set_ylabel("Indoor Temperature (°C)", color="tab:red", fontsize=11)
ax1.plot(df["datetime"], df[tair_col], color="tab:red", linewidth=0.8,
         label="Indoor Temperature (°C)")
ax1.tick_params(axis="y", labelcolor="tab:red")
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right")
ax1.yaxis.set_minor_locator(AutoMinorLocator())
ax1.grid(axis="x", linestyle="--", linewidth=0.4, alpha=0.6)

# Right Y: RH (blue dashed) + PMV (purple)
ax2 = ax1.twinx()
ax2.set_ylabel("Relative Humidity (%)  /  PMV index", fontsize=11)
ax2.plot(df["datetime"], df[rh_col], color="tab:blue", linewidth=0.8,
         linestyle="--", label="Indoor Relative Humidity (%)")
ax2.plot(df["datetime"], df[pmv_col], color="purple", linewidth=1.0,
         label="PMV index")
ax2.axhline(y=0,    color="gray",   linestyle=":",  linewidth=0.8)
ax2.axhline(y=0.5,  color="orange", linestyle="--", linewidth=0.6, alpha=0.7)
ax2.axhline(y=-0.5, color="orange", linestyle="--", linewidth=0.6, alpha=0.7)

# Legend
l1, lb1 = ax1.get_legend_handles_labels()
l2, lb2 = ax2.get_legend_handles_labels()
ax1.legend(l1 + l2, lb1 + lb2, loc="upper center", bbox_to_anchor=(0.5, -0.22),
           ncol=3, fontsize=9, fancybox=True, shadow=True)

ax1.set_title(
    f"Residence {RESIDENCE} – {SEASON}  |  Indoor Temperature / Relative Humidity / PMV",
    fontsize=12, fontweight="bold")
fig.tight_layout()
plt.savefig(f"Diagram_A_{RESIDENCE}_{SEASON}.jpg", dpi=300, bbox_inches="tight")
plt.show()
