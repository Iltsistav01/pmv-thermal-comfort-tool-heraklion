"""
Global / Bell-Curve diagrams  (Σχήματα 7–16)
---------------------------------------------
PMV (X) vs. electricity consumption (Y) grouped into three outdoor-temperature
bands (low / mid / high) with equal active-hour counts (~972–979 h/band).

Produces for each band:
    • RAW  diagram  – absolute kWh vs PMV with 2nd-degree polynomial fit
    • Norm 1        – per-residence normalisation  (each residence / its own max)
    • Norm 2        – per-band normalisation       (each point / band max per PMV bin)

Then produces the GLOBAL diagrams (Σχήματα 15–16):
    • Global Norm 1 – all three band curves on one plot, globally normalised
    • Global Norm 2 – same, each band normalised to its own max

Data source : summer.xlsx  /  Winter_period.xlsx
Libraries   : pandas, numpy, matplotlib, scipy  (Anaconda environment)

Usage: set SEASON at the top.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data_loader import load_summer, load_winter, SUMMER_FILE, WINTER_FILE

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
SEASON = "Summer"   # "Summer" or "Winter"

# PMV bin width (0.5 units as in the thesis)
PMV_STEP  = 0.5
PMV_EDGES = np.arange(-3.25, 3.26, PMV_STEP)
PMV_MIDS  = PMV_EDGES[:-1] + PMV_STEP / 2

BAND_COLORS = {"Low": "blue", "Mid": "orange", "High": "purple"}
TARGET_HOURS = 972   # equal-count target per band (~thesis value)

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD + BUILD LONG FORMAT
# ─────────────────────────────────────────────────────────────────────────────
if SEASON == "Summer":
    df_wide   = load_summer(SUMMER_FILE)
    residences = ["S1", "S2", "S3", "S4"]
else:
    df_wide   = load_winter(WINTER_FILE)
    residences = ["W1", "W2", "W3", "W4"]

frames = []
for res in residences:
    ec  = f"{res}_Elec_kWh"
    pc  = f"{res}_PMV"
    if ec not in df_wide.columns or pc not in df_wide.columns:
        continue
    sub = df_wide[["datetime", "T_amb", ec, pc]].copy()
    sub = sub.rename(columns={ec: "Elec_kWh", pc: "PMV"})
    sub["residence"] = res
    frames.append(sub)

df = pd.concat(frames, ignore_index=True)
df = df.dropna(subset=["PMV", "T_amb"])
df["Elec_kWh"] = pd.to_numeric(df["Elec_kWh"], errors="coerce")
df_active = df[df["Elec_kWh"] > 0].copy()

# ─────────────────────────────────────────────────────────────────────────────
# 2. DEFINE EQUAL-COUNT TEMPERATURE BANDS
#    Split the sorted T_amb into three groups with ~equal active hours.
# ─────────────────────────────────────────────────────────────────────────────
sorted_tamb = df_active["T_amb"].sort_values().reset_index(drop=True)
n_total     = len(sorted_tamb)
cut1        = n_total // 3
cut2        = 2 * n_total // 3

T_BANDS = [
    ("Low",  sorted_tamb.iloc[0],        sorted_tamb.iloc[cut1]),
    ("Mid",  sorted_tamb.iloc[cut1],     sorted_tamb.iloc[cut2]),
    ("High", sorted_tamb.iloc[cut2],     sorted_tamb.iloc[-1] + 0.001),
]
print("Temperature bands:")
for name, lo, hi in T_BANDS:
    n = ((df_active["T_amb"] >= lo) & (df_active["T_amb"] < hi)).sum()
    print(f"  {name}: [{lo:.2f} – {hi:.2f}°C]  active hours = {n}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def bin_and_sum(df_band, residence=None):
    """Return array of summed Elec_kWh per PMV mid-point."""
    sub = df_band if residence is None else df_band[df_band["residence"] == residence]
    sub = sub.copy()
    sub["bin"] = pd.cut(sub["PMV"], bins=PMV_EDGES, labels=PMV_MIDS, right=False)
    agg = sub.groupby("bin", observed=False)["Elec_kWh"].sum()
    return agg.values.astype(float)

def fit_poly2(x, y):
    """2nd-degree polynomial fit; return (coeffs, R², x_dense, y_fit_clipped)."""
    mask = np.isfinite(x) & np.isfinite(y) & (y > 0)
    if mask.sum() < 3:
        return None, None, None, None
    xm, ym    = x[mask], y[mask]
    coeffs    = np.polyfit(xm, ym, 2)
    y_pred    = np.polyval(coeffs, xm)
    ss_res    = np.sum((ym - y_pred) ** 2)
    ss_tot    = np.sum((ym - ym.mean()) ** 2)
    r2        = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    xd        = np.linspace(xm.min(), xm.max(), 300)
    yd        = np.clip(np.polyval(coeffs, xd), 0, None)
    return coeffs, r2, xd, yd

# ─────────────────────────────────────────────────────────────────────────────
# 4. PER-BAND PLOTS  (Σχήματα 9-14 equivalent)
# ─────────────────────────────────────────────────────────────────────────────
band_fit_results = {}   # store for global plots later

for band_name, t_lo, t_hi in T_BANDS:
    mask_b  = (df_active["T_amb"] >= t_lo) & (df_active["T_amb"] < t_hi)
    df_band = df_active[mask_b].copy()

    # ── RAW (aggregate across all residences) ─────────────────────────────────
    y_raw = bin_and_sum(df_band)

    # ── Norm 1: per-residence (each / its own max) ────────────────────────────
    norm1_points = {"x": [], "y": []}
    for res in residences:
        y_r = bin_and_sum(df_band, res)
        mx  = np.nanmax(y_r) if np.nanmax(y_r) > 0 else np.nan
        if np.isfinite(mx):
            norm1_points["x"].extend(PMV_MIDS)
            norm1_points["y"].extend(y_r / mx)

    # ── Norm 2: per-band (each bin / that bin's cross-residence max) ──────────
    norm2_points = {"x": [], "y": []}
    all_res_bins  = np.vstack([bin_and_sum(df_band, r) for r in residences])
    bin_max        = np.nanmax(all_res_bins, axis=0)
    bin_max[bin_max == 0] = np.nan
    for row in all_res_bins:
        norm2_points["x"].extend(PMV_MIDS)
        norm2_points["y"].extend(row / bin_max)

    # ── Plot three variants ───────────────────────────────────────────────────
    for variant, px, py, ylabel in [
        ("RAW",   PMV_MIDS,                y_raw,
         "Electricity Consumption (kWh)"),
        ("Norm1", np.array(norm1_points["x"]), np.array(norm1_points["y"]),
         "Normalised Electricity (per-residence)"),
        ("Norm2", np.array(norm2_points["x"]), np.array(norm2_points["y"]),
         "Normalised Electricity (per-band)"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.scatter(px, py, color=BAND_COLORS[band_name], s=25, alpha=0.55,
                   zorder=3, label="Data points")

        coeffs, r2, xd, yd = fit_poly2(np.asarray(px, float), np.asarray(py, float))
        if coeffs is not None:
            ax.plot(xd, yd, color="red", linewidth=2.2,
                    label=f"Poly fit  R²={r2:.2f}")
            band_fit_results[(band_name, variant)] = (coeffs, t_lo, t_hi)

        ax.axvline(x=0,    color="gray",   linestyle=":", linewidth=0.8)
        ax.axvline(x=0.5,  color="orange", linestyle="--", linewidth=0.6, alpha=0.6)
        ax.axvline(x=-0.5, color="orange", linestyle="--", linewidth=0.6, alpha=0.6)
        ax.set_xlabel("PMV Index", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(
            f"{SEASON} – Band {band_name}  [{t_lo:.1f}–{t_hi:.1f}°C]  |  {variant}",
            fontsize=11, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(linestyle="--", linewidth=0.4, alpha=0.6)
        plt.tight_layout()
        fname = f"Bell_{SEASON}_{band_name}_{variant}.jpg"
        plt.savefig(fname, dpi=300, bbox_inches="tight")
        print(f"  Saved: {fname}")
        plt.show()

# ─────────────────────────────────────────────────────────────────────────────
# 5. GLOBAL PLOTS  (Σχήματα 15–16)
# ─────────────────────────────────────────────────────────────────────────────
for variant_label in ["Norm1", "Norm2"]:
    fig, ax = plt.subplots(figsize=(10, 5))

    # Collect curve max values for global normalisation (Norm1 version)
    all_curve_maxes = []
    curves = {}
    xd_dense = np.linspace(-3, 3, 400)
    for band_name, t_lo, t_hi in T_BANDS:
        key = (band_name, variant_label)
        if key not in band_fit_results:
            continue
        coeffs, _, _ = band_fit_results[key]
        y_fit = np.clip(np.polyval(coeffs, xd_dense), 0, None)
        curves[band_name] = (y_fit, t_lo, t_hi)
        all_curve_maxes.append(y_fit.max())

    global_max = max(all_curve_maxes) if all_curve_maxes else 1.0

    for band_name, (y_fit, t_lo, t_hi) in curves.items():
        # Version 1 (Norm1): globally normalised → stacked appearance
        # Version 2 (Norm2): each band / its own max → all peaks at ~1
        if variant_label == "Norm1":
            y_plot = y_fit / global_max
        else:
            band_max = y_fit.max() if y_fit.max() > 0 else 1.0
            y_plot   = y_fit / band_max

        ax.plot(xd_dense, y_plot,
                color=BAND_COLORS[band_name], linewidth=2.4,
                label=f"{band_name} [{t_lo:.1f}–{t_hi:.1f}°C]")

    ax.axvline(x=0,    color="gray", linestyle=":",  linewidth=0.8)
    ax.axvline(x=0.5,  color="gray", linestyle="--", linewidth=0.6, alpha=0.5)
    ax.axvline(x=-0.5, color="gray", linestyle="--", linewidth=0.6, alpha=0.5)
    ax.set_xlabel("PMV Index", fontsize=11)
    ax.set_ylabel("Normalised Electricity (0–1)", fontsize=11)
    ax.set_ylim(bottom=0)
    ax.set_title(
        f"Global EL–PMV Curves  |  {SEASON}  |  {variant_label}\n"
        f"(polynomial 2nd-degree fit, grouped by outdoor-temperature band)",
        fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(linestyle="--", linewidth=0.4, alpha=0.6)
    plt.tight_layout()
    fname = f"Global_{SEASON}_{variant_label}.jpg"
    plt.savefig(fname, dpi=300, bbox_inches="tight")
    print(f"Saved: {fname}")
    plt.show()
