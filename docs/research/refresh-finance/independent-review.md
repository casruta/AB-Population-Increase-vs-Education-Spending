# Independent source freshness review

Reviewed 2026-10-05 using the saved official responses in `responses/`; no canonical data or application changes. Conclusions describe what these snapshots establish, rather than proving that no unindexed resource exists elsewhere.

## Financial actuals

- `exact_search_0` returns one matching package: **2024-2025 school authorities audited financial statements** (`2828632-2024-2025`), with 83 authority PDF resources. `individual2024_metadata` independently agrees. Package publication metadata was created 2025-12-16, its declared `date_modified` is 2026-01-19, and catalog `metadata_modified` is 2026-04-21T15:50:48.507824. The newest resource `last_modified` is 2026-04-08T17:43:11.717866 (Sturgeon School Division). Catalog metadata changes are distinct from fiscal coverage and document release dates.
- `exact_search_2` contains 73 results. Its newest individual authority year is 2024-25, while its newest **combined financial statements** and **summary reports** are 2023-24, both with declared modification date 2025-07-08. `live_combined_metadata` confirms 2023-24 and nine combined resources, with catalog metadata modified 2026-04-20.
- The official `authority_statements.txt` explicitly defines combined statements as a provincial roll-up compiled from individual statements and schedules (lines 872-873); it lists 2023/2024 as newest combined and summary year and 2024/2025 as newest individual authority year (lines 874-889).

Therefore “no 2024-25 actuals are available” would be false. **2024-25 individual audited actuals are available; the newest evidenced province-wide published combined/summary actuals remain 2023-24.** Updating the provincial series from individual statements would require a separate aggregation and reconciliation exercise.

## Enrolment timing

The official `student_statistics.txt` defines ordinary registration timing as September 30 (line 866), but explicitly marks **2025/2026*** with “Enrolment as of December 2025 student count” (lines 877, 1036). Its published 2025-26 total is 835,089. The school/authority data section explicitly calls 2025-26 **preliminary** (line 1067). Keep that year preliminary and preserve its December count footnote; do not describe it as a final ordinary September snapshot. These timing labels must accompany comparisons with prior years.

## Allocation PDFs

Saved Budget 2025 PDF: 158,581 bytes; SHA-256 `b32cac6feeccabfff0edbf0b3fb5075419191600720640ac32084694fa476be3`.

Saved Budget 2026 PDF: 188,388 bytes; SHA-256 `e68e9d5c5bb2433266ec51e53aa840ddb4766919aa6250adbc69dc00c4a909e7`.

They differ in both bytes and extracted content. Budget 2025 is “As of August 2025,” footer September 16, 2025; its 2025/26 column is expressly an estimate and Public Total is $8,079,870,097. Budget 2026 is “As of April 2026,” footer May 13, 2026; it reports 2025/26 including in-year adjustments ($8,406,884,442) and projected 2026/27 ($8,942,970,333). The newer 2025/26 total exceeds the earlier estimate by $327,014,345. These are operational funding allocations/projections, not audited expense actuals; neither is a substitute for combined financial statement expenditure totals.

Extracted text SHA-256: Budget 2025 `5e573fcd31649a28a3861f0ae6d1cea7511612c7ebf1ca62363bdc55c51a8957`; Budget 2026 `604165da1162ab0493e007af5b2953dfaff6677c2a929d28624c86e6b32142eb`.

## Independent 2024-25 extraction check

Use Schedule 3 (Schedule of Program Operations), row (34) TOTAL EXPENSES, **2025 TOTAL** column. Subtract current-year totals for rows (24)-(28): supported TCA, unsupported TCA, supported ARO TCA, unsupported ARO TCA, purchased intangibles. Keep accretion (29) distinct; it is not amortization. Cross-check row (34) against Statement of Operations actual total expenses. Parse actual current-year column rather than budget or 2024 comparator. Missing blank cells mean positional text-token counting alone is unsafe, especially row (28), which may have no prior-year comparator. Confirm column positions/header and reconcile component totals.

| Sample | Expenses | Rows 24–28 amortization | Expenses excluding amortization | Audit opinion |
|---|---:|---:|---:|---|
| Alberta Classical Academy (0) | 20,298,390 | 1,338,346 | 18,960,044 | Unqualified |
| Calgary Board of Education (11) | 1,643,348,000 | 95,785,000 | 1,547,563,000 | Unqualified |
| Edmonton School Division (21) | 1,350,130,710 | 64,278,167 | 1,285,852,543 | Unqualified |
| Northland (55) | 65,931,413 | 5,142,207 | 60,789,206 | Unqualified |
| Valhalla (76) | 1,605,400 | 59,928 | 1,545,472 | Qualified |

CBE amortization components: 61,722,000 + 31,244,000 + 0 + 2,819,000 + 0. Edmonton: 48,669,994 + 13,898,387 + 0 + 1,709,786 + 0. Northland: 3,778,246 + 1,360,001 + 0 + 3,960 + 0. Valhalla: 24,080 + 35,848 + 0 + 0 + 0. Valhalla’s qualification concerns completeness of fundraising revenues and resulting effects on reported financial position/results; preserve that limitation rather than calling the entire collection unqualified.

Locations are the six numbered schedule rows in each `actual_example_N.txt`; auditor reports appear near the start of each file. The Edmonton TCA note independently prints amortization 64,278,166, one dollar below the Schedule 3 component sum 64,278,167. Preserve the schedule values and flag this rounding/reconciliation difference. CBE values are printed in dollar amounts rounded to thousands; retain source precision. The extraction should carry PDF resource URL/hash, legal authority name/code, current fiscal year, expense/amortization components, page or schedule locator, audit qualification, and reconciliation status for every authority.
