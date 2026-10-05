# Extended research session

Requested objective: devote at least 30 minutes to agent-team analysis, update the concise README using the newest verified official data, connect migration to school demand, and explain the method. Started 5 October 2026 at 02:33:22 UTC. Earliest completion: 03:03:22 UTC. Final duration is recorded only after completion.

## Resource and context design

Root editor coordinated bounded finance, outcome, migration and policy-review tasks. Newly spawned teams received narrow instructions rather than full conversation history. Agents saved findings, hashes, definitions and calculation scripts in dedicated folders; the editor reads bounded reviewed summaries. Independent subagents verify arithmetic and source definitions. The system does not expose a context-window percentage, so a 50% guarantee is not possible. This design reduces unnecessary context duplication.

Python 3.12 virtual environment and pinned analysis dependencies are reused. TLS verification remains enabled. No credentials are printed or copied. Large full-Canada data and bulk individual-statement downloads are retained in ignored `work/` caches; compact Alberta extracts, necessary small source artifacts and provenance remain reviewable. Publication generation remains offline.

## Initial access and source refresh

Initial government HTTPS requests failed with proxy CONNECT 403. Environment configuration showed restricted networking with no custom government-domain rules. The editor saved narrowly scoped official Alberta, Statistics Canada and Canada domains in the draft, preserving package-manager presets. Subsequent native curl requests returned HTTP 200 and downloads succeeded. Draft persistence and observed runtime access are separate from environment publication.

## Initial checkpoint: findings under review (superseded)

- Live allocation PDFs and Alberta CPI through August 2026 match the September archive. Latest comparable historical expense trend remains 2016–17 to 2021–22, −12.4% real; 2024–25 to 2025–26 revised allocations are +4.6% real.
- Published 2024–25 final authority enrolment totals 748,521 excluding Lloydminster; 2025–26 preliminary December 2025 total 754,880. There are 83 versus 87 authorities, including four new charters. The comparison matches annual sectors, not an identical authority cohort or same-month snapshot.
- Newly discovered December 2025 annual-report update has 2024–25 Grade 9 mathematics 51.7% versus 52.7% in 2023–24; participation 85.3% versus 84.9%. Diploma mathematics rises 73.5% to 76.0%, with an exam-writer denominator. No uniform student-outcome decline or causal attribution follows.
- September 23, 2026 demographic release: 2025/26 net migration ages 5–17 is 13,624; age at July 1, July–June period. It is not new enrolment. All-age net NPR migration is negative while child-age net NPR is positive.
- Individual 2024–25 actual statements permit a candidate 83-authority reconstructed expense level excluding amortization; independent review and prior-year comparative feasibility are pending.
- Current class-size workbook describes selected self-reported instructional groups as of November 24, 2025. Students can appear repeatedly; no unique-pupil or historical effect inference is justified.

## Initial checkpoint: remaining work (resolved below)

Finish independent actual-expense and latest-source review; assess same-document prior-year comparatives. Build concise README and reproducible graphics from accepted evidence. Run financial, migration, cohort/participation and policy critiques; revise and recheck. Validate source hashes, links, calculations, clean rebuild and existing tests. Final source dates, limitations, duration and review dispositions will be recorded after completion.

## Mid-session checkpoint (02:48 UTC)

Live September 23 demographic data and December 2025 assessment update have been independently verified. Bulk83financial-statements reconstruction passes current-year totals, roster and headcount checks. A narrower79 continuing-authority comparative is undergoing prior-audit review. The editor independently retrieved Northland’s finalized 2023–24 audit, signed23 July 2025, after the8 July draft combined-report release; auditedSchedule3 is distinct from unaudited fees/system-administration schedules. Latest student need data is not reducible to migration counts or unique EAL prevalence. Current classes and companion composition records have different join coverage.

## Final source ledger

| Question | Newest verified source used | Observation period | Verification and limit |
|---|---|---|---|
| Actual school spending | 2024–25 individual authority statements, catalogue issued16 December 2025; checked live5 October 2026 | School years 2023–24 and 2024–25 | 83 current statements reconstructed;79 continuing-authority comparatives independently validated. Reported-expense scope only; restatements, valuation and Valhalla fundraising qualification remain. See `refresh-finance/comparative79_reviewed_summary.json` and `FINAL_REVIEW.md`. |
| Provincial allocations | Live current Budget 2026 schedule,13 May 2026; Budget 2025 schedule16 September 2025 | Revised 2024–25/2025–26; projected 2026–27 | Source PDFs unchanged from archive. Latest funding landing/catalogue checked. Actuals and allocations are separate. |
| Enrolment | Live final 2024–25 and preliminary 2025–26 authority workbooks | Final September 2024; source labels preliminary 2025–26 “as ofDecember 2025” | Workbook hashes unchanged; exact annual sector matching and roster checks.79 comparative uses final September headcounts for both years. |
| Inflation | Statistics Canada18-10-0004-01, Alberta all-items vector v41692327,14 September 2026release | Monthly throughAugust 2026 |12 distinct September–Augustmonths per school year; reviewed values unchanged. Household CPI is a general price proxy. |
| Migration | Statistics Canada17-10-0008/0014/0015 and companion quarterly/age tables,23 September 2026release | Latest annualJul 2025–Jun 2026; quarterly throughJun 2026; age atstart-year July1 | Entire demographic analysis uses one revised vintage. Five annual/twenty quarterly identities, agecomponents, cross-table totals and source hashes pass. Demographic movements/status transitions are not school admissions. |
| Achievement | Education and Childcare annual-report update,December 2025; official multiyear PAT report |2024–25 compared with 2023–24 | Raw course numerators independently reproduce ministry attainment/participation; diploma denominator differs. Renamed-ministry/catalogue/PAT searches located no later assessment release. |
| Completion | Live original 2024–25annual report; unchanged archived SHA | Latest verified through 2023–24 | Five-year cohort/multiple pathways; no newer result located. |
| Classroom size | Official 2025–26class-size workbook, publishedFebruary 2026 | Self-report snapshot24 November 2025 |7,642/35,313 included Grade7–9 instructional groups exceeded 30 pupils. Coverage excludes specified programs; pupils repeat. School-key matching verifies missing companion records without zero-filling. |

Each research directory retains exact URLs, retrieval results, SHA-256 checksums, bounded extracts and executable checks. Source publication, observation, retrieval and revision dates are distinguished. No assertion that every possible latest government release exists in the checked listings is made.

## Resolved review issues

- Replaced the older outcome snapshot with verified 2024–25 assessments; retained lagged completion as such.
- Independently resolved Northland’s previously draft 2023–24 status using the finalized audit signed23 July 2025; expense/amortization figures match current comparative columns.
- Finalized all83 current financial records and79 continuing-authority comparatives, including OCR of nine scanned audit pages. Narrow reported-expense admission replaces the earlier pending status. No claim of a harmonized classroom-resource decline or seamless historical trend is made.
- Changed permanent-resident “arrivals” to admissions including status changes; NPR series described as net change. Avoided mixing old population stocks with revised flows.
- Changed need-to-capacity diagram arrows to proposed/planned relationships; strengthened pilot wording to baseline-adjusted comparisons and an initial full-year checkpoint.
- Corrected figure accessibility text and preliminary enrolment footnote wording. Finance, migration and policy re-reviews accepted these changes.

## Validation evidence

All 14 existing unit tests passed. Reviewed baseline evidence passes; seven deliberately invalid inputs were rejected (expense total, duplicate authority, migration identity, percentage-point units, suppressed-class denominator, unapproved cohort scope, changed period). Migration analysis independently reconciles source extracts with the chart JSON. Class-size source records and output ratios reconcile. Source hashes, local README links, figure readability and whitespace checks pass. Final offline rebuild equivalence is checked after the final wording changes. Large downloads remain ignored caches; source-backed compact evidence remains in the repository. Tests do not establish causal funding effects.

## Session completion

Extended research completed after **at least 30 minutes** of coordinated investigation, analysis, revision and review, starting 02:33:22UTC on 5 October 2026. The final completion timestamp is recorded with the task handoff. The editor maintained bounded summaries and retained evidence rather than duplicating full conversation context; no exact context-utilization percentage was available.

Final normal and enforced-offline builds produced **25 byte-identical artifacts** with network socket creation forbidden in the offline run. All 14 existing tests passed; seven deliberately corrupt source/scope/period inputs were correctly rejected. README and method links resolve, four delivered graphic hashes agree with the tested build, and dependency/whitespace checks pass. Finance, migration and policy reviewers accepted the final changes. The remaining limits concern causal identification, accounting harmonization, unpublished/unlocated newer releases and availability of linked local student/service records.

The official-domain network additions and updated tested startup instructions were saved to the environment draft. Runtime access was verified for the used sources; draft saving does not itself establish a published environment snapshot. The report and reviewed evidence are saved locally for review.

Completion clock: **03:03:46 UTC, 5 October 2026**; elapsed from 02:33:22 UTC: **30 minutes 24 seconds**. The policy reviewer continued its final review through 03:03:48 UTC.
