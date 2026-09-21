# Evidence-brief migration

## September 2026 report integration

The README now leads with the reviewed report's findings in short paragraphs. Added revised 2024-25 and 2025-26 school allocations, projected 2026-27 funding, monthly CPI through August 2026, and consolidated education expense per resident. Current charts use 2025 dollars and school-year inflation. The downloadable PDF preserves the reviewed report snapshot.

The previous four-series analysis remains available as supporting audit evidence, with its original definitions intact. The publication build regenerates the current README, charts and evidence tables offline; tests distinguish the new measures from historical audit outputs.

The earlier analysis compared five selected ministry-budget observations with provincial population. Its unmodified code, inputs, notebooks and charts are preserved in `archive/original/` from commit `b261e252c19eb8709d023297e752e2f1d3e8ea55`.

The maintained publication separates provincial grants from institutional expenses and matches each approved series to its own learner coverage. It does not promote earlier ministry totals into either of those measures.

## CPI correction

The official annual Alberta All-items table differs from four original observations:

| Year | Original input | Official annual CPI |
|---|---:|---:|
| 2012 | 127.1 | 127.1 |
| 2013 | 128.6 | 128.9 |
| 2023 | 164.4 | 164.1 |
| 2024 | 169.2 | 168.9 |
| 2025 | 172.1 | 172.2 |

Source: [Statistics Canada Table 18-10-0005-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000501), vector `v41694625`, annual Alberta All-items index, 2002=100. The current inputs preserve the verified extract and its provenance.

The archived figures still use their original inputs. They are retained as historical evidence of the change and must not be mistaken for the maintained results.
