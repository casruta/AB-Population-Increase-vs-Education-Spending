# Shared source extraction notes

Prepared on 2026-09-17 from local raw source files. This script does not access the network and does not extrapolate values.

## Population

- Source: Statistics Canada Table 17-10-0009-01, `Population estimates, quarterly`.
- Release date: 2026-06-17; retrieval date: 2026-09-17.
- Raw archive: `data/raw/shared/population-17100009.zip`.
- Filter: `GEO=Alberta`, `UOM=Persons`, `REF_DATE` ending `-01`, year >= 2012. Table metadata defines Q1 as January 1.
- Selected rows: 15 (2012-01 through 2026-01).
- Raw filtered extract: `data/raw/shared/population-alberta-q1-extract.csv`.
- Staging output: `data/staging/shared/population.csv` with columns `year,population,reference_date,source_id`.
- Source ID: `statcan_population_17100009_2026-06-17`.

## CPI

- Source: Statistics Canada Table 18-10-0005-01, `Consumer Price Index, annual average, not seasonally adjusted`.
- Release date: 2026-01-19; retrieval date: 2026-09-17.
- Existing raw extract: `data/raw/shared/cpi-alberta-extract.csv`.
- Filter: `GEO=Alberta`, `Products and product groups=All-items`, `UOM=2002=100`, years 2012-2025 inclusive.
- Selected rows: 14; no 2026 CPI is included or extrapolated.
- Staging output: `data/staging/shared/cpi.csv` with columns `year,cpi,source_id`.
- Source ID: `statcan_cpi_2025`.

Exact source URLs, local raw-file SHA-256 hashes, filters, and output paths are in `data/staging/shared/source_records.json`.
