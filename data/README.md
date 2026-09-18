# Evidence inventory

The publication reads four CSV tables and two JSON metadata files in this folder. The [data contract](../docs/DATA_CONTRACT.md) defines their fields and eligibility rules. Missing financial observations are absent from the inputs and become explicit gaps in generated coverage tables; they are never zero spending.

| Location | Purpose |
|---|---|
| `spending.csv` | Actual financial observations and retained source vintages; `selected` is an explicit admission decision |
| `enrolment.csv` | Matched headcounts and approved-program FLE, including ineligible reported counts and their reasons |
| `cpi.csv` | Verified Alberta annual All-items CPI, 2012–2025 |
| `population.csv` | January 1 provincial population, 2012–2026, one release vintage; context only |
| `series.json` | Measure definitions, accounting boundaries, coverage IDs and limitations |
| `sources.json` | Official source URLs, date precision, original local files and SHA-256 checksums |
| `raw/` | Preserved official source snapshots and coverage metadata |
| `staging/` | Source extracts, accounting components, exact workbook cells, admission notes and preparation scripts |

## Refreshing evidence

The supported publication command is `python generate_all_charts.py` at the repository root. It needs no network, PDF reader or spreadsheet engine and does not change source inputs.

Source preparation is separate. To assemble already reviewed staging tables, run `python data/prepare_data.py`. The sector preparation scripts are audit aids, not additional supported publication commands; they require `openpyxl` and `pypdf` when extracting original XLSX/PDF snapshots. Preserve the original download, record its official URL and checksum, then review the measure, source vintage, status, learner coverage and comparability before selecting a new observation. Do not select a row just because it comes from the newest report.

For a financial refresh, reconcile all additions and deductions in the component tables. Confirm that the learner roster covers the same institutions. Source changes can require a new segment, an ineligible denominator, or a new measure rather than an extension of the existing line. An independent reviewer must check the source observation and the canonical table before publication.

Unknown release dates are recorded explicitly. K–12 catalogue dates identify portal publication/upload dates, not necessarily the original historical release. Retrieval records span September 17 in Edmonton and September 18 UTC; this does not imply a later local research date.
