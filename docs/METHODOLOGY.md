# Reading the evidence

## Two sectors, two financial questions

The provincial-support panels show selected recognized provincial revenue for school authorities and departmental operating grants for post-secondary institutions. The institutional-resource panels show expenses with explicit exclusions, across the included revenue sources. These measures must not be interchanged. The difference between them is not automatically own-source revenue: timing, accounting recognition, transfers and consolidation can prevent that identity.

K–12 and post-secondary have equal prominence in this publication. They do not necessarily share a reporting period, institutional boundary, learner definition or comparable historical starting year. Comparing dollar levels across sectors does not establish relative efficiency or appropriate funding.

| Published measure | Financial boundary | Matched learner boundary |
|---|---|---|
| K–12 provincial revenue | Recognized Government of Alberta revenue less capital recognition and inter-authority revenue; includes reported provincial pension contributions, excludes direct opted-out-board property taxes | September headcount including ECS at the same reporting authorities; excludes Lloydminster boards and, in 2022–23 only, Valhalla |
| K–12 institutional expenses | Combined school-authority expenses less amortization; includes non-instructional functions, pensions, finance costs and expensed capital-related work | Same authority roster and school year as the revenue series |
| Post-secondary provincial grants | Department operating grants from all programs to 20 public institutions, excluding Banff and separately reported infrastructure grants | Reported approved-program FLE for those same 20 institutions; domestic and international learners |
| Post-secondary institutional expenses | MacEwan, Mount Royal and Alberta University of the Arts: total expenses less tangible/intangible amortization and separately identified capital disposal losses | Approved-program FLE at those three universities only |

The expense measures are not identical across sectors and neither is classroom or instructional cost. The post-secondary subset is not representative of the full sector. The three universities' fiscal years end March 31 (MacEwan and Mount Royal) or June 30 (AUArts). Their academic counts are approximately aligned by starting-year label, not exact month.

Detailed accounting bridges and original source locators are retained in the [K–12 admission notes](../data/staging/k12/K12_EVIDENCE_NOTES.md) and [post-secondary admission notes](../data/staging/postsec/COVERAGE.md). K–12's 2023–24 compilation includes draft Northland reporting; it is not a uniformly finalized audited total. The departmental grant schedules are supplemental and unaudited where the source labels them so.

## Price adjustment

The build uses Statistics Canada Table 18-10-0005-01, Alberta, All-items, annual average, 2002=100. It expresses real values in constant 2012 dollars:

```text
real amount = nominal amount × CPI(2012) / CPI(period starting year)
real amount per learner = real amount × 1,000,000 / matched learners
```

The multiplication converts the standardized nominal input unit (CAD millions) to dollars. The starting-calendar-year CPI is a reproducible approximation for school, academic and fiscal periods that cross calendar years. It measures general consumer prices rather than the mix of wages, benefits, materials and other education input costs.

## Periods and learners

Financial observations retain their source period. Each series records an approved denominator and a reason that its institutions and period match the numerator. Headcount, full-time equivalent (FTE) and full-load equivalent (FLE) are distinct units. Preliminary denominators remain labelled, and their ratios inherit that uncertainty. Provincial population is contextual information only; it never fills a missing enrolment denominator.

Known post-secondary reporting issues make the 20-institution ratios ineligible for 2023–24 and 2024–25. Earlier eligible ratios are reported levels with source warnings, not a fully harmonized trend: the thesis-reporting issue may affect earlier years and its magnitude is unknown. The three-university subset has no reporting-change entries for its two published years in the current source workbook. Its two-year comparison remains descriptive.

## Original plans and actual results

Budget-delivery comparisons use nominal amounts for the same measure, sector, period and accounting segment:

```text
dollar variance = actual − original budget
percentage variance = 100 × (actual − original budget) / original budget
```

A later forecast or restated budget is not a replacement for the original plan. Where the original budget cannot be verified on a matching boundary, the comparison is unavailable. A positive variance is not automatically success and a negative variance is not proof of fewer services. Explanations require the relevant report's variance notes.

## Missing evidence and scope changes

Missing values are never filled by interpolation or converted to zeros. Actuals, budgets and forecasts remain separate. Source releases are selected explicitly rather than by a generic most-recent-row rule. Financial observations carry a comparability segment; figures do not connect different segments or missing years.

Trend lines require at least three consecutive comparable observations. A comparable pair can support a dated change, while a single observation supports a level only. Unsupported denominators or financial classifications produce an evidence gap with a stated next step.

## Interpretation

These are descriptive comparisons, not causal estimates or funding-adequacy standards. They can identify periods and accounting differences for review. They cannot independently explain classroom conditions, institutional productivity, student outcomes or the resource level required to attain a policy target.

The source manifest and data dictionary provide the audit trail. The publication build reads archived local inputs and works offline. Source retrieval and extraction are separate preparation steps.
