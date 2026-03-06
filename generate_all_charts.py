"""
generate_all_charts.py
----------------------
Generates all integration and CPI-adjusted charts for the
Alberta Population vs Education Spending analysis.

Outputs are saved to plots/ at 300 DPI (publication quality).
A combined CSV is exported to budget_data/population_vs_spending.csv.

Data sources:
  - Population: Statistics Canada Table 17-10-0009-01 (via alberta_yoy_growth.csv)
  - Spending: Alberta Budget Fiscal Plans (via spending_data.csv)
  - CPI: Alberta All-Items CPI, Statistics Canada Table 18-10-0005-01
         (annual averages, 2002=100), retrieved from Alberta Economic Dashboard API
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ── Ensure output directories exist ─────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(SCRIPT_DIR, "plots")
BUDGET_DIR = os.path.join(SCRIPT_DIR, "budget_data")
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(BUDGET_DIR, exist_ok=True)

DPI = 300

# ── Dark infographic theme ──────────────────────────────────────────────────
sns.set_theme(style="darkgrid", context="notebook", font_scale=1.15)
plt.rcParams.update({
    "figure.facecolor": "#0D1117",
    "axes.facecolor": "#161B22",
    "axes.edgecolor": "#30363D",
    "axes.labelcolor": "#E6EDF3",
    "text.color": "#E6EDF3",
    "xtick.color": "#8B949E",
    "ytick.color": "#8B949E",
    "grid.color": "#21262D",
    "grid.alpha": 0.6,
    "font.family": "sans-serif",
    "savefig.facecolor": "#0D1117",
})

POP_COLOR = "#F778BA"
K12_COLOR = "#58A6FF"
PS_COLOR = "#56D364"
TOT_COLOR = "#FFB703"
CPI_COLOR = "#FF6B6B"
REAL_K12_COLOR = "#1E90FF"
REAL_PS_COLOR = "#2E8B57"
REAL_TOT_COLOR = "#DAA520"


def load_data():
    """Load population, spending, and CPI data; merge into a single DataFrame."""
    # Population from YoY CSV (Q1 snapshots)
    pop_path = os.path.join(SCRIPT_DIR, "alberta_yoy_growth.csv")
    pop = pd.read_csv(pop_path)[["Year", "Population"]]

    # Spending from CSV
    spend_path = os.path.join(SCRIPT_DIR, "spending_data.csv")
    spending = pd.read_csv(spend_path)
    spending["Total_M"] = spending["K12_M"] + spending["PostSec_M"]

    # Merge
    df = spending.merge(pop, on="Year", how="left")

    # Alberta CPI (All-items, annual average, 2002=100)
    # Source: Statistics Canada Table 18-10-0005-01
    # Retrieved via Alberta Economic Dashboard API
    cpi_data = {2012: 127.1, 2013: 128.6, 2023: 164.4, 2024: 169.2, 2025: 172.1}
    df["CPI"] = df["Year"].map(cpi_data)
    df["CPI_Deflator"] = df["CPI"] / cpi_data[2012]  # deflator relative to 2012

    # Nominal per-capita
    df["K12_PerCapita"] = (df["K12_M"] * 1_000_000) / df["Population"]
    df["PostSec_PerCapita"] = (df["PostSec_M"] * 1_000_000) / df["Population"]
    df["Total_PerCapita"] = (df["Total_M"] * 1_000_000) / df["Population"]

    # Real spending (2012 dollars)
    df["K12_Real_M"] = df["K12_M"] / df["CPI_Deflator"]
    df["PostSec_Real_M"] = df["PostSec_M"] / df["CPI_Deflator"]
    df["Total_Real_M"] = df["Total_M"] / df["CPI_Deflator"]

    # Real per-capita (2012 dollars)
    df["K12_Real_PerCapita"] = (df["K12_Real_M"] * 1_000_000) / df["Population"]
    df["PostSec_Real_PerCapita"] = (df["PostSec_Real_M"] * 1_000_000) / df["Population"]
    df["Total_Real_PerCapita"] = (df["Total_Real_M"] * 1_000_000) / df["Population"]

    # Index to 2012-13 baseline (= 100)
    base = df.iloc[0]
    df["Pop_Index"] = (df["Population"] / base["Population"]) * 100
    df["K12_Index"] = (df["K12_M"] / base["K12_M"]) * 100
    df["PostSec_Index"] = (df["PostSec_M"] / base["PostSec_M"]) * 100
    df["Total_Index"] = (df["Total_M"] / base["Total_M"]) * 100
    df["K12_Real_Index"] = (df["K12_Real_M"] / base["K12_Real_M"]) * 100
    df["PostSec_Real_Index"] = (df["PostSec_Real_M"] / base["PostSec_Real_M"]) * 100
    df["Total_Real_Index"] = (df["Total_Real_M"] / base["Total_Real_M"]) * 100

    return df


def style_legend(ax, loc="upper left"):
    """Apply dark theme to legend."""
    leg = ax.legend(fontsize=12, loc=loc, framealpha=0.7, edgecolor="#30363D")
    leg.get_frame().set_facecolor("#161B22")
    for t in leg.get_texts():
        t.set_color("#E6EDF3")
    return leg


def chart_indexed_growth(df):
    """Chart 1: Indexed Growth — Population vs Education Spending (2012-13 = 100)."""
    era1 = df[df["Year"].isin([2012, 2013])]
    era2 = df[df["Year"].isin([2023, 2024, 2025])]

    series = [
        ("Pop_Index", POP_COLOR, "o", "Population"),
        ("K12_Index", K12_COLOR, "s", "K-12 Spending"),
        ("PostSec_Index", PS_COLOR, "^", "Post-Secondary Spending"),
        ("Total_Index", TOT_COLOR, "D", "Total Education Spending"),
    ]

    fig, ax = plt.subplots(figsize=(14, 7))

    for col, color, marker, label in series:
        ax.plot(era1["Year"], era1[col], color=color, linewidth=3,
                marker=marker, markersize=11, zorder=5, label=label)
        ax.plot(era2["Year"], era2[col], color=color, linewidth=3,
                marker=marker, markersize=11, zorder=5)

    ax.axhline(100, color="#8B949E", linewidth=1.2, linestyle="--",
               alpha=0.55, label="2012-13 Baseline (= 100)")
    ax.axvspan(2013.4, 2022.6, alpha=0.07, color="#8B949E", zorder=1)
    ax.text(2018, 109, "Data gap\n2014 \u2013 2022", ha="center", fontsize=11,
            color="#8B949E", style="italic")

    for col, color, _, _ in series:
        val = df.iloc[-1][col]
        ax.text(2025.25, val, f"{val:.0f}", color=color,
                fontsize=10, fontweight="bold", va="center")

    ax.set_xlim(2011, 2027)
    ax.set_xticks(df["Year"].tolist())
    ax.set_xlabel("Calendar Year (Q1 population snapshot)", fontsize=13, labelpad=10)
    ax.set_ylabel("Index  (2012-13 = 100)", fontsize=13, labelpad=10)
    ax.set_title(
        "Alberta: Population Growth vs. Education Spending\n"
        "Indexed to 2012-13 = 100  |  Nominal figures",
        fontsize=18, fontweight="bold", pad=20, color="white",
    )
    style_legend(ax)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "integration_indexed_growth.png")
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved -> {out}")


def chart_per_capita(df):
    """Chart 2: Nominal Per-Capita Education Spending."""
    labels = df["Fiscal_Year"].values
    x = np.arange(len(labels))
    w = 0.38

    fig, ax = plt.subplots(figsize=(14, 7))

    bars1 = ax.bar(x - w / 2, df["K12_PerCapita"], w, label="K-12",
                   color=K12_COLOR, edgecolor="#0D1117", linewidth=1.5)
    bars2 = ax.bar(x + w / 2, df["PostSec_PerCapita"], w, label="Post-Secondary",
                   color=PS_COLOR, edgecolor="#0D1117", linewidth=1.5)

    for bars, color in [(bars1, K12_COLOR), (bars2, PS_COLOR)]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 18,
                    f"${h:,.0f}", ha="center", va="bottom",
                    fontsize=9, fontweight="bold", color=color)

    gap_y = df["K12_PerCapita"].max() * 0.62
    ax.axvline(1.5, color="#8B949E", linewidth=1.2, linestyle=":", alpha=0.55)
    ax.text(1.5, gap_y, "9-year\ndata gap", ha="center", va="center",
            fontsize=10, color="#8B949E", style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#161B22",
                      edgecolor="#30363D", alpha=0.85))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12, fontweight="bold")
    ax.set_ylabel("Spending per Capita ($)", fontsize=13, labelpad=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.set_title(
        "Alberta: Education Spending per Capita\n"
        "K-12 vs Post-Secondary  |  Nominal figures",
        fontsize=18, fontweight="bold", pad=20, color="white",
    )
    style_legend(ax)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "integration_per_capita.png")
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved -> {out}")


def chart_growth_rates(df):
    """Chart 3: Growth Rates Lollipop (fixed text overlap)."""
    first, last = df.iloc[0], df.iloc[-1]

    metrics = [
        "Population",
        "K-12 Spending",
        "Post-Secondary\nSpending",
        "Total Education\nSpending",
    ]
    pcts = [
        (last["Population"] / first["Population"] - 1) * 100,
        (last["K12_M"] / first["K12_M"] - 1) * 100,
        (last["PostSec_M"] / first["PostSec_M"] - 1) * 100,
        (last["Total_M"] / first["Total_M"] - 1) * 100,
    ]
    colors = [POP_COLOR, K12_COLOR, PS_COLOR, TOT_COLOR]

    fig, ax = plt.subplots(figsize=(12, 6))
    y = np.arange(len(metrics))

    for i in range(len(metrics)):
        ax.hlines(y[i], 0, pcts[i], color=colors[i], linewidth=4, alpha=0.85)
        ax.scatter(pcts[i], y[i], color=colors[i], s=280, zorder=5,
                   edgecolor="#0D1117", linewidth=2)
        ax.text(pcts[i] + 3, y[i], f"+{pcts[i]:.1f}%",
                va="center", fontsize=14, fontweight="bold", color=colors[i])

    pop_pct = pcts[0]
    ax.axvline(pop_pct, color=POP_COLOR, linewidth=1.5, linestyle="--", alpha=0.45)
    ax.text(pop_pct + 1, len(metrics) - 0.15,
            f"Population growth ({pop_pct:.1f}%)",
            color=POP_COLOR, fontsize=9, alpha=0.85)

    ax.set_yticks(y)
    ax.set_yticklabels(metrics, fontsize=13, fontweight="bold")
    ax.set_xlabel("Growth from 2012-13 Baseline (%)", fontsize=13, labelpad=10)
    ax.set_xlim(-5, max(pcts) * 1.3)
    ax.set_title(
        "Education Spending vs. Population Growth\n"
        "2012-13 to 2025-26  |  Nominal figures",
        fontsize=18, fontweight="bold", pad=20, color="white",
    )
    ax.axvline(0, color="#30363D", linewidth=1)

    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "integration_growth_rates.png")
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved -> {out}")


def chart_real_vs_nominal(df):
    """Chart 4 (NEW): Real vs Nominal Total Education Spending."""
    labels = df["Fiscal_Year"].values
    x = np.arange(len(labels))
    w = 0.38

    fig, ax = plt.subplots(figsize=(14, 7))

    bars1 = ax.bar(x - w / 2, df["Total_M"], w, label="Nominal $",
                   color=TOT_COLOR, edgecolor="#0D1117", linewidth=1.5)
    bars2 = ax.bar(x + w / 2, df["Total_Real_M"], w, label="Real $ (2012 dollars)",
                   color=REAL_TOT_COLOR, edgecolor="#0D1117", linewidth=1.5,
                   alpha=0.85)

    for bars, color in [(bars1, TOT_COLOR), (bars2, REAL_TOT_COLOR)]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 100,
                    f"${h:,.0f}M", ha="center", va="bottom",
                    fontsize=8, fontweight="bold", color=color)

    # Annotate the inflation gap for 2025
    nom_2025 = df.iloc[-1]["Total_M"]
    real_2025 = df.iloc[-1]["Total_Real_M"]
    gap = nom_2025 - real_2025
    ax.annotate(
        f"Inflation accounts for\n${gap:,.0f}M of apparent growth",
        xy=(x[-1] + 0.05, (nom_2025 + real_2025) / 2),
        xytext=(x[-1] + 0.8, nom_2025 * 0.85),
        fontsize=10, color="#E6EDF3",
        arrowprops=dict(arrowstyle="->", color="#8B949E", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#161B22",
                  edgecolor="#30363D", alpha=0.9),
    )

    ax.axvline(1.5, color="#8B949E", linewidth=1.2, linestyle=":", alpha=0.55)
    ax.text(1.5, df["Total_M"].max() * 0.35, "9-year\ndata gap",
            ha="center", va="center", fontsize=10, color="#8B949E", style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#161B22",
                      edgecolor="#30363D", alpha=0.85))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12, fontweight="bold")
    ax.set_ylabel("Total Education Spending ($M)", fontsize=13, labelpad=10)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"${v:,.0f}M"))
    ax.set_title(
        "Alberta: Total Education Spending \u2014 Nominal vs. Real\n"
        "Real figures in constant 2012 dollars  |  "
        "Deflated using Alberta CPI (All-items)",
        fontsize=16, fontweight="bold", pad=20, color="white",
    )
    style_legend(ax, loc="upper left")
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "integration_real_vs_nominal.png")
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved -> {out}")


def chart_real_per_capita(df):
    """Chart 5 (NEW): Real Per-Capita Education Spending (2012 dollars)."""
    labels = df["Fiscal_Year"].values
    x = np.arange(len(labels))
    w = 0.38

    fig, ax = plt.subplots(figsize=(14, 7))

    bars1 = ax.bar(x - w / 2, df["K12_Real_PerCapita"], w,
                   label="K-12 (2012 dollars)",
                   color=REAL_K12_COLOR, edgecolor="#0D1117", linewidth=1.5)
    bars2 = ax.bar(x + w / 2, df["PostSec_Real_PerCapita"], w,
                   label="Post-Secondary (2012 dollars)",
                   color=REAL_PS_COLOR, edgecolor="#0D1117", linewidth=1.5)

    for bars, color in [(bars1, REAL_K12_COLOR), (bars2, REAL_PS_COLOR)]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 12,
                    f"${h:,.0f}", ha="center", va="bottom",
                    fontsize=9, fontweight="bold", color=color)

    # Reference line for 2012 K-12 baseline
    k12_base = df.iloc[0]["K12_Real_PerCapita"]
    ax.axhline(k12_base, color=REAL_K12_COLOR, linewidth=1, linestyle="--",
               alpha=0.4)
    ax.text(len(labels) - 0.5, k12_base + 15,
            f"2012-13 K-12 baseline: ${k12_base:,.0f}",
            fontsize=8, color=REAL_K12_COLOR, alpha=0.7, ha="right")

    ax.axvline(1.5, color="#8B949E", linewidth=1.2, linestyle=":", alpha=0.55)
    ax.text(1.5, df["K12_Real_PerCapita"].max() * 0.55,
            "9-year\ndata gap", ha="center", va="center",
            fontsize=10, color="#8B949E", style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#161B22",
                      edgecolor="#30363D", alpha=0.85))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12, fontweight="bold")
    ax.set_ylabel("Spending per Capita (2012 dollars)", fontsize=13, labelpad=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.set_title(
        "Alberta: Real Education Spending per Capita\n"
        "K-12 vs Post-Secondary  |  Constant 2012 dollars (Alberta CPI-adjusted)",
        fontsize=16, fontweight="bold", pad=20, color="white",
    )
    style_legend(ax)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "integration_real_per_capita.png")
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved -> {out}")


def chart_real_growth_comparison(df):
    """Chart 6 (NEW): Nominal vs Real Growth Rates with CPI reference."""
    first, last = df.iloc[0], df.iloc[-1]

    metrics = [
        "CPI Inflation\n(Alberta)",
        "Population",
        "K-12 Spending\n(nominal)",
        "K-12 Spending\n(real)",
        "Post-Secondary\n(nominal)",
        "Post-Secondary\n(real)",
        "Total Education\n(nominal)",
        "Total Education\n(real)",
    ]
    pcts = [
        (last["CPI_Deflator"] - 1) * 100,
        (last["Population"] / first["Population"] - 1) * 100,
        (last["K12_M"] / first["K12_M"] - 1) * 100,
        (last["K12_Real_M"] / first["K12_Real_M"] - 1) * 100,
        (last["PostSec_M"] / first["PostSec_M"] - 1) * 100,
        (last["PostSec_Real_M"] / first["PostSec_Real_M"] - 1) * 100,
        (last["Total_M"] / first["Total_M"] - 1) * 100,
        (last["Total_Real_M"] / first["Total_Real_M"] - 1) * 100,
    ]
    colors = [
        CPI_COLOR, POP_COLOR,
        K12_COLOR, REAL_K12_COLOR,
        PS_COLOR, REAL_PS_COLOR,
        TOT_COLOR, REAL_TOT_COLOR,
    ]

    fig, ax = plt.subplots(figsize=(14, 8))
    y = np.arange(len(metrics))

    for i in range(len(metrics)):
        ax.hlines(y[i], 0, pcts[i], color=colors[i], linewidth=4, alpha=0.85)
        ax.scatter(pcts[i], y[i], color=colors[i], s=220, zorder=5,
                   edgecolor="#0D1117", linewidth=2)
        sign = "+" if pcts[i] >= 0 else ""
        ax.text(pcts[i] + 2, y[i], f"{sign}{pcts[i]:.1f}%",
                va="center", fontsize=12, fontweight="bold", color=colors[i])

    pop_pct = pcts[1]
    ax.axvline(pop_pct, color=POP_COLOR, linewidth=1.2, linestyle="--", alpha=0.35)

    ax.set_yticks(y)
    ax.set_yticklabels(metrics, fontsize=11, fontweight="bold")
    ax.set_xlabel("Cumulative Growth from 2012-13 Baseline (%)", fontsize=13,
                  labelpad=10)
    ax.set_xlim(-5, max(pcts) * 1.25)
    ax.set_title(
        "Alberta: Nominal vs. Real Growth Rates (2012-13 to 2025-26)\n"
        "Real figures deflated using Alberta CPI (All-items)  |  "
        "Dashed line = population growth",
        fontsize=15, fontweight="bold", pad=20, color="white",
    )
    ax.axvline(0, color="#30363D", linewidth=1)

    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "integration_real_vs_nominal_growth.png")
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved -> {out}")


def chart_indexed_real_growth(df):
    """Chart 7 (NEW): Indexed Real Growth — all series including CPI."""
    era1 = df[df["Year"].isin([2012, 2013])]
    era2 = df[df["Year"].isin([2023, 2024, 2025])]

    series = [
        ("Pop_Index", POP_COLOR, "o", "Population"),
        ("K12_Real_Index", REAL_K12_COLOR, "s", "K-12 Spending (real)"),
        ("PostSec_Real_Index", REAL_PS_COLOR, "^", "Post-Secondary (real)"),
        ("Total_Real_Index", REAL_TOT_COLOR, "D", "Total Education (real)"),
    ]

    fig, ax = plt.subplots(figsize=(14, 7))

    for col, color, marker, label in series:
        ax.plot(era1["Year"], era1[col], color=color, linewidth=3,
                marker=marker, markersize=11, zorder=5, label=label)
        ax.plot(era2["Year"], era2[col], color=color, linewidth=3,
                marker=marker, markersize=11, zorder=5)

    ax.axhline(100, color="#8B949E", linewidth=1.2, linestyle="--",
               alpha=0.55, label="2012-13 Baseline (= 100)")
    ax.axvspan(2013.4, 2022.6, alpha=0.07, color="#8B949E", zorder=1)
    ax.text(2018, 104, "Data gap\n2014 \u2013 2022", ha="center", fontsize=11,
            color="#8B949E", style="italic")

    for col, color, _, _ in series:
        val = df.iloc[-1][col]
        ax.text(2025.25, val, f"{val:.0f}", color=color,
                fontsize=10, fontweight="bold", va="center")

    ax.set_xlim(2011, 2027)
    ax.set_xticks(df["Year"].tolist())
    ax.set_xlabel("Calendar Year (Q1 population snapshot)", fontsize=13, labelpad=10)
    ax.set_ylabel("Index  (2012-13 = 100)", fontsize=13, labelpad=10)
    ax.set_title(
        "Alberta: Population Growth vs. Real Education Spending\n"
        "Indexed to 2012-13 = 100  |  Inflation-adjusted (Alberta CPI)",
        fontsize=16, fontweight="bold", pad=20, color="white",
    )
    style_legend(ax)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "integration_indexed_real_growth.png")
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved -> {out}")


def chart_real_per_capita_total(df):
    """Chart 8 (NEW): Total Real Per-Capita — nominal vs real side by side."""
    labels = df["Fiscal_Year"].values
    x = np.arange(len(labels))
    w = 0.38

    fig, ax = plt.subplots(figsize=(14, 7))

    bars1 = ax.bar(x - w / 2, df["Total_PerCapita"], w,
                   label="Nominal $ per capita",
                   color=TOT_COLOR, edgecolor="#0D1117", linewidth=1.5)
    bars2 = ax.bar(x + w / 2, df["Total_Real_PerCapita"], w,
                   label="Real $ per capita (2012 dollars)",
                   color=REAL_TOT_COLOR, edgecolor="#0D1117", linewidth=1.5,
                   alpha=0.85)

    for bars, color in [(bars1, TOT_COLOR), (bars2, REAL_TOT_COLOR)]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 18,
                    f"${h:,.0f}", ha="center", va="bottom",
                    fontsize=9, fontweight="bold", color=color)

    ax.axvline(1.5, color="#8B949E", linewidth=1.2, linestyle=":", alpha=0.55)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12, fontweight="bold")
    ax.set_ylabel("Total Education Spending per Capita ($)", fontsize=13,
                  labelpad=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.set_title(
        "Alberta: Total Education Spending per Capita\n"
        "Nominal vs. Real (2012 dollars)  |  Alberta CPI-adjusted",
        fontsize=16, fontweight="bold", pad=20, color="white",
    )
    style_legend(ax, loc="upper left")
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    out = os.path.join(PLOTS_DIR, "integration_real_per_capita_total.png")
    plt.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"Saved -> {out}")


def export_csv(df):
    """Export the full integrated dataset to CSV."""
    export_cols = [
        "Fiscal_Year", "Year", "Population", "CPI", "CPI_Deflator",
        "K12_M", "PostSec_M", "Total_M",
        "K12_Real_M", "PostSec_Real_M", "Total_Real_M",
        "K12_PerCapita", "PostSec_PerCapita", "Total_PerCapita",
        "K12_Real_PerCapita", "PostSec_Real_PerCapita", "Total_Real_PerCapita",
        "Pop_Index", "K12_Index", "PostSec_Index", "Total_Index",
        "K12_Real_Index", "PostSec_Real_Index", "Total_Real_Index",
    ]
    out = os.path.join(BUDGET_DIR, "population_vs_spending.csv")
    df[export_cols].to_csv(out, index=False)
    print(f"Saved -> {out}")


def print_summary(df):
    """Print key findings to console for verification."""
    first, last = df.iloc[0], df.iloc[-1]
    cpi_inflation = (last["CPI_Deflator"] - 1) * 100

    print("\n" + "=" * 70)
    print("KEY FINDINGS SUMMARY")
    print("=" * 70)
    print(f"\nAlberta CPI inflation (2012 to 2025): {cpi_inflation:.1f}%")
    print(f"Population growth: {(last['Population']/first['Population']-1)*100:.1f}%")

    print("\n--- NOMINAL GROWTH ---")
    print(f"K-12:            +{(last['K12_M']/first['K12_M']-1)*100:.1f}%")
    print(f"Post-Secondary:  +{(last['PostSec_M']/first['PostSec_M']-1)*100:.1f}%")
    print(f"Total Education: +{(last['Total_M']/first['Total_M']-1)*100:.1f}%")

    print("\n--- REAL GROWTH (2012 dollars) ---")
    print(f"K-12:            +{(last['K12_Real_M']/first['K12_Real_M']-1)*100:.1f}%")
    print(f"Post-Secondary:  +{(last['PostSec_Real_M']/first['PostSec_Real_M']-1)*100:.1f}%")
    print(f"Total Education: +{(last['Total_Real_M']/first['Total_Real_M']-1)*100:.1f}%")

    print("\n--- NOMINAL PER CAPITA ---")
    print(f"K-12:     ${first['K12_PerCapita']:,.0f} -> ${last['K12_PerCapita']:,.0f}"
          f"  (+{(last['K12_PerCapita']/first['K12_PerCapita']-1)*100:.1f}%)")
    print(f"Post-Sec: ${first['PostSec_PerCapita']:,.0f} -> ${last['PostSec_PerCapita']:,.0f}"
          f"  (+{(last['PostSec_PerCapita']/first['PostSec_PerCapita']-1)*100:.1f}%)")
    print(f"Total:    ${first['Total_PerCapita']:,.0f} -> ${last['Total_PerCapita']:,.0f}"
          f"  (+{(last['Total_PerCapita']/first['Total_PerCapita']-1)*100:.1f}%)")

    print("\n--- REAL PER CAPITA (2012 dollars) ---")
    print(f"K-12:     ${first['K12_Real_PerCapita']:,.0f} -> ${last['K12_Real_PerCapita']:,.0f}"
          f"  ({(last['K12_Real_PerCapita']/first['K12_Real_PerCapita']-1)*100:+.1f}%)")
    print(f"Post-Sec: ${first['PostSec_Real_PerCapita']:,.0f} -> ${last['PostSec_Real_PerCapita']:,.0f}"
          f"  ({(last['PostSec_Real_PerCapita']/first['PostSec_Real_PerCapita']-1)*100:+.1f}%)")
    print(f"Total:    ${first['Total_Real_PerCapita']:,.0f} -> ${last['Total_Real_PerCapita']:,.0f}"
          f"  ({(last['Total_Real_PerCapita']/first['Total_Real_PerCapita']-1)*100:+.1f}%)")
    print("=" * 70)


def main():
    df = load_data()
    print_summary(df)

    # Original charts (regenerated at 300 DPI with fixes)
    chart_indexed_growth(df)
    chart_per_capita(df)
    chart_growth_rates(df)

    # New CPI-adjusted charts
    chart_real_vs_nominal(df)
    chart_real_per_capita(df)
    chart_real_growth_comparison(df)
    chart_indexed_real_growth(df)
    chart_real_per_capita_total(df)

    # Export
    export_csv(df)
    print("\nAll charts generated successfully.")


if __name__ == "__main__":
    main()
