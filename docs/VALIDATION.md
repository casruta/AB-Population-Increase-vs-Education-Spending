# Validation report

**Release checks passed · September 2026.** No unresolved correctness blocker remains within the admitted evidence boundaries. Source gaps are retained as gaps, not treated as failed arithmetic or zero spending.

| Check | Result |
|---|---|
| Official source admission | Independent reviewer checked source observations, accounting deductions, workbook cells, institution coverage and source hashes |
| Canonical integration | 47 retained financial rows; 37 selected actuals; 22 denominator rows; 78 source records |
| Published coverage | 26 eligible ratios across four measures; 56 year/measure coverage rows; zero verified original-budget pairs |
| Calculation tests | Eight tests passed under Python 3.12.14, pandas 3.0.6, NumPy 2.5.3 and Matplotlib 3.11.2 |
| Offline publication | Two empty-destination builds with Python socket creation disabled produced 13 byte-identical artifacts: README, six figures, five CSVs and summary JSON |
| Output agreement | Every exported numeric column matched validated results within the CSV's six-decimal precision; README endpoint values and relative links checked |
| Source preparation | Independently reran all four local preparation scripts; 21 staged CSV/JSON files reproduced unchanged after newline normalization |
| GitHub presentation | Independent reviewer inspected all three figures at 820-pixel reading width and verified author corrections |
| Print | Lead inspected all three rendered figures on landscape A4 pages: labels, annotations and gap explanations are legible and unclipped |
| Original archive | Original tracked inputs, notebooks, code and charts retained at `archive/original/`; obsolete root copies removed only after matching archive hashes |

## What the tests protect

Tests cover constant-dollar arithmetic, official CPI observations, selected-row uniqueness, duplicate JSON IDs, strict booleans, source-hash failures, status validation, period/unit/coverage matching, ineligible denominators and original-budget pairing. Source-based assertions pin K–12 accounting and headcount observations, the three-university expense/FLE pair, the distinct public-20 grant boundary, and the two withheld recent system ratios. No missing value is substituted with zero or provincial population.

The code reviewer requested the new post-secondary boundary regression; the calculation author added it and the reviewer independently reran it. The policy reviewer requested clearer dot/line captions, accounting-break annotations, exact measure labels, precise excluded-expense wording, larger text and explicit withheld periods. The presentation author corrected them and the reviewer verified the generated results. The evidence reviewer also verified the lead's metadata fixes. Preparation-path and formatting fixes were independently checked by the lead through complete local regeneration.

## Reproduce the maintained publication

Install dependencies once, then run locally without network access:

```sh
python -m pip install -r requirements.txt -c constraints.txt
python -m unittest discover -v
python generate_all_charts.py
```

Use `python generate_all_charts.py --output-dir PATH` with an empty destination for a clean publication build. It reads source inputs from the repository and writes only generated README, figures and tables to that destination. Supporting documentation and source files remain in the repository. The CI workflow repeats tests and an isolated build; no remote CI run or GitHub push was performed for this local release.

## Evidence still needed

The post-secondary expense result covers MacEwan, Mount Royal and Alberta University of the Arts only. Broader sector expenses require a complete institution-level reconciliation. Public-20 grant ratios for 2023–24 and 2024–25 are withheld because of enrolment reporting problems; earlier reported levels also carry unresolved comparability limitations. K–12 2023–24 includes draft Northland reporting. Original-budget status and equivalent accounting boundaries remain unverified, so no delivery variance is published. These are explicit limits on conclusions, not claims that the institutions have no budgets or resources.

Charts use general consumer-price inflation and approximate alignment of financial and academic periods. The evidence does not establish instructional cost, efficiency, causation or an adequate funding level.

Independent review records:

- [Source and accounting admission](reviews/evidence-review.md)
- [Code and data review](reviews/code-data-review.md)
- [Policy and visual review](reviews/policy-visual-review.md)
