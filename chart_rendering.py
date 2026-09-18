"""Render the three publication figures from validated analysis tables."""

from __future__ import annotations

from pathlib import Path
from textwrap import fill

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


NAVY = "#17324D"
TEAL = "#087E83"
PURPLE = "#70449B"
MUTED = "#53657A"
PALE = "#E7ECF1"
SECTORS = (("k12", "K–12 school authorities", TEAL),
           ("postsec", "Post-secondary institutions", PURPLE))


def _style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.titlesize": 14, "axes.labelsize": 10,
        "text.color": NAVY, "axes.labelcolor": NAVY,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.edgecolor": PALE, "svg.fonttype": "none",
        "svg.hashsalt": "alberta-education-brief",
        "savefig.facecolor": "white",
    })


def _save(fig, destination: Path, stem: str) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination / f"{stem}.svg", bbox_inches="tight", metadata={"Date": None})
    fig.savefig(destination / f"{stem}.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def _runs(rows):
    """Only consecutive observations in the same approved segment form a line."""
    run = []
    for row in rows.itertuples():
        if run and (row.year != run[-1].year + 1 or row.segment != run[-1].segment):
            yield run
            run = []
        run.append(row)
    if run:
        yield run


def resources(result: dict, measure: str, destination: Path) -> None:
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.5), constrained_layout=True)
    title = "Provincial support" if measure == "grants" else "Institutional resources"
    fig.suptitle(f"{title} | real dollars per learner", fontsize=17,
                 fontweight="bold", color=NAVY)
    data = result["per_learner"]
    for ax, (sector, sector_label, color) in zip(axes, SECTORS):
        subset = data.loc[(data["sector"] == sector) & (data["measure"] == measure)]
        valid = subset.dropna(subset=["real_per_learner"]).sort_values("year")
        definition = next(v for v in result["series"].values()
                          if v["sector"] == sector and v["measure"] == measure)
        ax.set_title(sector_label, loc="left", fontweight="bold", color=color, pad=14)
        subtitle = {
            ("k12", "grants"): "Provincial revenue excluding capital recognition",
            ("postsec", "grants"): "Department operating grants · 20 public institutions",
            ("k12", "expenses"): "School-authority expenses less amortization",
            ("postsec", "expenses"): "Three universities · expenses less amortization",
        }[(sector, measure)]
        ax.text(0, 1.01, subtitle, transform=ax.transAxes,
                color=MUTED, fontsize=11, va="bottom")
        ax.grid(axis="y", color=PALE)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.yaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
        ax.set_ylabel(f"2012 CAD / {definition['learner_unit']}")
        ax.set_xlabel("Reporting period start year")
        if valid.empty:
            ax.text(0.5, 0.5, "No matched per-learner observation yet",
                    transform=ax.transAxes, ha="center", va="center",
                    color=MUTED, fontsize=11, wrap=True)
            ax.set_xticks([])
            continue
        ax.scatter(valid["year"], valid["real_per_learner"], s=50,
                   color=color, zorder=3)
        for run in _runs(valid):
            if len(run) >= 3:
                ax.plot([row.year for row in run],
                        [row.real_per_learner for row in run], color=color,
                        linewidth=2.2, zorder=2)
        years = valid["year"].astype(int)
        ax.set_xlim(years.min() - 0.7, years.max() + 1.4)
        if years.max() - years.min() <= 4:
            ax.set_xticks(years.tolist())
        else:
            ax.set_xticks(list(range(years.min(), years.max() + 1, 2)))
        values = valid["real_per_learner"]
        span = max(values.max() - values.min(), values.max() * 0.15, 1)
        ax.set_ylim(max(0, values.min() - span * 0.25), values.max() + span * 0.35)
        latest = valid.iloc[-1]
        ax.annotate(f"{latest['period']}\n${latest['real_per_learner']:,.0f}",
                    (latest["year"], latest["real_per_learner"]),
                    xytext=(8, 8), textcoords="offset points",
                    color=color, fontweight="bold", fontsize=9)
        if len(valid) == 2:
            first = valid.iloc[0]
            ax.annotate(f"${first['real_per_learner']:,.0f}",
                        (first["year"], first["real_per_learner"]),
                        xytext=(-3, 9), textcoords="offset points",
                        color=color, fontsize=9)
    fig.text(0.5, -0.025,
             "Dots show annual observations; lines join ≥3 comparable years. Sector axes and learner units differ.",
             ha="center", color=MUTED, fontsize=11)
    annotation = (
        "K–12: 2018 revenue break; 2022 Valhalla omitted; 2023 draft Northland. "
        "PS: 2023–24 and 2024–25 grant ratios withheld (FLE reporting)."
        if measure == "grants" else
        "K–12: 2022 Valhalla omitted / asset-retirement change; 2023 draft Northland. "
        "PS: three-university subset also excludes disposal losses."
    )
    fig.text(0.5, -0.065, annotation, ha="center", color=MUTED, fontsize=11)
    _save(fig, destination, "provincial_support" if measure == "grants" else "institutional_resources")


def plans_delivery(result: dict, destination: Path) -> None:
    _style()
    delivery = result["delivery"]
    if not delivery.empty:
        plot = delivery.sort_values(["sector", "measure", "year"])
        labels = [f"{row.sector.upper()} · {row.measure} · {row.period}"
                  for row in plot.itertuples()]
        colors = [TEAL if row.sector == "k12" else PURPLE
                  for row in plot.itertuples()]
        fig, ax = plt.subplots(figsize=(11.6, max(4.2, len(plot) * 0.65 + 1.6)),
                               constrained_layout=True)
        bars = ax.barh(labels, plot["variance_m"], color=colors)
        ax.axvline(0, color=NAVY, linewidth=1)
        ax.set_xlabel("Actual minus original budget · nominal CAD millions")
        ax.set_title("Plans and delivery | matched original budgets",
                     loc="left", fontsize=17, fontweight="bold")
        ax.grid(axis="x", color=PALE)
        ax.set_axisbelow(True)
        for bar, value in zip(bars, plot["variance_m"]):
            ax.annotate(f"{value:+,.1f} M", (bar.get_width(), bar.get_y() + bar.get_height() / 2),
                        xytext=(5 if value >= 0 else -5, 0),
                        textcoords="offset points", va="center",
                        ha="left" if value >= 0 else "right", fontsize=10)
    else:
        fig, axes = plt.subplots(2, 2, figsize=(11.6, 6.5), constrained_layout=True)
        fig.suptitle("Plans and delivery | original-budget evidence gap",
                     fontsize=17, fontweight="bold", color=NAVY)
        for ax, (sector, label, color), measure in zip(
            axes.flat,
            (SECTORS[0], SECTORS[1], SECTORS[0], SECTORS[1]),
            ("grants", "grants", "expenses", "expenses"),
        ):
            definition = next(v for v in result["series"].values()
                              if v["sector"] == sector and v["measure"] == measure)
            ax.set_facecolor("#F5F8FA")
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_color(PALE)
            card_label = ("K–12 · Provincial revenue" if sector == "k12" and measure == "grants"
                          else "Three universities · Expenses" if sector == "postsec" and measure == "expenses"
                          else f"{'K–12' if sector == 'k12' else 'Post-secondary'} · {measure.capitalize()}")
            ax.text(0.045, 0.88, card_label,
                    transform=ax.transAxes, va="top", fontsize=13,
                    fontweight="bold", color=color)
            ax.text(0.045, 0.57, "No matched original-budget pair",
                    transform=ax.transAxes, va="top", fontsize=12, color=NAVY)
            gap = definition["delivery_gap"].replace("this subset", "the three universities")
            ax.text(0.045, 0.37, fill(gap, width=45),
                    transform=ax.transAxes, va="top", fontsize=11.5,
                    color=MUTED, linespacing=1.25)
        fig.text(0.5, -0.015,
                 "Decision request: publish original plan, accounting bridge and actual on the same institutional boundary.",
                 ha="center", fontsize=10, color=NAVY)
    _save(fig, destination, "plans_and_delivery")
