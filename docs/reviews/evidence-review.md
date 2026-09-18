# Independent evidence admission review

Status at this interim handoff: shared inputs and staged K–12 definitions/arithmetic approved; post-secondary grant classification, 20-institution coverage and denominator eligibility rules approved. This is not approval of the final canonical dataset or application. Institutional post-secondary expense remains outside this review. This review sampled original sources independently, rather than relying only on the extraction scripts. It does not certify the entire application or every source cell.

## Shared context and price inputs

Approved: all 14 Alberta All-items annual CPI observations (2012–2025) and all 15 Alberta January 1 population observations (2012–2026). Independently re-read the full archived Statistics Canada ZIP CSVs, applied the documented filters, compared every value and year to staging, and verified every raw-file SHA-256 in the shared manifest. CPI endpoints are 127.1 and 172.2; population endpoints are 3,822,425 and 5,048,151. No 2026 CPI is admitted. Population remains contextual and is not a learner denominator.

Original metadata states: “Population estimates: Q1 = January 1; Q2 = April 1; Q3 = July 1; Q4 = October 1.” The population archive also identifies recent estimates as preliminary; the publication must not call the entire historical series final. Release dates were not independently established from these metadata files.

## K–12 financial definitions and boundary

The proposed non-amortization expense measure is defensible as reported total expenses minus tangible-capital-asset amortization. It is not cash spending and does not exclude all maintenance or capital-related activity charged to expense. Use a precise label and preserve both calculation components.

The proposed grant measure is defensible only as recognized Government of Alberta grant revenue excluding identified capital-related revenue recognition, not government cash grants paid during the year. For 2018 onward this should remove both spent deferred capital contribution amortization and direct grant-revenue recognition from unspent deferred capital contributions. In the original 2023–2024 deferred-contributions PDF, page 1, the GoA components independently read were SDCC 71,594,701 + 301,140,808 and direct UDCC recognition 827,050 + 4,945,019 dollars. Deducting only SDCC would leave the latter capital-origin recognition included.

Original 2022–2023 catalogue metadata excludes Valhalla because its statements were not finalized. Original enrolment workbook rows independently checked: Lloydminster codes 3170 and 4870 report 3,060 and 2,568 learners, and Valhalla code 0224 reports 81. For 2023–2024 the same rows report 3,128, 2,625, and 64 respectively. The reconciled numerator boundary must justify excluding both Lloydminster authorities every year; this exclusion was independently confirmed for 2023–2024 by reading the original expense-by-program roster: its 80 authority codes exactly match the 80 admitted enrolment codes, with no unmatched codes. Both Lloydminster codes are absent and Valhalla is present. Earlier years use the same Alberta-reporting boundary; a year-by-year roster audit was not performed. Exclude Valhalla only in 2022–2023, then create another boundary break when it returns.

The 2023–2024 catalogue explicitly includes draft Northlands reporting. Actual is the correct financial category, but the source assurance is provisional in part and must be stated. Do not describe this combined total as wholly final audited evidence.

A column headed Budget does not establish original budget status. No budget-delivery result is admitted without further evidence identifying the original plan on the same boundary and accounting basis. Early grants without a verified GoA-specific capital split remain unavailable; no aggregate-capital proxy is approved.

Independently verified all 50 staged K–12 source hashes, every staged spending calculation against component rows, and all ten enrolment year totals directly from the original workbooks using their actual header rows. The 2023–2024 cash-flow PDF confirms amortization of 492,100,123 dollars. Its program-operations PDF confirms 8,617,415 dollars of other-school-authority revenue, which must also be deducted from the provincial-grant proxy to avoid misclassifying inter-school revenue. The resulting non-amortization expense is 8,463.238670 million; the grant proxy is 7,663.506403 million. With the stated limitations, staged K–12 definitions and arithmetic are admitted.

## Post-secondary coverage and reported FLE

The institutional boundary of 20 public institutions excluding Banff matches the 20 public institution rows in the FLE workbook, after excluding independent academic institutions and every subtotal. Independently summed all ten source years using exact decimal arithmetic; each year has 20 institutions and matches staging exactly. All 14 staged post-secondary source hashes also passed.

The 2024–2025 original annual-report table was visually reviewed at printed page 102 (PDF page 104). It separately labels operating grants and infrastructure grants and includes funding from all department programs. The public total less Banff is 2,101.387 − 16.161 = 2,085.226 million dollars. This is departmental operating-grant expenditure, not all-GoA institutional revenue, an instruction-only grant, or institutional operating expense. The supplemental table is explicitly unaudited; that does not change actual financial status.

Annual FLE is approved-program course load, not headcount. Whole-institution grants/expenses per reported approved-program FLE may be described as a resource-intensity indicator, with explicit activity-scope and period limitations. They cannot be described as the cost of instruction or funding attached to each student. The financial year and institutional academic reporting year overlap but are not identical; this is a labelled approximation, not exact temporal reconciliation.

Withhold the 2023–2024 ratio: Reporting Changes!C16 says, “Graduate level thesis FLE at the University of Alberta continues to be over reported in the 2023-24 submission.” A known erroneous denominator is not repaired by placing it in a separate segment. Retain its source value as reported context. The word continues leaves the affected earlier interval uncertain; earlier ratios must retain a reported-FLE limitation and cannot be certified error-free.

Withhold the 2024–2025 ratio: Athabasca includes January 2024 through April 2025 and about 3,200 additional FLE. NorQuest also repeats a spring session, and University of Alberta thesis reporting changes. Subtracting a rounded 3,200 is not an approved correction. Both 2023 and 2024 are now flagged ineligible in staging.

Earlier reported ratios may support dated levels and narrowly segmented changes, not a continuous trend. Required breaks include Olds 2015 cleanup; Alberta 2017 thesis change; Lethbridge 2018 program change; system 2019 active-learner change; 2021 institutional calendar changes; and 2022 Lakeland/Northwestern timing changes. The 2021 source explicitly describes consistent twelve-month reporting; its repeated spring session breaks year-on-year comparability but does not itself establish a sixteen-month level. In 2023 Lakeland and Northwestern return from four to three reported sessions, another reason not to bridge these years. Institutional renames/reclassifications alone do not change the 20-institution aggregate.

## Historical open gates at the first interim review (subsequently resolved below)

1. Replace the post-secondary generic newest-vintage selection with an explicit reviewed source map and document why each selected comparative is suitable. Unknown department-boundary reconciliation must not be presented as a comparable financial segment.
2. Replace guessed report publication months with verified dates or explicit unknown/precision metadata. The staging script currently assumes June while noting a possible July exception.
3. K–12 source, arithmetic, denominator filtering and 2023–2024 exact roster checks are complete; this gate is closed. Source caveats and comparability breaks must remain visible.
4. Enforce denominator eligibility in the publication build; publishing the known 2023/2024 FLE defects as ordinary ratios is a blocker.
5. Preserve all actual/budget/forecast distinctions. Institutional post-secondary expense and any original-budget gaps must remain explicit if no matching evidence is admitted.
6. Never connect gaps or different financial/denominator segments. Financial-series and denominator breaks should combine for ratios, without inventing financial breaks solely because an unrelated revenue classification changed.


## Interim handoff update

The post-secondary specialist subsequently replaced generic latest-vintage selection with a fixed, documented source map in `COVERAGE.md`, including numerical restatement differences and the 2019 source exception. That closes the generic-selection blocker for staged annual levels. The same notes explicitly limit financial segments to provisional boundaries and do not certify a harmonized historical all-program series; publication must preserve that limitation. A financial trend must not be inferred merely because the same provisional segment label is present.

The final canonical import, source registry, output labels and post-secondary institutional-expense candidate still require a follow-up gate. This review is limited to the inspected staging state and definitions. No original budget comparison has been admitted.


The source-date blocker is also resolved at staging: report dates now use dated catalogue metadata where available, 2012 is recorded as July 1, 2013/2014 remain unknown, and the guessed universal June-month rule is removed. The K–12 specialist additionally reports exact code-equality checks for every 2016–2023 financial roster, stored in `roster_checks.json`; this reviewer directly repeated the 2023 check and all workbook totals, but did not repeat every older roster comparison.


## Second admission gate: three-university institutional expense subset

Admitted after independent review: 2023–2024 and 2024–2025 institutional expenses excluding amortization and separately identified capital disposal losses for MacEwan University, Mount Royal University and Alberta University of the Arts only. This narrower population must remain visible in every table/chart title or immediately adjacent coverage label. It is not a province-wide post-secondary expense estimate, the same definition as the K–12 amortization-only exclusion, or the provincial fiscal-plan operating-expense measure.

Independently viewed the rendered original expense-by-object schedules at MacEwan PDF 88/printed 82, MRU PDF 72/statement printed 31 and AUArts PDF 52/statement printed 24; checked all three archived PDF hashes; recomputed all six institutional amounts and both totals; and read all six original LERS cells directly. The synthetic aggregate source identifier must resolve to all three parent PDFs and these component locators in the canonical manifest.

The selected 2023–2024 amount is CAD 502.428 million and 2024–2025 is CAD 540.755 million. MacEwan's 2023 comparative explicitly includes a CAD 1.532 million capital-asset disposal loss in total expenses; removing it is supported by the narrowly named measure. MRU amortization correctly includes tangible and purchased-intangible amounts: 15.724 million in 2023–2024 and 16.490 million in 2024–2025. Remaining interest, pension, inventory consumption, ancillary services, research and scholarship expenses are not removed and must not be described as instruction-only spending.

The matched FLE values are 26,056.497 (cells E276:E278) and 27,463.219 (E308:E310), comprising precisely the same three institutions. The current workbook has no 2023 or 2024 reporting-change entry affecting these institutions. The larger system's 2023 UAlberta error and 2024 Athabasca/NorQuest disruptions do not apply to this subset. These ratios are therefore eligible even though the broader 20-institution ratios for the same years remain ineligible.

All three numerator periods contain twelve months, although MacEwan/MRU close March 31 and AUArts closes June 30. Matching by academic/fiscal start-year label is an explicit approximation, not identical calendar coverage. The stable institution pair and same-source comparative columns support two dated levels and, if desired, a carefully labelled dated change. Two observations do not establish a trend. Budgets remain candidates only; no original-budget comparison is admitted. The final canonical import and its downstream enforcement still require review.


## Final canonical integration gate

Independently checked `data/prepare_data.py` and canonical spending, enrolment, series and source files against admitted staging. All 47 financial rows preserve their observation identifiers, values, periods, statuses, selection flags, segments and locators. The two subset expense rows are explicitly renamed to the maintained expense-series identifier; coverage remains the three universities. All 22 denominator rows preserve values, units, statuses, source locators and applicable eligibility/segment flags. Broader post-secondary 2023/2024 ratios remain ineligible, while the unaffected three-university rows remain eligible.

All 78 canonical source records resolve, and every archived raw-file SHA-256 passes. The composite expense source contains all three original PDF hashes and points to their individual source/locator tables. Both shared CSVs are byte-identical to their reviewed staging files. Every financial coverage identifier is allowed by its series metadata, and every available selected numerator/denominator join has identical coverage, including the 2022 Valhalla exclusion. The preparation script imports reviewed selections without introducing a newest-row selection rule or substituting forecasts/budgets.

Canonical quantitative evidence is approved within the previously stated boundaries. A final metadata wording fix was requested: the post-secondary grant limitation must explicitly retain annual-level-only admission, unresolved department-program harmonization and the uncertain earlier duration of thesis-FLE errors. These restrictions should travel with `series.json`, not only the detailed staging notes. The three-university missing-evidence description should consistently name the disposal-loss exclusion. Application behavior is being reviewed separately; this evidence gate does not replace that review.


## Closed evidence verdict

The requested final metadata fixes are verified in `data/series.json`: post-secondary grants explicitly retain annual-reported-level-only admission, unresolved department-program boundaries and possible earlier thesis-FLE error; the three-university gap description now includes the identified capital-disposal-loss exclusion. These close the remaining wording requirements from this review. Earlier open-gate sections above record the review history and are superseded by the later gate closures.

Final verdict: the canonical evidence is admitted for the stated measures, institution boundaries, periods and eligibility rules. No unresolved evidence-review blocker remains. The latest preparation-script cleanup introduced no new evidence; the root independently reports reproduction of 21 staged CSV/JSON files, unchanged after newline normalization, followed by canonical reassembly. Prior quantitative and provenance checks therefore remain applicable. Application correctness and publication behavior are covered by their separate implementation review, not certified by this evidence verdict.
