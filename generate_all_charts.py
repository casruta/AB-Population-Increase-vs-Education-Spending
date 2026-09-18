"""Build the offline education evidence brief and its downloadable tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from analysis import ROOT, build_analysis
from chart_rendering import plans_delivery, resources


def _count(frame: pd.DataFrame, series_id: str) -> int:
    return int(frame.loc[frame["series_id"].eq(series_id), "available"].sum())


def _latest(result: dict, series_id: str) -> str:
    item = result["summary"]["latest"].get(series_id)
    if item is None:
        return "no matched observation"
    unit = result["series"][series_id]["learner_unit"]
    return f"${item['real_per_learner']:,.0f} per {unit} ({item['period']})"


def _coverage_table(result: dict) -> str:
    names = {
        "k12_operating_grants": "K–12 · provincial revenue",
        "postsec_operating_grants": "Post-secondary · departmental grants (20 public)",
        "k12_operating_expenses": "K–12 · school-authority expenses",
        "postsec_operating_expenses": "Post-secondary · three-university expenses",
    }
    order = list(names)
    rows = ["| Evidence line | Latest matched learners | Matched years | Latest real amount per learner |",
            "|---|---|---:|---|"]
    for series_id in order:
        matched = result["per_learner"].loc[result["per_learner"]["series_id"].eq(series_id)].dropna(subset=["real_per_learner"])
        latest = matched.sort_values("year").iloc[-1] if not matched.empty else None
        if latest is None:
            learners = "none verified"
        else:
            learners = f"{latest['learners']:,.0f} {latest['learner_unit']} ({latest['period']})"
        rows.append(f"| {names[series_id]} | {learners} | {_count(result['coverage'], series_id)} | {_latest(result, series_id)} |")
    return "\n".join(rows)


def _brief(result: dict) -> str:
    kgrant = _latest(result, "k12_operating_grants")
    pgrant = _latest(result, "postsec_operating_grants")
    kexp = _latest(result, "k12_operating_expenses")
    pexp = _latest(result, "postsec_operating_expenses")
    n = len(result["delivery"])
    delivery_statement = (f"{n} matched original-budget/actual pairs are available."
                          if n else "No verified original-budget/actual pair is available on these boundaries.")
    delivery_context = ("The bars show actual less original plan on a matching measure and boundary."
                        if n else "Reported budget columns and later forecasts cannot establish original plans for the selected measures.")
    delivery_limits = ("A variance needs the source's explanation; its sign alone says nothing about service quality."
                       if n else "No zero variance is implied by missing bars. The missing original-plan evidence prevents a defensible delivery assessment.")
    delivery_question = ("Which matched variances need a published explanation of timing, accounting and service delivery?"
                         if n else "Can each ministry or institution publish the adopted original budget, subsequent revisions and a reconciliation to the actual on the *same* recipient and accounting boundary? That would permit signed variance bars in the next edition.")
    pair = result["per_learner"].loc[result["per_learner"]["series_id"].eq("postsec_operating_expenses")].dropna(subset=["real_per_learner"]).sort_values("year")
    if (len(pair) == 2 and int(pair.iloc[1]["year"]) == int(pair.iloc[0]["year"]) + 1
            and pair.iloc[0]["segment"] == pair.iloc[1]["segment"]):
        real_change = 100 * (pair.iloc[1]["real_per_learner"] / pair.iloc[0]["real_per_learner"] - 1)
        nominal_change = 100 * (pair.iloc[1]["amount_m"] / pair.iloc[0]["amount_m"] - 1)
        subset_change = (f"For the verified three-university subset, real expenses per FLE were "
                         f"{abs(real_change):.1f}% {'lower' if real_change < 0 else 'higher'} "
                         f"in {pair.iloc[1]['period']} than {pair.iloc[0]['period']}, while "
                         f"nominal expenses on this definition {'rose' if nominal_change >= 0 else 'fell'} "
                         f"{abs(nominal_change):.1f}%.")
    else:
        subset_change = "The three-university expense evidence currently supports dated levels only."
    return f"""# Alberta education: resources, learners and delivery

**Evidence brief · September 2026 source refresh · constant 2012 Canadian dollars**

> **What changed.** {subset_change} The latest matched K–12 school-authority expense level is **{kexp}**. **Why it matters.** School-authority revenue, institutional expense and provincial budgets answer different questions; enrolment reporting and accounting breaks constrain trend readings. **Decision supported.** Review the dated periods shown below and commission a common original-budget bridge before assessing plan delivery. These data identify questions for investigation; they do not establish funding adequacy or causation.

## 1 · Provincial support

![Two aligned sector panels of real provincial support per learner, with gaps at changes in accounting or enrolment reporting.](plots/provincial_support.png)

**Finding.** The latest supported K–12 recognized provincial revenue excluding capital recognition is **{kgrant}**. The latest supported post-secondary departmental operating grants to 20 public institutions are **{pgrant}**. These are dated levels, not a cross-sector funding rank. The latest 20-institution post-secondary ratios are withheld where the FLE source flags reporting problems.

**Policy question.** Which changes in each *comparable* reporting segment warrant a source-level review of grant decisions and learner demand?

**Limits.** K–12 revenue includes reported provincial pension support and excludes directly collected opted-out-board property tax; it is not cash grants or total support. Its classification changes in 2018–19, 2022–23 omits Valhalla, and the 2023–24 compilation includes draft Northland reporting. The post-secondary numerator includes all department operating-grant programs, not just base grants; historical program boundaries are not fully harmonized. Fiscal and academic periods only approximately align. Earlier FLE years may also reflect the thesis-reporting issue flagged later; its size is unknown. [Download observations](budget_data/per_learner.csv) · [Coverage and reasons](budget_data/coverage.csv) · [Methods](docs/METHODOLOGY.md)

## 2 · Institutional resources

![Two aligned sector panels of real institutional expense per learner, explicitly identifying the post-secondary three-university subset.](plots/institutional_resources.png)

**Finding.** The latest matched school-authority expense excluding amortization is **{kexp}**. For the defined three undergraduate universities—Alberta University of the Arts, MacEwan and Mount Royal—the latest expense excluding amortization and identified capital disposal losses is **{pexp}**. {subset_change} This subset does not describe the whole post-secondary system.

**Policy question.** Do changes in expenses per learner reflect staffing, facilities, pensions, research, ancillary activity or other functions, and how do institutions explain them?

**Limits.** Both expense measures include activity beyond classroom instruction. The three-university financial and FLE periods do not have identical month boundaries. Neither expense series is interchangeable with its provincial grant series. [Download observations](budget_data/per_learner.csv) · [Definitions](data/series.json) · [Methods](docs/METHODOLOGY.md)

## 3 · Plans and delivery

![Four evidence cards show whether an original budget can be compared with an actual for the same sector, measure, year and accounting boundary.](plots/plans_and_delivery.png)

**Finding.** {delivery_statement} {delivery_context}

**Policy question.** {delivery_question}

**Limits.** {delivery_limits} [Matched-pair table](budget_data/delivery.csv) · [Source manifest](data/sources.json) · [Budget rules](docs/METHODOLOGY.md)

## Demand and evidence coverage

{_coverage_table(result)}

K–12 uses matched September school-authority **headcount**; post-secondary uses approved-program **full-load equivalents (FLE)**. Their units, institutions and periods differ. The 2025–26 K–12 enrolment is preliminary; matched financial actuals end earlier. The 20-institution post-secondary FLE counts for 2023–24 and 2024–25 are retained as reported demand context but excluded from ratios. [Download enrolment](budget_data/demand.csv) · [Coverage grid](budget_data/coverage.csv) · [Population context](budget_data/population.csv)

### Evidence and reproduction

The [K–12 financial-statement index](https://www.alberta.ca/k-12-education-financial-statements) calls its combined statements a “roll-up provincial total”; the [2023–24 source record](data/raw/k12/metadata-2023-2024.json) states “Includes draft reporting for The Northlands School Division”. The [Advanced Education 2024–25 annual report](https://open.alberta.ca/dataset/9c785a4b-e79a-465b-8fa9-322a322f1f15/resource/f0581939-0ba9-4bd8-8290-3148f224ec76/download/ae-annual-report-2024-2025.pdf) says its operating-grant schedule includes funding “from all department programs.” CPI comes from [Statistics Canada Table 18-10-0005-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000501). Original files, hashes and retrieval details are in the [source manifest](data/sources.json); the [data contract](docs/DATA_CONTRACT.md), [methodology](docs/METHODOLOGY.md) and [validation report](docs/VALIDATION.md) explain selection, exclusions and checks.

Install the pinned dependencies with `python -m pip install -r requirements.txt -c constraints.txt`, then rebuild the figures, derived tables and this brief offline with `python generate_all_charts.py`. Run the tests with `python -m unittest discover -v`. Use `--output-dir PATH` for an isolated build. The repository keeps the prior exploratory work in [the archive](archive/README.md).
"""


def build(destination: Path) -> dict:
    result = build_analysis(ROOT)
    destination.mkdir(parents=True, exist_ok=True)
    tables = destination / "budget_data"
    plots = destination / "plots"
    tables.mkdir(exist_ok=True)
    for key, name in (("per_learner", "per_learner"), ("coverage", "coverage"),
                      ("demand", "demand"), ("delivery", "delivery"),
                      ("population", "population")):
        result[key].to_csv(tables / f"{name}.csv", index=False, float_format="%.6f")
    (tables / "summary.json").write_text(json.dumps(result["summary"], indent=2) + "\n",
                                         encoding="utf-8")
    resources(result, "grants", plots)
    resources(result, "expenses", plots)
    plans_delivery(result, plots)
    (destination / "README.md").write_text(_brief(result), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT,
                        help="Destination for README, plots and derived tables (default: repository root)")
    args = parser.parse_args()
    build(args.output_dir.resolve())
