# Final finance review — 5 October 2026

Reviewed the updated `README.md`, the finance loading/calculation and chart construction in `extended_report.py`, and the exported `plots/funding_and_actuals.png` at ordinary reading size after the figure was rebuilt.

**Accepted with wording/spacing polish requested.** The report correctly admits the 79-authority comparison only as inflation-adjusted **reported expenses excluding amortization per pupil**. It identifies accounting changes and Valhalla's qualified fundraising audit, distinguishes the separately reconstructed 83-authority 2024-25 level, and keeps provincial allocations apart from all-source actual authority expenses. It does not join these results to the 2016-22 continuous historical series or claim that spending caused outcomes.

Checked the plotted and written rounded amounts against independently reviewed records:

| Scope | Prior real dollars/pupil | Current real dollars/pupil | Change |
|---|---:|---:|---:|
| 79 continuing authorities, 2023-24 → 2024-25 | $11,972.50 | $11,814.20 | −1.3222%, shown −1.3% |
| Revised annual-sector allocations, 2024-25 → 2025-26 | $10,375.43 | $10,857.16 | +4.6431%, shown +4.6% |
| Separate reconstructed 83-authority 2024-25 actual level | — | $11,814.42 | No joined historical change |

Cohort headcounts are 726,604 and 747,640; the current cohort covers 99.8823% of the full matched 748,521 count. Allocation denominators are 748,521 and preliminary 754,880. The 2026-27 matched allocation of $8,896,073,124 is projected, with no matched headcount; no per-pupil figure was manufactured.

The side-by-side bar panels use a zero baseline and common scale. Titles, endpoints and audit/accounting caveats are legible. The stand-alone 83-authority level is explicitly labelled a reconstruction; the allocation panel names its different measure. Rounded current per-pupil values happen to be identical ($11,814) for the 79 and 83 scopes, but their different scope is still stated.

Requested fixes before final acceptance: update the image alt text, which still describes historical spending instead of the new 79-authority comparison; restore missing spaces in README and the figure's enrolment footnote. Recommended headcount wording echoes the official footnote: the preliminary 2025-26 count is labelled “as of December 2025 student count.” The same official page defines an Alberta student by September 30 registration, so the December label should not be expanded into a stronger claim about a separate census date.

Source review was exhaustive for the financial numerator: all 83 current expenses/amortization columns and Statement of Operations totals checked independently; all 79 comparative numerators checked independently; nine image-only auditor reports reviewed using OCR and saved bounded excerpts. Northland's final 2023-24 audit signed 23 July 2025 and its current-year totals match the later comparative exactly. Source rounding and the qualified audit remain disclosed, with no invented financial adjustments.

The stored-response replay and `--archived-only` refresh path both passed after the hash review gate and enrolment schema-header handling were added. The pipeline fails if any of the 83 independently reviewed statement hashes or either allocation schedule changes, prompting another review before revised results are admitted. No canonical financial inputs were modified by this research subtask.

## Re-review after fixes, 02:58 UTC

Re-read the updated README and figure code, then inspected the rebuilt PNG again. The alt text now describes the 79-authority comparison; missing spaces are restored; the enrolment footnote accurately says the count remains preliminary and quotes the source's “as of December 2025” label. The longer footnote remains inside the image and readable. **Final finance review accepted within the reported-expenses-only scope.** No remaining finance wording, arithmetic, coverage or chart repair is requested.
