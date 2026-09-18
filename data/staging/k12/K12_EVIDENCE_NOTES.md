# K-12 source admission and reconciliation

Prepared 18 September 2026 from official Alberta source snapshots. Amounts in the component table are exact CAD; staged spending is CAD millions. Periods are **school years, September 1 through August 31**, not Alberta government April–March fiscal years.

## Admitted measures

1. `k12_operating_expenses`: combined school-authority total expenses minus total amortization in the statement of cash flows. Recommended publication label: **School-authority expenses excluding amortization**. It includes instruction, facilities operations/maintenance, transport, administration and external services; includes pensions, finance costs, asset-retirement accretion and any capital-related work expensed in the year. It is neither cash expenditure nor a measure of classroom instruction alone. Capital acquisitions do not enter this accrual expense numerator. Annual financial amounts are verified for 2012–13 through 2023–24.
2. `k12_operating_grants`: **Recognized provincial revenue excluding capital recognition**, on an accrual basis. Before 2018: Alberta Education plus Other Government of Alberta revenue, less their separately identified recognized capital revenue. From 2018: Statement of Operations Government of Alberta revenue, less Other Alberta school authorities revenue, less GoA spent-deferred-capital recognition, less signed GoA unspent-deferred-capital transfers to grant revenue. All deductions appear separately in `k12_components.csv`. The 2018 unspent Education amount is a reversal, so its signed value is negative and subtracting it adds it back. This is not cash grant payments, original appropriations or all education-related public support.

The grants measure includes provincial pension contributions reported as revenue and funding supported by education property tax flowing through the provincial fund. It excludes the distinct Property Taxes revenue line, including directly collected opted-out-board taxes; therefore it must not be described as total provincial education support. Source schedules classify other-government revenue and capital contributions, rather than asserting all noncapital receipts are discretionary classroom operating grants.

No financial budget is admitted for a delivery comparison. Combined statements say **Budget**, but original versus revised/adopted provenance was not established. They also report total-expense budgets including amortization; an original budget for the net-of-amortization measure was not extracted. `k12_reported_budgets_not_admitted.csv` retains these observations without manufacturing an original-budget comparison.

## Institution and learner match

Public, separate, francophone and charter school authorities are included. Exclude private/independent schools and ECS operators, federal/First Nations-operated schools and provincial authorities. Students at public authorities who identify as First Nations are included; the exclusion concerns school operator, not student identity. ECS is included. Enrolment is headcount, not a weighted/funded count or FTE.

The financial rollup excludes the two Saskatchewan-based Lloydminster boards, while enrolment's Public/Separate categories include their Alberta-located schools. Exclude authority codes **3170 and 4870** from each year. For 2022–23 also exclude **0224 Valhalla School Foundation**, because that year's combined report explicitly omits its unfinalized financial statements. Do not compare across this temporary coverage break as a like-for-like growth result.

`k12_authority_enrolment.csv` records each admitted/excluded row, code and exact source cell. `k12_enrolment.csv` sums only admitted rows. **Every financial-summary authority roster from 2016–17 through 2023–24 matches the admitted enrolment codes exactly**, with 74, 74, 74, 74, 74, 76, 77 and 80 authorities respectively. `roster_checks.json` records this check, and source-manifest entries retain each official roster PDF. No separate home-education count is added: supervised/shared-responsibility students already appear within authority data.

Matched headcounts verified from official authority XLSX files exist for 2016–17 through 2025–26. Financial per-learner publication ends 2023–24; 2024–25 has no published combined financial rollup in the current official index. The 2025–26 enrolment file is explicitly preliminary. Earlier financial amounts remain useful in nominal/real history, but 2012–13 through 2015–16 per-learner results are gaps until matching official headcounts are verified.

## Comparability and source limitations

- Preserve the original current-year compiled observation. Later-year statements contain restated prior-year comparators; do not splice a revised revenue total together with unrevised capital-recognition components. The original PDFs archive those comparators for a future fully reconciled restatement refresh.
- The 2018–19 statement newly groups Government of Alberta revenue and its prior-year comparative restates GoA/property-tax classifications. Grants have a comparability break at 2018; expense series do not inherit this revenue-only break.
- The 2022–23 statements introduce asset-retirement accounting and omit Valhalla. The published 2023–24 rollup restores Valhalla and includes draft reporting from Northland School Division. These are explicitly distinct segments. The 2023–24 figure is an official compiled actual with a draft component, **not a uniformly finalized audited total**.
- The 2012–13 capital schedule combines recognized capital revenue across origins, preventing a verified provincial-only subtraction. The 2013–14 catalogue links the same 2012–13 capital schedule (check its period), so it cannot validate 2013–14 provincial capital recognition. Grants for both years are intentionally absent.
- For 2014–17 the separate capital-revenue schedule supplies recognized amounts by Alberta Education and Other GoA. From 2018 the deferred-contributions schedule supplies both spent-capital amortization and unspent-capital direct recognition. The method follows the published classification, with no interpolated amounts.
- Financial publication dates are the official catalogue `issuedate`, which may reflect later portal publication rather than the historical initial release. Enrolment dates use the portal resource-created/upload timestamp; original publication dates are not independently verified. Each source records this date basis explicitly.
- The combined expenses are a provincial rollup, not a consolidation eliminating all inter-authority purchases. The provincial-revenue measure explicitly excludes receipts from Other Alberta school authorities where grouped into GoA. Do not imply the two numerators are a complete reconciled funding balance.

## Key official source statements

- The financial index describes combined statements as a “roll-up provincial total” compiled from individual statements: https://www.alberta.ca/k-12-education-financial-statements.
- 2023–24 catalogue explicitly says: “Includes draft reporting for The Northlands School Division”. See `data/raw/k12/metadata-2023-2024.json`.
- 2022–23 catalogue says statements “do not include reporting for Valhalla Charter School”. See `data/raw/k12/metadata-2022-2023.json`.
- Student statistics defines the reference date as “registered as of September 30 of the school year”: https://www.alberta.ca/student-population-statistics. Cached page is in the raw archive.

## Preparation and checks

`prepare_evidence.py` recreates staged CSV/JSON from archived official sources. It checks manually read financial values occur in the exact source, preserves every netting component, verifies authority grade sums against published Total cells, checks authority-code uniqueness, and records SHA-256 for referenced originals. PDF pages for the recent operation/capital schedules and the 2018 classification change were rendered and visually inspected. Independent review checks source figures, scope matching and eligibility; passing arithmetic alone does not prove financial meaning.

Staging is an integration handoff, not the published data contract. Parent integration should carry these labels, coverage segments and missing-denominator rules into the maintained `data/` tables and policy README. The raw archive currently includes some duplicate exploratory downloads; only source-manifest-referenced files and essential coverage metadata need be retained in the published archive.
