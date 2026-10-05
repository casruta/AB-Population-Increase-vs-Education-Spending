# School finance refresh: 5 October 2026

Verified official HTTPS requests succeeded after the environment network configuration changed. The current operational-funding listing, financial-statements page, student-statistics page, Open Alberta catalogue API, and Statistics Canada CPI table/download were retrieved with normal TLS verification and the existing proxy. CBE's own website remained blocked; its official Alberta-hosted 2024-25 audited statement was accessible. A 403 from Python's default User-Agent on the individual-PDF downloader was resolved by using the same descriptive User-Agent as the successful official-source requests; no proxy, authentication, TLS or network-policy bypass was used.

## Exact source freshness

| Measure/source | Latest verified reference period | Publication or upload date and basis | Live refresh result | Admission/coverage |
|---|---|---|---|---|
| [Individual school-authority actual statements](https://open.alberta.ca/dataset/2f4b0aa9-b327-4bfa-86ba-783583eae157) | 2024-25 | Catalogue `issuedate` **2025-12-16**; individual resources created **2025-12-16 through 2026-04-08**; latest resource `last_modified` **2026-04-08T17:43:11.717866**; catalogue metadata modified **2026-04-21T15:50:48.507824** | Catalogue and all **83** official PDFs retrieved; PDF source hashes retained | New independently checked reconstructed level; not a government-published combined total or extension of continuous historical trend |
| [Combined actual statements](https://open.alberta.ca/dataset/2a9487b1-9d7a-47db-9f05-e633c315e447) and [summary reports](https://open.alberta.ca/dataset/a91a3309-414c-4632-8166-a847273ad73e) | 2023-24 | Catalogue `issuedate` **2025-07-08**; catalogue metadata modified **2026-04-20** | Live page links and exact catalogue searches still show these as newest combined/summary packages; no 2024-25 combined/summary package found | Northland draft caveat persists in original combined/summary records. Absence from checked listings is not proof that no unpublished/unindexed file exists |
| [2024-25 revised allocation schedule](https://www.alberta.ca/system/files/educ-budget-2025-projected-operational-funding-school-jurisdictions.pdf) | 2024-25 revised actual-year allocation, 2025-26 former projection | PDF printed **2025-09-16**, amounts as of **August 2025** | Live PDF hash exactly matches archived source | Use 2024-25 prior-year column, including in-year adjustments |
| [Current operational schedule](https://www.alberta.ca/system/files/ecc-projected-operational-funding-school-authorities.pdf) | 2025-26 revised allocation and 2026-27 projection | PDF printed **2026-05-13**, amounts as of **April 2026** | Live PDF hash exactly matches archived source; live [operational listing](https://www.alberta.ca/education-projected-operational-funding) still identifies this PDF | 2025-26 prior-year column includes in-year adjustments; 2026-27 lacks matched enrolment |
| [Authority enrolment](https://www.alberta.ca/student-population-statistics), [catalogue](https://open.alberta.ca/dataset/ccbcf0fb-615e-44a0-b7ec-681e2ea4e1e7) | 2024-25 published count; 2025-26 preliminary count | Both resource-created/upload timestamps **2026-02-05**; these are upload proxies, not independently established original release dates | Both live XLSX hashes exactly match archived sources; current catalogue still labels 2025-26 preliminary | 2024-25 September school-year headcount; official page labels 2025-26 **December 2025 student count**. Counts cover ECS through Grade 12 |
| [Statistics Canada 18-10-0004-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401), vector `v41692327` | **August 2026** | Table links [Daily release **2026-09-14**](https://www150.statcan.gc.ca/n1/daily-quotidien/260914/dq260914a-eng.htm); live CSV metadata ends **2026-08-01** | Live full-ZIP hash exactly matches archived manifest; **zero** changes in stored Alberta monthly observations | Both 2024-25 and 2025-26 school years contain 12 distinct September-August months; 2025 base remains 172.2 |

The independent freshness/source review is [independent-review.md](independent-review.md); response timestamps, HTTP status, SHA-256 and official URLs are in `*_network_results.json`. Large CPI and individual-statement downloads are under ignored `work/finance-downloads`; bounded extracts, five example PDFs, catalogue evidence and manifests are retained here.

## Newly verified 2024-25 actual level

Reconstruct actual expenses from each authority's 2024-25 audited Schedule 3, current-year **Total** column: row 34 total expenses, less rows 24-28 amortization (supported and unsupported tangible assets, supported and unsupported asset-retirement-obligation assets, and purchased intangibles). Each total independently equals that authority's Statement of Operations actual expense total. All 83 financial authority codes equal the 83 included enrolment authority codes. The 85 public/separate/francophone/charter enrolment rows include both Lloydminster boards; exclude codes 3170 and 4870 to reach **748,521** pupils and **83** authorities, including ECS.

| Reconstructed 2024-25 amount | Value |
|---|---:|
| Actual expenses, including amortization | $9,294,025,811 |
| Amortization removed | $507,171,459 |
| Actual expenses excluding amortization | **$8,786,854,352** |
| Matched headcount | **748,521** |
| Nominal actual expenses per student | **$11,738.96** |
| Actual expenses per student in 2025 dollars | **$11,814.42** |

Formula: `$8,786,854,352 / 748,521 × 172.2 / 171.1`. The school-year CPI mean of 171.1 uses September 2024 through August 2025. This total is our reconstruction, not an official published combined total. It is a separate later actual level and cannot establish recovery relative to the continuous 2016-17 through 2021-22 trend.

Independent source/hash/column/arithmetic checks of **all 83** authorities passed; see [rollup-review.md](rollup-review.md), [all extraction records](actual2024_25_extraction.json), [CSV](actual2024_25_extraction.csv) and [rollup](actual2024_25_rollup.json). Source rounding is retained: Grande Prairie Catholic, Red Deer public and WISE each have six program amounts summing $1 below their printed total; Grande Yellowhead unsupported amortization program amounts sum $1 above the printed total. Calculations use printed **Total** amounts, never repair source figures silently.

Valhalla's audit has a fundraising-completeness qualification. Its possible monetary effect is unknown; there is no basis to substitute zero or invent an adjustment. Four other audit emphasis notes concern Clearview's asset/ARO estimates, Footprints' PSAS transition and unaudited restated comparatives, Horizon's prior-year revenue-recognition correction, and Red Deer Catholic's restated comparatives. They do not modify those current-year opinions. Keyword mentions of going concern in standard auditor-responsibility paragraphs do **not** establish a going-concern problem. Review `audit_opinion_scan.json` together with the independent report before interpreting a keyword hit.

## Funding and headcount reconciliation

The existing real allocation result is unchanged: **4.643069635%**, or **4.6%**, from 2024-25 to 2025-26. Matched allocations are $7,716,613,874 and $8,361,644,972; matched counts are 748,521 and 754,880. Real values are $10,375.43 and $10,857.16 per student (see exact decimals in `reviewed_summary.json`). An illustrative extra $100 at the latter count costs **$75,488,000** annually; this is a scenario, not an estimate of optimal funding.

This matches annual sectors and each year's financial/enrolment authority coverage. It does **not** match an identical authority cohort: 2024 has 83 matched authorities and 2025 has 87. Four new 2025 charter authorities account for 765 pupils. The current funding PDF contains the corresponding four additional charter rows. A few dollars of source rounding separate summed displayed authority amounts from the printed Public Total; retain the published total, as the existing method does.

The final 2024 school-year count and preliminary December 2025 count differ in timing and certainty. They should not be described as two final September snapshots. No 2026-27 per-student amount is admitted without matched enrolment.

## Comparative investigation and reproduction

A research-only 79-authority common cohort was extracted from the **prior-year comparative columns of the same 2024-25 statements**. It excludes four new 2024 authorities and Mother Earth's former 2023 authority; see `comparative79_research.json`. All 79 prior numerators and comparative Statement of Operations totals were independently checked. Northland’s final 2023-24 individual audit, signed 23 July 2025, resolves the earlier draft-compilation concern; its final expense/amortization totals match exactly. Nine scanned audit reports were reviewed with OCR; Valhalla remains the only identified qualification. The scoped result is **−1.3222%** in inflation-adjusted **reported expenses excluding amortization per pupil**, covering 99.8823% of 2024-25 matched pupils. Accounting changes and a qualified audit limit interpretation as a stable-basis resource trend. This is not a province-wide total or historical-series extension. Footprints' unaudited comparatives are excluded. See [comparative review](comparative79_review.md) and [scoped reviewed summary](comparative79_reviewed_summary.json).

```bash
# No network; validate the original stored canonical funding/CPI/headcount inputs.
.venv/bin/python docs/research/refresh-finance/refresh.py --archived-only
# Replay stored verified official responses and 83 working PDFs.
.venv/bin/python docs/research/refresh-finance/refresh.py
# Re-fetch official evidence first; still never mutates canonical inputs/report.
.venv/bin/python docs/research/refresh-finance/refresh.py --download
```

Both offline modes were executed successfully. The actual-statement gate fails if any of the 83 source hashes differ from the independently reviewed snapshot. The allocation reconciliation fails if a live schedule hash differs from the archived schedule whose numeric inputs are being used, preventing silent reuse of stale amounts. Source changes require explicit review rather than automatic admission. TLS verification remains enabled throughout.
