# Evidence tables

The maintained build reads local, source-backed CSVs and JSON. Downloads and PDF extraction are preparation steps; the publication build never calls the network.

## Tables

- `data/spending.csv`: observation_id, series_id, year, period, amount_m, status, budget_basis, coverage_id, segment, source_id, locator, selected. Amounts are nominal CAD millions; status is actual, budget, or forecast. Only original budgets qualify for delivery comparisons. Explicitly selected rows determine each published series/year/status.
- `data/enrolment.csv`: denominator_id, year, period, learners, unit, status, coverage_id, source_id, locator, segment, eligible, note. Units are headcount, FTE, or FLE. Preliminary and final describe enrolment status, not financial status. Ineligible reported counts remain traceable but cannot produce a ratio. Enrolment reporting changes also break comparability.
- `data/cpi.csv`: year, cpi, source_id. Alberta All-items annual average, 2002=100. Constant-dollar calculations use 2012 as their price base and the spending period's starting calendar year.
- `data/population.csv`: year, population, reference_date, source_id. One release vintage; January 1 estimates provide context only.
- `data/series.json`: an object keyed by series ID. Each definition contains sector (`k12` or `postsec`), measure (`grants` or `expenses`), label, coverage_ids (allowed boundaries), denominator_id, learner_unit, period_basis, match_note, limitation, gap_reason, target_start, and target_end. Optional year_notes explain observation-specific limitations. A missing approved denominator produces an explicit gap, never a substitute provincial-population ratio.
- `data/sources.json`: an object keyed by source ID. Each source contains title, URL, release/retrieval date, and a raw_files list of repository-local path and SHA-256 pairs, plus extraction/filter notes. Unknown release precision is stated rather than fabricated.

## Selection and comparisons

Grants and institutional operating expenses remain different measures. Ministry totals cannot substitute for either without a documented boundary reconciliation. Series metadata determines coverage; observations record the comparability segment. Comparisons cannot cross segments or missing years silently.

One approved enrolment series is matched to each financial series. The definition records why its institution coverage and school/academic year are suitable. Headcounts and full-load/full-time equivalents are never relabelled as one another. Different sector scales do not imply equivalent instructional costs.

The computed comparability segment combines financial and enrolment segments. A boundary change in either breaks the plotted line and prevents a cross-boundary headline growth calculation.

Financial and enrolment observations must have identical coverage_id in a ratio. For example, the 2022–23 K–12 rollup and its denominator both exclude Valhalla; this is a separately named boundary, not an implicit exception to validation.

Only actuals feed resource-per-learner charts. Budget delivery uses an actual and an original budget with identical series, period, year, and segment; it uses nominal totals without an enrolment denominator. Forecasts and unselected source vintages remain traceable but never replace actuals.

Unknown data remain absent with a reason. Zero is a real observation. Invalid numbers, duplicate selected rows, missing provenance, and contradictory definitions fail validation rather than being silently repaired.
