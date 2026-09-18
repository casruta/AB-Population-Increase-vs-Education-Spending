# Independent code and data review

Reviewed the canonical integration on 18 September 2026. Reviewer did not author the calculation module, data assembly, source extraction or presentation. This review covers `analysis.py`, `data/prepare_data.py`, canonical metadata, calculation tests and the integrated evidence. Presentation review is a separate gate.

## Result

Approved: no calculation or canonical-integration blocker found. All eight tests pass after the requested regression addition. The selected data contain 37 actual financial observations, 26 eligible per-learner results, 56 coverage rows and zero admitted original-budget comparisons.

The implementation validates source hashes, selected-observation uniqueness, explicit financial status, numeric values, CPI availability and duplicate JSON identifiers. Only selected actuals enter resource ratios. Period labels, coverage identifiers, learner units and eligibility must match before division. Both financial and enrolment segments survive in the computed comparison key. Delivery requires an original budget and actual with identical series, year, period, institutional coverage and financial segment; forecasts and revised budgets cannot silently substitute.

## Independent calculations

- Read every canonical CPI observation against the archived Statistics Canada ZIP, filtering Alberta, All-items and `2002=100`; all agree, including 2023 = 164.1 and 2024 = 168.9.
- Recomputed all 22 K–12 financial observations with exact decimal arithmetic from 74 staged accounting components. All agree with canonical amounts. This includes the signed unspent-capital adjustment, interschool exclusion and amortization subtraction.
- Summed all admitted school-authority components for each of the ten enrolment years; every canonical K–12 denominator agrees. The 2022 financial and enrolment records share the explicit Valhalla-exclusion boundary.
- Recomputed six university expense components after tangible/intangible amortization and separately identified disposal losses. The totals are CAD 502.428 million (2023–24) and CAD 540.755 million (2024–25), matching the canonical data.
- Checked the subset's matched FLE values, 26,056.497 and 27,463.219, and independently calculated constant-2012-dollar amounts per FLE: $14,934.640555 and $14,817.161163. These ratios describe only MacEwan, Mount Royal and Alberta University of the Arts.
- Verified the 2024–25 public-20 operating-grant amount is CAD 2,085.226 million. Its 2023–24 and 2024–25 ratios remain missing because their broader denominators are ineligible, despite the three-university expense ratios being eligible.
- Checked every admitted ratio's financial/learner coverage, period and eligibility. The composite university source resolves to exactly the three individually registered original PDFs; the normal build checks all their hashes. The separate evidence review independently inspects the original expense pages and workbook cells.

## Fix and independent verification

The original test suite pinned K–12 and CPI samples but did not pin the newly admitted university subset and the two withheld public-20 ratios. Requested the implementation author add those canonical regression assertions, including an empty delivery table. The author added `test_postsec_subset_is_distinct_from_system_grants`. This reviewer inspected its assertions and independently reran the complete suite: eight tests passed. The request is closed; the reviewer did not author the fix.

The completed renderer source was also inspected: it sorts dated observations and connects only runs of at least three consecutive years with the same combined financial/enrolment segment. It retains isolated points and renders a gap when original-budget pairs are absent. Tables, summary values, chart inputs and README figures use one validated analysis result. Visual inspection and a clean offline publication rebuild are separate release checks recorded in the validation report.

## Interpretation constraints

Financial and academic periods align approximately by starting-year label, not identical months. K–12 recognized provincial revenue is not cash grants or total provincial support. The university expense subset excludes an additional identified disposal loss and is not the whole post-secondary sector. Earlier public-20 ratios use reported FLE with documented limitations; provisional financial segments do not certify a harmonized historical all-program trend. No original-budget comparison is supported by the admitted evidence. These limitations must remain visible in the README and figures.
