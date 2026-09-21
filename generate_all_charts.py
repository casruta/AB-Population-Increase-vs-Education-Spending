"""Rebuild the current education brief and retained historical evidence offline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from analysis import ROOT, build_analysis
from chart_rendering import plans_delivery, resources
from report_analysis import build_current_report


def _brief(current: dict) -> str:
    return f"""# Alberta education funding per student

**Evidence updated 20 September 2026. All amounts are Canadian dollars.**

Funding per student has increased in the latest allocations. Earlier school spending lost purchasing power after inflation.

[Read the concise report](reports/alberta_education_brief.pdf) · [Download the data](budget_data/education_evidence.csv) · [Methods and sources](docs/CURRENT_METHODS.md)

## Recent funding increased

Revised operating funding rose from **$10,309 per student in 2024–25** to **${current['current_nominal_per_student']:,.0f} in 2025–26**. That is **{current['current_nominal_change']:.1%} growth in dollars**, or **{current['current_real_change']:.1%} after inflation**.

Total funding on the matched school-authority boundary increased from **$7.717 billion to $8.362 billion**. Student headcount grew by **0.85%**, from 748,521 to 754,880.

![Revised operating funding per student in 2024–25 and 2025–26, shown in nominal and inflation-adjusted dollars.](plots/recent_funding.png)

These are revised funding allocations, not audited spending. The funding schedule includes “in-year adjustments”; the 2025–26 student count is preliminary.

The comparison covers public, separate, francophone and charter authorities, including Early Childhood Services. Both Lloydminster boards are excluded from funding and student counts.

## Earlier spending lost purchasing power

Actual school-authority expenses per student were almost unchanged between 2016–17 and 2021–22: **$11,358 versus $11,356**.

After inflation, spending fell from **$14,334 to $12,559 in 2025 dollars**—a **{abs(current['historical_real_change']):.1%} decline**. Total expenses rose from $7.402 billion to $7.719 billion while enrolment increased.

![Actual school spending per student from 2016–17 to 2021–22, showing nominal dollars and purchasing power in 2025 dollars.](plots/historical_spending.png)

This measure includes instruction, transport, facilities and administration, excluding amortization. It measures spending across schools, not a single grant rate.

The later 2023–24 return records **$8.463 billion**, or **$11,647 per student**. That is a separately reported level because later returns changed accounting and coverage.

Calgary Board of Education provides a recent local example. Its 2024–25 adjusted funding was **$9,622 per student**, versus an inflation-preserving benchmark of **$11,048**—a **12.9% gap**. This is a Calgary measure, not a provincial estimate.

## What the 2026–27 plan provides

Projected public-school operating allocations total **$8.943 billion**. On the matched boundary excluding Lloydminster, the amount is **$8.896 billion**, up **{current['future_allocation_growth']:.1%}** from 2025–26.

Preserving purchasing power per student requires the combined effect of enrolment growth and cost inflation not to exceed that increase. The 2026–27 figure remains a funding plan.

## Overall education spending

Alberta's consolidated education expenses were **${current['broad2024_total']/1e9:.3f} billion in 2024–25**, approximately **${current['broad2024_per_resident']:,.0f} per resident**.

**Budget 2026 provides ${current['broad2026_total']/1e9:.3f} billion**, equivalent to **${current['broad2026_per_resident']:,.0f} per resident** using April 1, 2026 population. These are respectively actual and budget amounts.

This broader measure includes post-secondary education and institutional own-source spending. It excludes childcare and must not be added to school grants or divided by school pupils.

Within the 2026–27 operating budget, the school system receives **$10.755 billion** and Advanced Education **$7.110 billion**. Childcare's **$2.110 billion** is kept outside school comparisons.

## What to do next

Protect real funding per student by adjusting the operating baseline for enrolment growth and costs. Add separately costed learning-support priorities, then track teachers, education assistants and support capacity alongside dollars.

At the matched 2025–26 headcount, an extra **$100 per student costs about $75.5 million annually**. Distinguish ongoing funding from temporary additions when costing improvements.

## Sources and reproduction

The current report uses [Alberta operating allocations](https://www.alberta.ca/system/files/ecc-projected-operational-funding-school-authorities.pdf), [student statistics](https://www.alberta.ca/student-population-statistics), official financial statements and Statistics Canada. Full links, definitions and accounting boundaries are in the [methodology](docs/CURRENT_METHODS.md) and [source manifest](data/latest/source_manifest.json).

Inflation is matched to each September–August school year and expressed in **2025 dollars**. Monthly CPI extends through August 2026. Historical audit tables retain their separately documented 2012-dollar convention.

```bash
python -m pip install -r requirements.txt -c constraints.txt
python generate_all_charts.py
python -m unittest discover -v
```

The build runs offline. Use `--output-dir PATH` for an isolated build. The PDF is the reviewed September 2026 snapshot; the README, charts and evidence tables rebuild from checked-in inputs.
"""


def build(destination: Path) -> dict:
    destination = Path(destination)
    result = build_analysis(ROOT)
    destination.mkdir(parents=True, exist_ok=True)
    tables = destination / "budget_data"
    plots = destination / "plots"
    tables.mkdir(exist_ok=True)
    for key in ("per_learner", "coverage", "demand", "delivery", "population"):
        result[key].to_csv(tables / f"{key}.csv", index=False, float_format="%.6f")
    (tables / "summary.json").write_text(json.dumps(result["summary"], indent=2) + "\n", encoding="utf-8")
    resources(result, "grants", plots)
    resources(result, "expenses", plots)
    plans_delivery(result, plots)
    current = build_current_report(destination)
    (destination / "README.md").write_text(_brief(current), encoding="utf-8")
    result["current_report"] = current
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT,
                        help="Destination for README, plots and derived tables (default: repository root)")
    args = parser.parse_args()
    build(args.output_dir.resolve())
