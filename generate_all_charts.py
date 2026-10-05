"""Rebuild the current education brief and retained historical evidence offline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from analysis import ROOT, build_analysis
from chart_rendering import plans_delivery, resources
from report_analysis import build_current_report, load_current_data
from extended_report import build_extended_report


def _brief(current: dict, reviewed: dict) -> str:
    hist, funding, _ = load_current_data()
    old = hist[hist.year <= 2021]
    actual = reviewed['actual']
    cohort = reviewed['cohort']
    migration = reviewed['migration']
    child = migration['age_5_17_latest']
    outcomes = reviewed['outcomes']
    math = outcomes['grade9_math']
    diploma = outcomes['diploma_math']
    classes = reviewed['classes']['grade_bands']['G7-9']
    return f"""# Alberta schools: reported real expenses fell; newer funding rose

**For {cohort['common_authority_count']} continuing authorities, reported expenses excluding amortization per pupil fell {abs(float(cohort['real_reported_expense_per_student_change_percent'])):.1f}% after inflation from 2023–24 to 2024–25. Revised allocations per pupil rose {current['current_real_change']:.1%} after inflation from 2024–25 to 2025–26.** Accounting changes limit the spending comparison; allocations are a different measure.

## Spending and funding

Amounts are Canadian dollars. This report covers schools; [methods and broader education context](docs/CURRENT_METHODS.md) retain post-secondary totals, childcare exclusions and operating/capital boundaries.

![Reported expenses per pupil fell 1.3% for 79 continuing authorities; inflation-adjusted allocations per pupil rose 4.6%; the separate 83-authority 2024–25 level is also shown.](plots/funding_and_actuals.png)

The comparison uses statement comparatives and matched September headcounts for 79 authorities covering **{float(cohort['coverage']['current_common_cohort_percent']):.1f}%** of the 2024–25 pupils in our public system scope. Restatements and Valhalla's qualified fundraising audit mean it measures reported expenses, not a fully harmonized change in classroom resources. [Independent audit review](docs/research/refresh-finance/comparative79_review.md).

All {actual['authority_count']} matched 2024–25 statements separately yield **${float(actual['real2025_expenses_per_student']):,.0f} per pupil in 2025 dollars**. These are researcher aggregations. The older like-for-like 2016–22 decline was {abs(current['historical_real_change']):.1%}; accounting and coverage breaks prevent joining the series.

Expenses include all authority revenue sources; allocations are provincial funding. Annual scope includes public, separate, francophone and charter authorities plus Early Childhood Services, excluding Lloydminster. The allocation comparison uses **preliminary 2025–26 enrolment, labelled “as of December 2025”**, versus final September 2024 enrolment, with four new charters. CPI measures general purchasing power, not school input costs.

## Outcomes are mixed; service capacity needs checking

The [December 2025 official update]({outcomes['source']['url']}) extends assessment evidence to 2024–25:

| Acceptable-standard attainment | 2023–24 → 2024–25 | Change |
|---|---|---:|
| Grade 9 mathematics, enrolled denominator | {math['earlier']:.1f}% → {math['later']:.1f}% | {math['change_pp']:+.1f} percentage points |
| Diploma mathematics, exam-writer denominator | {diploma['earlier']:.1f}% → {diploma['later']:.1f}% | {diploma['change_pp']:+.1f} percentage points |

Grade 9 mathematics participation rose {math['participation_earlier']:.1f}% → {math['participation_later']:.1f}%. Regular Mathematics 9 results also weakened among exam writers. Different cohorts and denominators limit comparison; these outcomes predate the 2025–26 allocation increase. [Completion and assessment definitions](docs/research/refresh-outcomes/FINDINGS.md).

A newer classroom snapshot shows **{classes['over30_percent_of_all_included_records']:.1f}% of included Grade 7–9 class records exceeded 30 pupils** as of 24 November 2025. These selected self-reported public/separate/francophone groups exclude specified programs; pupils repeat across records. This is a capacity signal, not a unique-pupil count or spending effect.

## Immigration and migration change the demand picture

![Net international and interprovincial migration of children aged 5–17 remained positive, reaching 13,624 in 2025–26. These demographic counts are not school admissions.](plots/migration_demand.png)

In **July 2025–June 2026**, Alberta gained an estimated **{child['Total net migration']:,} net migrants aged 5–17**: {child['Net international migration']:,} internationally and {child['Net-migration']:,} from other provinces. The immigrant component counted {child['Immigrants']:,} permanent-resident admissions, including status changes rather than only new arrivals.

All-age net non-permanent-resident change was negative, yet it remained **+{child['Net non-permanent residents']:,} for ages 5–17**. An overall population slowdown therefore cannot substitute for school-age forecasts. Age-at-July 1 estimates omit younger ECS pupils and students 18+, and do not measure new enrolment, local settlement or language needs. [Migration evidence and revisions](docs/research/migration/FINDINGS.md).

**The available datasets do not establish that spending or immigration caused these outcome changes.**

```mermaid
flowchart LR
    M[Migration and cohort change] -. Demand to measure .-> N[Local enrolment and assessed needs]
    F[Real funding] -. Delivery to verify .-> S[Staffing, space and supports]
    N -. Capacity to plan .-> S
    S -. Effect to evaluate .-> O[Learning and completion]
    C[Pandemic and assessment changes] --> O
```

## Decisions

- **Ministry and authorities:** audit forecast errors and midyear adjustment timing under the existing 30% current-year/70% projected-year enrolment model. Use local registrations, withdrawals, grade cohorts and assessed needs; separately cost staff and space. Planned 2026–27 allocations grow {current['future_allocation_growth']:.1%}, but missing matched enrolment prevents a per-student estimate.
- **Authorities:** prioritize numeracy and timely language/learning support according to assessed need. Track enrolment-to-assessment waits, delivered support hours, attendance and learning progress. Compare baseline-adjusted progress and delivered supports with comparable schools and prior trends; a full-year review is an initial checkpoint before scaling. Do not treat immigrant status as a learning deficit.
- **Reviewers:** independently reconcile source definitions and arithmetic, challenge causal claims, revise, and recheck. The [recorded critique loop](docs/reviews/extended-policy-review.md) identifies remaining uncertainty rather than promising a funding payoff.

## How we obtained and checked the evidence

**Verified 5 October 2026:** we enabled narrowly scoped official-domain access, checked live catalogues, downloaded the latest located statements/update/classroom files, and independently validated extraction, coverage, CPI periods and migration identities. Migration uses a consistent **23 September 2026 revised vintage**; mixing it with older population snapshots would give incorrect results. Large downloads stay in caches; bounded extracts, checksums and reproducible scripts preserve the evidence. [Source ledger and resource record](docs/research/extended-session-log.md).

Allocations and August 2026 CPI were unchanged on live recheck. No 2025–26 ministry annual report or assessment release was located in checked official listings. The evidence is latest verified, not a guarantee of completeness. The PDF remains the September snapshot; **this README is the updated report**.

```bash
source .venv/bin/activate
export XDG_CACHE_HOME="$PWD/.venv/cache" MPLCONFIGDIR="$PWD/.venv/matplotlib"
python -m unittest discover -v
python generate_all_charts.py --output-dir validation-output
```
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
    reviewed = build_extended_report(destination)
    (destination / "README.md").write_text(_brief(current, reviewed), encoding="utf-8")
    result["current_report"] = current
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT,
                        help="Destination for README, plots and derived tables (default: repository root)")
    args = parser.parse_args()
    build(args.output_dir.resolve())
