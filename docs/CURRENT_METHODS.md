# Current report methodology

## October 2026 extension

The README was refreshed on **5 October 2026**. It now leads with a separately reviewed comparison of **79 continuing school authorities**: inflation-adjusted reported expenses excluding amortization per pupil fell **1.3% from 2023–24 to 2024–25**. Both years use matched September headcounts, current-statement comparative expense columns and complete September–August CPI periods. This cohort covers 99.9% of the matched 2024–25 public-system headcount; it is not a full-province total or a fully harmonized measure of delivered classroom resources. Restatements, accounting policies and Valhalla’s fundraising audit qualification limit interpretation. See the [comparative audit review](research/refresh-finance/comparative79_review.md).

A separate reconstruction of all 83 matched 2024–25 statements yields $8.787 billion of expenses excluding amortization and approximately **$11,814 per pupil in 2025 dollars**. These are researcher aggregations of official individual statements. They do not replace a government-issued combined statement or extend the historical 2016–22 trend. Northland’s finalized 2023–24 audit, signed 23 July 2025, was checked after the earlier combined report included draft information.

Current source verification leaves revised funding unchanged at +4.6% real per pupil for 2024–25 to 2025–26. This comparison uses matched annual sector coverage, not a fixed authority cohort: four charters enter the later roster. The later enrolment is preliminary and its source footnote says “as of December 2025”; the source also defines registered-student counts by September 30. Do not infer a fully comparable December census from the footnote alone.

The [source ledger](research/extended-session-log.md) and focused [outcome](research/refresh-outcomes/FINDINGS.md), [migration](research/migration/FINDINGS.md) and [policy review](reviews/extended-policy-review.md) document newer evidence. Migration uses one September 23, 2026 revised vintage, age at start-year July 1 and July–June periods; it is not pupil enrolment. Assessment and class-size populations differ from the financial scope. No linked evidence identifies funding or immigration as a cause of outcome changes. The remaining sections describe the retained September 2026 methodology and inputs.


Evidence date: **20 September 2026**. The README separates historical school expenses, recent operating allocations and consolidated education expenses. These are different financial measures and are never joined into one trend.

## Historical school spending

Divide combined school-authority expenses excluding amortization by matched September student headcount, including Early Childhood Services. Public, separate, francophone and charter authorities are included. Both Saskatchewan-based Lloydminster boards are excluded.

The like-for-like trend covers 2016-17 through 2021-22. The 2023-24 amount is a separately reported later level: subsequent returns changed accounting and coverage, and the compilation includes draft Northland reporting. The supporting 2022-23 record excludes Valhalla and must not be used to claim an uninterrupted like-for-like trend.

Historical inputs and exact financial components remain in `data/spending.csv`, `data/enrolment.csv` and `data/staging/k12/`. Original source records remain in `data/sources.json`.

## Recent school funding

Use Alberta's published operational-funding schedules for school authorities. The prior-year columns include in-year adjustments. They are revised allocations, not original budgets or audited expenses.

| School year | Matched operating allocation | Matched students | Status |
|---|---:|---:|---|
| 2024-25 | $7,716,613,874 | 748,521 | Revised allocation; final headcount |
| 2025-26 | $8,361,644,972 | 754,880 | Revised allocation; preliminary headcount |
| 2026-27 | $8,896,073,124 | — | Projected allocation |

Start with the published public total and subtract both Lloydminster divisions' funding and student counts. This avoids assuming that Alberta's contribution to a cross-border division has the same residency boundary as students attending Alberta-located schools.

For 2024-25, subtract funding of $24,656,179 and $17,596,861 and headcounts of 2,942 and 2,763. For 2025-26, subtract $25,733,439 and $19,506,031 and headcounts of 3,073 and 2,734. For 2026-27, subtract $26,569,105 and $20,328,104. Do not manufacture a 2026-27 per-student figure using a previous-year count.

Sources: [Budget 2025 operating allocations](https://www.alberta.ca/system/files/educ-budget-2025-projected-operational-funding-school-jurisdictions.pdf), [Budget 2026 operating allocations](https://www.alberta.ca/system/files/ecc-projected-operational-funding-school-authorities.pdf), and [Alberta student statistics](https://www.alberta.ca/student-population-statistics), Table 2 and authority enrolment files.

## Inflation

Average Alberta's monthly all-items CPI from September through August for each school year. Express purchasing power in calendar-2025 dollars, using CPI 172.2 as the base.

```text
nominal dollars per student = amount in dollars / matched headcount
2025 dollars per student = nominal dollars per student × 172.2 / school-year mean CPI
```

The source is [Statistics Canada Table 18-10-0004-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401), vector `v41692327`. The September 14, 2026 release includes August 2026, completing the 2025-26 school year. Every average requires 12 distinct months.

This improves the previous period-start calendar-year approximation: the 2016-17 to 2021-22 real decline is **12.38%**, compared with 9.46% under the old convention. Household CPI measures general purchasing power, not the exact mix of school wage and other input costs.

## Overall education spending per resident

Divide consolidated education-function expense by Alberta's April 1 population at the start of the fiscal year. This broad measure includes post-secondary institutions' own-source expenses and amortization, excludes childcare, and must not be added to school grants or divided by school pupils.

| Fiscal year | Education expense | April 1 population | Nominal expense per resident |
|---|---:|---:|---:|
| 2024-25 actual | $17.197 billion | 4,857,695 | $3,540.16 |
| 2026-27 Budget 2026 | $19.388 billion | 5,057,077 | $3,833.84 |

Sources: [Alberta Annual Report 2024-25](https://open.alberta.ca/dataset/7714457c-7527-443a-a7db-dd8c1c8ead86/resource/e6c7f85c-73bc-44d3-af00-edebf01d82a1/download/goa-annual-report-2024-2025.pdf), printed page 25; [Budget 2026 Fiscal Plan](https://open.alberta.ca/dataset/3393a7b5-07bf-4b9f-8aaf-a6d89273297b/resource/58a8d024-398f-482e-b1c2-81a754a97253/download/budget-2026-fiscal-plan-2026-29.pdf), printed page 162; and [Statistics Canada population estimates](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000901), June 17, 2026 release.

The August 27, 2026 first-quarter update leaves Education and Childcare and Advanced Education ministry operating totals unchanged. It does not publish a revised education-function total, so $19.388 billion remains explicitly labelled **Budget 2026**.

## Interpretation and refresh

For 2026-27, subtract $2.110 billion of childcare from the $12.865 billion ministry operating envelope to obtain $10.755 billion for the school system. Advanced Education's operating envelope is $7.110 billion. Construction cash investment is separate from these operating measures.

Calgary Board of Education's local 2024-25 funding comparison excludes specified pension, transport, capital-related and one-time amounts. It supports a local illustration, not a province-wide estimate or an extension of the expenditure trend. Its [financial results](https://cbe.ab.ca/about-us/budget-and-finance/Documents/Financial-Results-2024-25.pdf), PDF page 8, report $9,622 per student against an inflation-preserving benchmark of $11,048.

Refresh source vintages, amounts, status and matched authority counts together. Preserve original files and locators, validate complete CPI periods, and rebuild the report. Review the exported charts at ordinary reading size before publication.

The downloadable PDF is the reviewed September 2026 publication snapshot. The README, charts and evidence table are reproducible outputs; refreshing inputs does not silently revise the dated PDF.
