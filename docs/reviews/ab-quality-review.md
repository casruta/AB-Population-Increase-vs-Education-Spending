# Publication A/B quality review

Reviewed 5 October 2026. A is GitHub commit `552c45fb95ba006cce35544e138325f75352e4ab`; B is the revised report and retained evidence in this release. The comparison uses a controlled editorial rubric, independent visual review and reproducibility checks. It is not a randomized reader experiment; no measured reader-preference or comprehension improvement is claimed.

## Editorial comparison

Scores are qualitative judgments out of five, not empirical effect sizes.

| Criterion | A | Revised B | Reason |
|---|---:|---:|---|
| Evidence freshness | 3 | 5 | Current verified finance, outcomes and migration vintages are identified. |
| Question coverage | 2 | 4 | Adds school-age demand, class-size records and separate outcome measures. |
| Financial scope | 4 | 4 | Canadian dollars and direct Methods navigation preserve broader finance context. |
| Outcomes and migration interpretation | 1 | 5 | Denominators, participation, status changes and causal limitations are explicit. |
| Actionability | 3 | 5 | Recommendations identify observable capacity and support needs. |
| Concision | 4 | 3 | B is 810 words versus A's 789; greater coverage costs length. |
| Traceability | 4 | 5 | Direct Methods navigation and retained audit/vintage evidence. |
| Visual accessibility | 4 | 4 | Larger wrapped footnotes and accepted PNG layouts; no mobile or assistive-user study. |

The independent reviewer required two corrections: the 4.6% allocation increase must explicitly mean **per pupil after inflation**, and the README must restore currency and broader financial-context navigation. Both corrections were verified. Enlarged figure notes initially overlapped; the final layout removes that overlap. Final visual inspection accepted both figures without clipping or label collisions. No remaining editorial publication blocker was identified.

## Release gates

Both versions are tested using the same pinned Python 3.12 environment in separate exports of their Git trees. Candidate validation uses only tracked files, without ignored research caches. The gates are: the existing 14 calculation/evidence tests; seven deliberately corrupted total, duplicate, identity, unit, denominator, scope and period cases rejected by the reviewed-evidence validator; offline generation; migration source-checksum and stock-flow checks; and equality of generated README and new figure bytes to the staged publication. A generates 19 publication artifacts and B generates 25; artifact count itself is not evidence of quality.

The retained research sources have byte-preserving Git attributes so CRLF conversion cannot invalidate recorded hashes. Generated charts and the current README must reproduce from the candidate export before committing. Final results: A and B each passed all 14 unit tests. B rejected all seven invalid-evidence cases, passed the migration source/identity checks and generated all 25 artifacts with network sockets disabled. Its README and four new figures exactly matched the staged bytes. All 18 checksummed migration extracts/metadata retained identical Git object hashes with `core.autocrlf=true`; all 210 staged files matched working-tree bytes before this final review-note update.

The dated September PDF remains a historical snapshot; the README and current Methods describe the refreshed evidence. Bulk PDF download caches and the local virtual environment are intentionally excluded from the release.
