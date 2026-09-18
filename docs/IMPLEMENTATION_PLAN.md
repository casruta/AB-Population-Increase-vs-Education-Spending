# Implementation and review plan

## Team and ownership

| Stage | Agent | Purpose and ownership |
|---|---|---|
| Audit | Two Luna scanners | Reuse the repository audit; inventory code, inputs and dependencies; organize shared CPI and population evidence |
| Source reconciliation | Two Astra sector specialists | Own separate K–12 and post-secondary source extracts, accounting bridges and enrolment matches |
| Admission | Independent Astra evidence reviewer | Check original observations and approve definitions without editing specialist data |
| Calculation | Sol implementer | Own `analysis.py`, tests, dependency files and validation workflow |
| Presentation | Separate Sol implementer | Own the build entry point, chart layer and generated README, tables and figures |
| Integration | Coordinating lead | Own canonical assembly, metadata, methods, archive and final packaging |
| Final challenge | Independent reviewers | Check code/data and policy/visual interpretation; assign defects to an author and have a different reviewer verify fixes |

No more than three workers run concurrently. Files have one editor at a time. The lead integrates changes and preserves review records.

## Revisions after source review

1. Replace the original ministry totals and population ratios with separate financial measures and matched learner denominators.
2. Use verified annual Alberta CPI; retain originals in the archive and document corrections.
3. Publish K–12 recognized provincial revenue and expenses with exact capital, transfer and authority exclusions. Preserve the temporary Valhalla break and draft Northland caveat.
4. Publish department grants for 20 public post-secondary institutions. Withhold two recent per-FLE ratios where source reporting errors prevent a defensible comparison.
5. Narrow post-secondary institutional expenses to three undergraduate universities whose actual statements and FLE can be reconciled. Label the subset clearly instead of substituting a ministry forecast for a sector-wide actual.
6. Show original-budget delivery as an evidence gap because original-versus-revised status and matching accounting boundaries are not verified.
7. Generate the three principal figures, CSVs and README from one validated result object. Keep exploratory notebooks archival.

## Completion gates

Verify source samples and hashes; test arithmetic, status, coverage and denominator eligibility; rebuild offline into an empty destination; compare generated claims and tables; inspect figures at GitHub width and in print; record independent review and verified fixes. No GitHub push, external publication, ranking, forecasting or regional dashboard is included.
