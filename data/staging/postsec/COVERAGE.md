# Post-secondary evidence admission notes

Prepared 2026-09-17. Data files here are staging inputs for integration, not a second analysis pipeline.

## Operating grants: admitted as annual reported actual levels

`grants.csv` contains all extracted source vintages and an explicitly reviewed selection map in `extract_evidence.py`. Values are CAD millions, calculated from the source's CAD-thousands total for public post-secondary institutions minus Banff Centre. Twenty individual institution lines reconcile with the result (to within $2,000 source rounding). Independent academic institutions, First Nations/other colleges and research entities are excluded. These are **Advanced Education department operating grants from all department programs**, not total Alberta-government transfers, base Campus Alberta grants alone, or institutional expense. Infrastructure grants are a separate source column and excluded. Supplemental schedules are unaudited where the source so titles them; financial status is actual, not budget.

2024-25 report PDF page 104, printed 102 says: "Include funding to these entities from all department programs." This source category—not a ministry total—is the financial numerator. Capital acquisition is not added to operating grants. No original budget for precisely these 20 operating-grant recipients/programs has been verified, so grant budget-delivery coverage remains a gap.

The stable institution set, using current names, is Athabasca, University of Alberta, University of Calgary, University of Lethbridge, Alberta University of the Arts, Grant MacEwan, Mount Royal, Lethbridge Polytechnic, NAIT, Northwestern Polytechnic, Red Deer Polytechnic, SAIT, Bow Valley, Keyano, Lakeland, Medicine Hat, NorQuest, Northern Lakes, Olds and Portage. Name/designation changes do not add institutions: Alberta College of Art + Design → Alberta University of the Arts; Grande Prairie Regional → Northwestern Polytechnic; Red Deer College → Red Deer Polytechnic; Lethbridge College → Lethbridge Polytechnic.

## Explicit observation selections and financial boundaries

Selected year → report-year map: 2012 → 2013, 2013 → 2014, 2014 → 2015, 2015 → 2016, 2016 → 2017, 2017 → 2018, 2018 → 2019, 2019 → 2019, 2020 → 2021, 2021 → 2022, 2022 → 2023, 2023 → 2024, 2024 → 2024. These selections were inspected against named grant tables, not an automatic newest-source rule.

- 2012 uses the 2013-14 restated comparative. The total for 21 public institutions was 2259.176 M in 2012-13 original and 2240.228 M after restatement. Banff 16.444 M unchanged. Department program transfers are not fully bridged; the original remains visible and this is a dated level, not proof of a fully consistent cross-ministry all-program series.
- 2013 is identical in 2013-14 current and 2014-15 comparative: 2154.564 M 21 public institutions, Banff 16.489 M.
- 2014 uses 2015-16 restated comparative 2159.426 M 21 public institutions minus Banff 19.989 M. Original 2014-15 reported 2190.879 M 21 public institutions. This is a financial boundary break; do not bridge it into 2013 without resolving department program transfers.
- 2015–2018 selected comparators agree with original current-year grant totals, with unchanged institutional membership.
- 2019 uses current-year 2019-20 table; 2020-21 source grant table is image-based and was not transcribed. No unverified new comparator substituted.
- 2020 uses the 2021-22 comparative; 2021 uses the 2022-23 comparative. Public totals 2179.354 M and 2044.885 M respectively.
- 2022 uses the explicitly restated 2023-24 comparator 1966.709 M 21 public institutions, rather than original 1918.767 M. Footnote says "Restated amounts includes 2023 re-organization and other adjustments." Banff 15.889 M unchanged. This creates a separate financial segment unless the entire department transfer bridge is established.
- 2023 uses 2024-25 comparator, agrees with original 2023-24 current table 2027.530 M 21 public institutions.
- 2024 uses 2024-25 current table 2101.387 M 21 public institutions minus Banff 16.161 M = 2085.226 M.

Financial segments in staging are provisional boundaries, not certification that all department-program classifications have been historically harmonized. Use annual reported levels. No pooled 2012 → 2024 claim about a fully consistent provincial-support series is warranted.

## FLE: coverage and eligibility

`fle.csv` sums exactly the same 20 public institutions from the official all-learners file, excluding independent academic institutions and all subtotal/system rows. Domestic and international students are included. `fle_institutions.csv` retains exact E-column workbook cells. `fle_reporting_changes.csv` archives EVERY reporting-change row. `fle_metadata.json` retains the full Information, Dictionary and Reporting Changes sheets.

FLE includes ministerially approved programming only; it is neither total headcount nor a count of all institutional activity. Grants can support research and overhead as well as approved-program instruction. Therefore label the ratio **department operating grants per reported approved-program FLE**, not teaching cost per student. Fiscal grants use April–March. Enrolments use institutional academic years (historically July–June, May–April, or Athabasca calendar year); same start-year labels align reporting cycles approximately, not exact months.

Admissions agreed with independent reviewer: 2015–2022 annual levels eligible with flags; 2023 and 2024 ratio withheld; keep their raw FLE as evidence context. 2023 explicitly overreports UAlberta graduate-thesis FLE. 2024 includes Athabasca 16-month transition, NorQuest repeated spring, UAlberta correction. No invented correction is applied. Earlier years may be affected by the thesis issue because the 2023 note says it "continues"; no magnitude is supplied.

Comparability segments: 2015–16; 2017; 2018; 2019–20; 2021; 2022; 2023 ineligible; 2024 ineligible. Relevant breaks: 2015 Olds cleanup; 2017 UAlberta artificial thesis decrease; 2018 Lethbridge credit change; 2019 system Active Learner definition; 2021 MRU/NAIT/SAIT academic-year changes; 2022 Lakeland/Northwestern repeated spring; 2023 their 4-to-3 session transitions and UCalgary correction; 2024 extended reporting and thesis correction. 2016 Keyano wildfire decrease is substantive demand disruption, not an accounting break. 2015 is already post-Olds-cleanup; it cannot be joined backwards to the archived 2014 vintage without a marked break.

## Validation completed

Every grant table extracted has 20 institutional rows; operating-grant column totals reconcile with reported 21 public institutions minus Banff. Workbook 20-public-institution row count is 20 in every year 2015–2024; institution identities stable after name crosswalk. 2024 grant table PDF 104 rendered and visually inspected. Source URLs and SHA-256 in `sources.json`; early release dates unknown where not verified. Raw source actual-vs-budget column labels retained in table text extracts.

## Institutional expense subset: three undergraduate universities, 2023-24 to 2024-25

The broad 20-institution non-amortization operating-expense total was not reconciled from ministry annual reports. Their Public Post-Secondary Institutions line includes 21 institutions, amortization and other accrual items. Budget 2022 has a Total PSI Operating Expense actual of 4600 M for 2020-21 (PDF 133/printed 131), but later source tables contain budgets/forecasts rather than actuals. Neither has been substituted for current institutional actual expenses.

A useful and explicitly narrower subset is available: MacEwan, Mount Royal and Alberta University of the Arts, the three institutions in the official Undergraduate Universities FLE category. These institutions have no 2023/2024 reporting-break entries in the current LERS workbook. All financial periods are 12 months, with MacEwan/MRU ending March 31 and AUArts ending June 30. Academic and fiscal months are approximately aligned by year label, not identical. This subset must never be described as representative of all Alberta post-secondary institutions.

`undergraduate3_expense_components.csv` transcribes audited Expense by Object schedules. Formula is total expense minus tangible and intangible amortization minus separately identified capital disposal losses. Capital acquisitions are absent from these expense schedules by accrual accounting design. All other functions remain: instruction, overhead, research, ancillary services, scholarships, interest and pension costs. This measure is **institutional expenses excluding amortization and identified capital disposal losses**, not the Alberta fiscal-plan operating-expense definition. Inventory consumption and interest remain; calling it simply the same operating expense as the province would be misleading.

Exact amounts (CAD thousands):

| Institution | FY 2023-24 total | Amortization | Identified disposal loss | FY 2024-25 total | Amortization | Identified disposal loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MacEwan | 260105 | 17098 | 1532 | 278164 | 17322 | 0 |
| Mount Royal | 251608 | 15724 | 0 | 270508 | 16490 | 0 |
| AUArts | 26407 | 1338 | 0 | 27403 | 1508 | 0 |

Sum after exclusions 502.428 M → 540.755 M. MRU amortization includes purchased intangibles 32/138 as well as tangible 15692/16352; omitting intangibles would be an error. MacEwan 2023 separately reported loss on sale of tangible capital assets 1532 is removed. Source locations: MacEwan 2024-25 PDF 88/printed 82, note 18; MRU 2024-25 PDF 72/financial-statement printed 31, note 18 (image-only, visually transcribed); AUArts 2024-25 PDF 52/financial-statement printed 24, note 16. Every relevant page rendered and visually checked.

Matched FLE 2023-24 = 26056.497, 2024-25 = 27463.219. Exact underlying source cells: E276:E278 and E308:E310 of 'By Sector and Institution'. Source ratio covers all institutional expenses listed above divided by reported approved-program FLE, so cannot be interpreted as teaching costs or educational adequacy.

The three reports provide 2024-25 budget expense/amortization columns. Budget notes say approved by the Board and submitted to the Minister. They do not explicitly establish whether original or revised; candidate values are preserved in `undergraduate3_budget_candidates.csv` but not admitted for original-budget delivery. All 2023 expense values come from the reviewed comparable columns of the same 2024-25 reports; notes permit comparative reclassification for presentation, so this is a consistent latest-report two-year pair.
