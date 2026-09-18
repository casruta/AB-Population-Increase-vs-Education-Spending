"""Build the integrated education-spending charts and analysis dataset.

The spending file contains five selected fiscal years, not a continuous time
series. Charts therefore use discrete bars or explicitly disconnected line
segments. Money values are budget figures from Alberta fiscal plans.

Data sources
------------
Population: Statistics Canada table 17-10-0009-01 (January 1 estimates)
Spending: Alberta fiscal plans listed in ``spending_data.csv``
CPI: Statistics Canada table 18-10-0005-01, documented in ``cpi_data.csv``
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PLOTS_DIR = SCRIPT_DIR / "plots"
BUDGET_DIR = SCRIPT_DIR / "budget_data"
BASELINE_YEAR = 2012
ENDPOINT_YEAR = 2025
DPI = 220

# Okabe-Ito colour-blind-safe palette. Hatches, markers, and line styles provide
# redundant visual encoding for readers who cannot distinguish the colours.
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILLION = "#D55E00"
PURPLE = "#CC79A7"
GREY = "#5F6368"
LIGHT_GREY = "#E5E7EB"
INK = "#202124"

SOURCE_NOTE = (
    "Sources: Alberta fiscal plans; Statistics Canada tables 17-10-0009-01 "
    "and 18-10-0005-01."
)
METHOD_NOTE = (
    "Five selected fiscal years only; no spending observations for 2014-15 "
    "to 2022-23. All spending values are fiscal-plan budget figures."
)

EXPECTED_YEARS = {2012, 2013, 2023, 2024, 2025}
INPUT_COLUMNS = {
    "spending": {
        "Fiscal_Year",
        "Year",
        "K12_M",
        "PostSec_M",
        "Source",
        "Source_Detail",
        "Source_URL",
    },
    "population": {"Year", "Population"},
    "cpi": {"Year", "CPI", "Source"},
}


def configure_style() -> None:
    """Set a light theme that remains readable on GitHub and in print."""
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#9AA0A6",
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "text.color": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "grid.color": LIGHT_GREY,
            "grid.linewidth": 0.8,
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "legend.frameon": False,
            "svg.hashsalt": "alberta-education-spending",
        }
    )


def _require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{name} is missing required columns: {sorted(missing)}")


def _validate_input(frame: pd.DataFrame, required: set[str], name: str) -> None:
    _require_columns(frame, required, name)
    if frame[list(required)].isnull().any().any():
        raise ValueError(f"{name} contains null values in required columns")
    if frame["Year"].duplicated().any():
        duplicates = frame.loc[frame["Year"].duplicated(keep=False), "Year"].tolist()
        raise ValueError(f"{name} contains duplicate years: {duplicates}")


def validate_data(
    spending: pd.DataFrame, population: pd.DataFrame, cpi: pd.DataFrame
) -> None:
    """Fail early when an input cannot support the stated comparison."""
    for frame, name in (
        (spending, "spending"),
        (population, "population"),
        (cpi, "cpi"),
    ):
        _validate_input(frame, INPUT_COLUMNS[name], name)

    years = set(spending["Year"].astype(int))
    if years != EXPECTED_YEARS:
        raise ValueError(
            f"spending years must be {sorted(EXPECTED_YEARS)}; got {sorted(years)}"
        )
    if BASELINE_YEAR not in years or ENDPOINT_YEAR not in years:
        raise ValueError("explicit baseline and endpoint years are required")

    for name, frame in (("population", population), ("cpi", cpi)):
        unavailable = years.difference(set(frame["Year"].astype(int)))
        if unavailable:
            raise ValueError(f"{name} has no values for years {sorted(unavailable)}")

    numeric_positive = {
        "spending": (spending, ["K12_M", "PostSec_M"]),
        "population": (population, ["Population"]),
        "cpi": (cpi, ["CPI"]),
    }
    for name, (frame, columns) in numeric_positive.items():
        values = frame[columns].apply(pd.to_numeric, errors="coerce")
        if values.isnull().any().any() or (values <= 0).any().any():
            raise ValueError(f"{name} values in {columns} must be numeric and positive")

    expected_labels = spending["Year"].map(
        lambda year: f"{int(year)}-{str(int(year) + 1)[-2:]}"
    )
    if not expected_labels.equals(spending["Fiscal_Year"].astype(str)):
        raise ValueError("Fiscal_Year labels do not match Year values")


def load_data(
    spending_path: Path | str | None = None,
    population_path: Path | str | None = None,
    cpi_path: Path | str | None = None,
) -> pd.DataFrame:
    """Load, validate, merge, and calculate the analysis fields."""
    spending = pd.read_csv(spending_path or SCRIPT_DIR / "spending_data.csv")
    population = pd.read_csv(
        population_path or SCRIPT_DIR / "alberta_yoy_growth.csv"
    )[["Year", "Population"]]
    cpi = pd.read_csv(cpi_path or SCRIPT_DIR / "cpi_data.csv")
    validate_data(spending, population, cpi)

    spending = spending.sort_values("Year", kind="stable").reset_index(drop=True)
    population = population.sort_values("Year", kind="stable")
    cpi = cpi.sort_values("Year", kind="stable")
    frame = spending.merge(
        population, on="Year", how="left", validate="one_to_one"
    ).merge(
        cpi[["Year", "CPI"]], on="Year", how="left", validate="one_to_one"
    )
    if frame[["Population", "CPI"]].isnull().any().any():
        raise ValueError("the population/CPI merge produced missing values")

    frame["Total_M"] = frame["K12_M"] + frame["PostSec_M"]
    if not np.allclose(frame["Total_M"], frame["K12_M"] + frame["PostSec_M"]):
        raise ValueError("Total_M must equal K12_M plus PostSec_M")

    baseline = frame.loc[frame["Year"] == BASELINE_YEAR]
    endpoint = frame.loc[frame["Year"] == ENDPOINT_YEAR]
    if len(baseline) != 1 or len(endpoint) != 1:
        raise ValueError("exactly one baseline and endpoint row are required")
    base = baseline.iloc[0]

    frame["Budget_Status"] = "Budget-plan figure"
    frame["CPI_Deflator"] = frame["CPI"] / base["CPI"]

    for prefix in ("K12", "PostSec", "Total"):
        nominal = f"{prefix}_M"
        frame[f"{prefix}_PerCapita"] = (
            frame[nominal] * 1_000_000 / frame["Population"]
        )
        frame[f"{prefix}_Real_M"] = frame[nominal] / frame["CPI_Deflator"]
        frame[f"{prefix}_Real_PerCapita"] = (
            frame[f"{prefix}_Real_M"] * 1_000_000 / frame["Population"]
        )
        frame[f"{prefix}_Index"] = frame[nominal] / base[nominal] * 100
        frame[f"{prefix}_Real_Index"] = (
            frame[f"{prefix}_Real_M"] / base[nominal] * 100
        )
    frame["Pop_Index"] = frame["Population"] / base["Population"] * 100

    derived = [column for column in frame if column not in spending.columns]
    if frame[derived].isnull().any().any():
        raise ValueError("calculation produced null values")
    if (frame.select_dtypes(include="number") <= 0).any().any():
        raise ValueError("merged and calculated numeric values must be positive")
    return frame


def headline_metrics(frame: pd.DataFrame) -> dict[str, float]:
    """Return endpoint comparisons used by the charts and README."""
    first = frame.loc[frame["Year"] == BASELINE_YEAR].iloc[0]
    last = frame.loc[frame["Year"] == ENDPOINT_YEAR].iloc[0]

    def growth(column: str) -> float:
        return (last[column] / first[column] - 1) * 100

    return {
        "cpi_inflation_pct": (last["CPI_Deflator"] - 1) * 100,
        "population_growth_pct": growth("Population"),
        "k12_nominal_growth_pct": growth("K12_M"),
        "postsec_nominal_growth_pct": growth("PostSec_M"),
        "total_nominal_growth_pct": growth("Total_M"),
        "k12_real_growth_pct": growth("K12_Real_M"),
        "postsec_real_growth_pct": growth("PostSec_Real_M"),
        "total_real_growth_pct": growth("Total_Real_M"),
        "k12_real_per_capita_growth_pct": growth("K12_Real_PerCapita"),
        "postsec_real_per_capita_growth_pct": growth(
            "PostSec_Real_PerCapita"
        ),
        "total_real_per_capita_growth_pct": growth("Total_Real_PerCapita"),
    }


def _labels(frame: pd.DataFrame) -> list[str]:
    return frame["Fiscal_Year"].astype(str).tolist()


def _finish(
    fig: plt.Figure,
    ax: plt.Axes,
    filename: str,
    *,
    note: str = METHOD_NOTE,
    source: str = SOURCE_NOTE,
) -> None:
    """Add provenance and save an SVG plus a high-resolution PNG."""
    ax.text(
        0,
        -0.18,
        f"{note}\n{source}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8.5,
        color=GREY,
        linespacing=1.35,
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.11, right=0.98, top=0.82, bottom=0.25)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg"):
        output = PLOTS_DIR / f"{filename}.{suffix}"
        metadata = {"Creator": "generate_all_charts.py"}
        if suffix == "svg":
            metadata["Date"] = None
        fig.savefig(
            output,
            dpi=DPI if suffix == "png" else None,
            bbox_inches="tight",
            metadata=metadata,
        )
        if suffix == "svg":
            svg = output.read_text(encoding="utf-8")
            output.write_text(
                "\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
                encoding="utf-8",
            )
        print(f"Saved -> {output}")
    plt.close(fig)


def _value_labels(ax: plt.Axes, bars: Iterable, fmt: str = "${:,.0f}") -> None:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            fmt.format(height),
            (bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=INK,
        )


def load_population_series(
    population_path: Path | str | None = None,
) -> pd.DataFrame:
    """Load the complete annual Q1 population series used by the overview chart."""
    population = pd.read_csv(
        population_path or SCRIPT_DIR / "alberta_yoy_growth.csv"
    )
    _require_columns(population, {"Year", "Population"}, "population")
    population = population[["Year", "Population"]].copy()
    if population.isnull().any().any():
        raise ValueError("population contains null Year or Population values")
    if population["Year"].duplicated().any():
        raise ValueError("population contains duplicate years")
    population = population.sort_values("Year", kind="stable").reset_index(drop=True)
    population = population[
        population["Year"].between(BASELINE_YEAR, ENDPOINT_YEAR)
    ].copy()
    expected = list(range(BASELINE_YEAR, ENDPOINT_YEAR + 1))
    if population["Year"].astype(int).tolist() != expected:
        raise ValueError(
            f"population overview requires every year from {BASELINE_YEAR} "
            f"through {ENDPOINT_YEAR}"
        )
    values = pd.to_numeric(population["Population"], errors="coerce")
    if values.isnull().any() or (values <= 0).any():
        raise ValueError("population values must be numeric and positive")
    return population


def chart_population_growth(population: pd.DataFrame) -> None:
    """Show Alberta's complete Q1 population series for the study period."""
    first = population.iloc[0]
    last = population.iloc[-1]
    fig, ax = plt.subplots(figsize=(11, 6.4))
    ax.plot(
        population["Year"],
        population["Population"],
        color=BLUE,
        marker="o",
        markersize=5,
        linewidth=2.4,
    )
    ax.fill_between(
        population["Year"],
        population["Population"],
        population["Population"].min() * 0.98,
        color=BLUE,
        alpha=0.08,
    )
    for row, alignment in ((first, "left"), (last, "right")):
        ax.annotate(
            f"{row['Population'] / 1_000_000:.2f} million",
            (row["Year"], row["Population"]),
            xytext=(0, 10),
            textcoords="offset points",
            ha=alignment,
            va="bottom",
            fontweight="bold",
            color=INK,
        )
    ax.set_xticks(np.arange(BASELINE_YEAR, ENDPOINT_YEAR + 1, 2))
    ax.set_ylabel("Alberta population (Q1 estimate)")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda value, _: f"{value / 1_000_000:.1f}M")
    )
    ax.grid(axis="y")
    ax.set_title("Alberta added 1.17 million residents from 2012 to 2025", loc="left")
    _finish(
        fig,
        ax,
        "alberta_population_growth",
        note="Annual Q1 estimates; this population series has no missing years.",
        source="Source: Statistics Canada table 17-10-0009-01.",
    )


def chart_real_growth_comparison(frame: pd.DataFrame) -> None:
    """Compare endpoint growth without implying observations in missing years."""
    metrics = headline_metrics(frame)
    labels = [
        "Population",
        "Education ministry expense",
        "Advanced-education ministry series",
        "Combined ministry expense",
    ]
    nominal = [
        metrics["population_growth_pct"],
        metrics["k12_nominal_growth_pct"],
        metrics["postsec_nominal_growth_pct"],
        metrics["total_nominal_growth_pct"],
    ]
    real = [
        metrics["population_growth_pct"],
        metrics["k12_real_growth_pct"],
        metrics["postsec_real_growth_pct"],
        metrics["total_real_growth_pct"],
    ]
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11, 6.4))
    ax.scatter(
        nominal, y + 0.12, s=90, marker="o", color=ORANGE, label="Nominal change"
    )
    ax.scatter(
        real, y - 0.12, s=85, marker="s", facecolor="white",
        edgecolor=BLUE, linewidth=2, label="Inflation-adjusted change"
    )
    for index, (nominal_value, real_value) in enumerate(zip(nominal, real)):
        ax.plot(
            [real_value, nominal_value],
            [index - 0.12, index + 0.12],
            color="#BDC1C6",
            linewidth=1.3,
            zorder=0,
        )
        ax.text(nominal_value + 2, index + 0.12, f"{nominal_value:+.1f}%", va="center")
        if index:
            ax.text(real_value + 2, index - 0.12, f"{real_value:+.1f}%", va="center")
    ax.axvline(0, color=GREY, linewidth=1)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Change from 2012-13 to 2025-26")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter())
    ax.grid(axis="x")
    ax.legend(loc="lower right")
    ax.set_title(
        "Inflation explains much of the nominal expense increase",
        loc="left",
        pad=14,
    )
    ax.text(
        0,
        1.01,
        "Endpoint comparison; constant 2012 dollars use Alberta all-items CPI",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        color=GREY,
        fontsize=10,
    )
    _finish(fig, ax, "integration_real_vs_nominal_growth")


def chart_real_per_capita(frame: pd.DataFrame) -> None:
    """Show real ministry operating expense per Alberta resident."""
    x = np.arange(len(frame))
    width = 0.36
    fig, ax = plt.subplots(figsize=(11, 6.4))
    k12 = ax.bar(
        x - width / 2,
        frame["K12_Real_PerCapita"],
        width,
        color=BLUE,
        hatch="//",
        edgecolor="white",
        label="Education ministry",
    )
    postsec = ax.bar(
        x + width / 2,
        frame["PostSec_Real_PerCapita"],
        width,
        color=GREEN,
        hatch="..",
        edgecolor="white",
        label="Advanced-education ministry series",
    )
    _value_labels(ax, k12)
    _value_labels(ax, postsec)
    ax.set_ylim(0, frame["K12_Real_PerCapita"].max() * 1.13)
    ax.axvline(1.5, color=GREY, linestyle=":", linewidth=1.2)
    ax.text(
        1.5,
        ax.get_ylim()[1] * 0.55,
        "No spending data\n2014-15 to 2022-23",
        ha="center",
        va="center",
        color=GREY,
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": LIGHT_GREY, "pad": 4},
    )
    ax.set_xticks(x, _labels(frame))
    ax.set_ylabel("Operating expense per resident (constant 2012 dollars)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
    ax.grid(axis="y")
    ax.legend(loc="upper center", ncols=2, bbox_to_anchor=(0.5, 1.0))
    ax.set_title(
        "Real ministry expense per resident moved in different directions",
        loc="left",
    )
    _finish(fig, ax, "integration_real_per_capita")


def chart_real_per_capita_total(frame: pd.DataFrame) -> None:
    """Contrast nominal and real total operating expense per resident."""
    x = np.arange(len(frame))
    width = 0.36
    fig, ax = plt.subplots(figsize=(11, 6.4))
    nominal = ax.bar(
        x - width / 2,
        frame["Total_PerCapita"],
        width,
        color=ORANGE,
        hatch="//",
        edgecolor="white",
        label="Nominal",
    )
    real = ax.bar(
        x + width / 2,
        frame["Total_Real_PerCapita"],
        width,
        color=PURPLE,
        hatch="..",
        edgecolor="white",
        label="Constant 2012 dollars",
    )
    _value_labels(ax, nominal)
    _value_labels(ax, real)
    ax.axvline(1.5, color=GREY, linestyle=":", linewidth=1.2)
    ax.text(
        1.5,
        ax.get_ylim()[1] * 0.48,
        "No spending data\n2014-15 to 2022-23",
        ha="center",
        va="center",
        color=GREY,
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": LIGHT_GREY, "pad": 4},
    )
    ax.set_xticks(x, _labels(frame))
    ax.set_ylabel("Total education operating expense per resident")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
    ax.grid(axis="y")
    ax.legend(loc="upper left")
    ax.set_title("Inflation changes the per-resident spending picture", loc="left")
    _finish(fig, ax, "integration_real_per_capita_total")


def chart_real_vs_nominal(frame: pd.DataFrame) -> None:
    """Show nominal and real total operating expense for selected years."""
    x = np.arange(len(frame))
    width = 0.36
    fig, ax = plt.subplots(figsize=(11, 6.4))
    nominal = ax.bar(
        x - width / 2, frame["Total_M"], width, color=ORANGE,
        hatch="//", edgecolor="white", label="Nominal"
    )
    real = ax.bar(
        x + width / 2, frame["Total_Real_M"], width, color=BLUE,
        hatch="..", edgecolor="white", label="Constant 2012 dollars"
    )
    _value_labels(ax, nominal, "${:,.0f}M")
    _value_labels(ax, real, "${:,.0f}M")
    ax.axvline(1.5, color=GREY, linestyle=":", linewidth=1.2)
    ax.text(
        1.5,
        ax.get_ylim()[1] * 0.48,
        "No spending data\n2014-15 to 2022-23",
        ha="center",
        va="center",
        color=GREY,
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": LIGHT_GREY, "pad": 4},
    )
    ax.set_xticks(x, _labels(frame))
    ax.set_ylabel("Total education operating expense ($ millions)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}M"))
    ax.grid(axis="y")
    ax.legend(loc="upper left")
    ax.set_title("Nominal growth is larger than inflation-adjusted growth", loc="left")
    _finish(fig, ax, "integration_real_vs_nominal")


def chart_indexed_real_growth(frame: pd.DataFrame) -> None:
    """Use disconnected segments so the missing observations remain visible."""
    fig, ax = plt.subplots(figsize=(11, 6.4))
    series = [
        ("Pop_Index", "Population", VERMILLION, "o", "-"),
        ("K12_Real_Index", "Education ministry, real", BLUE, "s", "--"),
        (
            "PostSec_Real_Index",
            "Advanced-education ministry series, real",
            GREEN,
            "^",
            "-.",
        ),
        ("Total_Real_Index", "Total education, real", PURPLE, "D", ":"),
    ]
    periods = [frame[frame["Year"].le(2013)], frame[frame["Year"].ge(2023)]]
    for column, label, colour, marker, linestyle in series:
        for period_index, period in enumerate(periods):
            ax.plot(
                period["Year"],
                period[column],
                color=colour,
                marker=marker,
                linestyle=linestyle,
                linewidth=2,
                markersize=7,
                label=label if period_index == 0 else None,
            )
    ax.axvspan(2013.4, 2022.6, color=LIGHT_GREY, alpha=0.55)
    ax.text(
        2018,
        105,
        "No spending data\n2014-15 to 2022-23",
        ha="center",
        va="center",
        color=GREY,
    )
    ax.axhline(100, color=GREY, linewidth=0.9)
    ax.set_xlim(2011.5, 2026)
    ax.set_xticks(frame["Year"], _labels(frame))
    ax.set_ylabel("Index (2012-13 = 100)")
    ax.grid(axis="y")
    ax.legend(loc="upper left", ncols=2)
    ax.set_title("Real spending observations are not a continuous series", loc="left")
    _finish(fig, ax, "integration_indexed_real_growth")


def export_csv(frame: pd.DataFrame) -> Path:
    """Export the documented, reproducible integrated dataset."""
    BUDGET_DIR.mkdir(parents=True, exist_ok=True)
    output = BUDGET_DIR / "population_vs_spending.csv"
    frame.to_csv(output, index=False)
    print(f"Saved -> {output}")
    return output


def print_summary(frame: pd.DataFrame) -> None:
    print("Endpoint comparison: 2012-13 to 2025-26 fiscal-plan figures")
    for name, value in headline_metrics(frame).items():
        print(f"{name}: {value:.1f}%")


def main() -> None:
    configure_style()
    population = load_population_series()
    frame = load_data()
    print_summary(frame)
    chart_population_growth(population)
    chart_real_growth_comparison(frame)
    chart_real_per_capita(frame)
    chart_real_per_capita_total(frame)
    chart_real_vs_nominal(frame)
    chart_indexed_real_growth(frame)
    export_csv(frame)
    print("All chart PNG and SVG files generated successfully.")


if __name__ == "__main__":
    main()
