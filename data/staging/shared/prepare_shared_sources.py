"""Prepare shared population and CPI source extracts.

The script is deterministic for the checked-in raw source files. It does not
download data or infer/extrapolate missing years.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date
from pathlib import Path


RETRIEVED_DATE = "2026-09-17"
POPULATION_SOURCE_ID = "statcan_population_17100009_2026-06-17"
CPI_SOURCE_ID = "statcan_cpi_2025"
POPULATION_RELEASE_DATE = "2026-06-17"
CPI_RELEASE_DATE = "2026-01-19"


SCRIPT_PATH = Path(__file__).resolve()
REPO_DIR = SCRIPT_PATH.parents[3]
RAW_SHARED = REPO_DIR / "data" / "raw" / "shared"
STAGING_SHARED = REPO_DIR / "data" / "staging" / "shared"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    STAGING_SHARED.mkdir(parents=True, exist_ok=True)

    population_archive = RAW_SHARED / "population-17100009.zip"
    population_csv = RAW_SHARED / "population-17100009-archive" / "17100009.csv"
    population_metadata = RAW_SHARED / "population-17100009-archive" / "17100009_MetaData.csv"
    cpi_archive = RAW_SHARED / "cpi-18100005.zip"
    cpi_extract = RAW_SHARED / "cpi-alberta-extract.csv"

    population_rows = read_csv(population_csv)
    selected_population = [
        row
        for row in population_rows
        if row["GEO"] == "Alberta"
        and row["REF_DATE"].endswith("-01")
        and int(row["REF_DATE"][:4]) >= 2012
    ]
    selected_population.sort(key=lambda row: row["REF_DATE"])
    if not selected_population:
        raise ValueError("population filter returned no Alberta January 1 rows")
    if any(row["UOM"] != "Persons" for row in selected_population):
        raise ValueError("population filter returned a non-persons unit")
    if len({row["REF_DATE"] for row in selected_population}) != len(selected_population):
        raise ValueError("population filter returned duplicate reference dates")

    raw_population_extract = RAW_SHARED / "population-alberta-q1-extract.csv"
    write_csv(raw_population_extract, list(selected_population[0]), selected_population)

    population_staging_rows = [
        {
            "year": int(row["REF_DATE"][:4]),
            "population": int(row["VALUE"]),
            "reference_date": f"{row['REF_DATE']}-01",
            "source_id": POPULATION_SOURCE_ID,
        }
        for row in selected_population
    ]
    population_staging = STAGING_SHARED / "population.csv"
    write_csv(
        population_staging,
        ["year", "population", "reference_date", "source_id"],
        population_staging_rows,
    )

    cpi_rows = read_csv(cpi_extract)
    selected_cpi = [
        row
        for row in cpi_rows
        if row["GEO"] == "Alberta"
        and row["Products and product groups"] == "All-items"
        and row["UOM"] == "2002=100"
        and 2012 <= int(row["REF_DATE"]) <= 2025
    ]
    selected_cpi.sort(key=lambda row: row["REF_DATE"])
    if [int(row["REF_DATE"]) for row in selected_cpi] != list(range(2012, 2026)):
        raise ValueError("CPI filter must contain every year from 2012 through 2025")

    cpi_staging_rows = [
        {
            "year": int(row["REF_DATE"]),
            "cpi": float(row["VALUE"]),
            "source_id": CPI_SOURCE_ID,
        }
        for row in selected_cpi
    ]
    cpi_staging = STAGING_SHARED / "cpi.csv"
    write_csv(cpi_staging, ["year", "cpi", "source_id"], cpi_staging_rows)

    sources = {
        "sources": [
            {
                "source_id": POPULATION_SOURCE_ID,
                "title": "Population estimates, quarterly",
                "table_id": "17-10-0009-01",
                "product_id": "17100009",
                "url": "https://www150.statcan.gc.ca/n1/tbl/csv/17100009-eng.zip",
                "landing_url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000901",
                "release_date": POPULATION_RELEASE_DATE,
                "retrieved_date": RETRIEVED_DATE,
                "raw_files": [
                    {
                        "path": "data/raw/shared/population-17100009.zip",
                        "sha256": sha256(population_archive),
                    },
                    {
                        "path": "data/raw/shared/population-17100009-archive/17100009.csv",
                        "sha256": sha256(population_csv),
                    },
                    {
                        "path": "data/raw/shared/population-17100009-archive/17100009_MetaData.csv",
                        "sha256": sha256(population_metadata),
                    },
                ],
                "extraction": {
                    "input": "data/raw/shared/population-17100009-archive/17100009.csv",
                    "filters": {
                        "GEO": "Alberta",
                        "UOM": "Persons",
                        "REF_DATE": "2012-01 through latest available January 1 row",
                        "quarter_rule": "Q1 = January 1 (confirmed by table metadata)",
                    },
                    "rows": len(selected_population),
                    "output": "data/raw/shared/population-alberta-q1-extract.csv",
                    "normalized_output": "data/staging/shared/population.csv",
                },
            },
            {
                "source_id": CPI_SOURCE_ID,
                "title": "Consumer Price Index, annual average, not seasonally adjusted",
                "table_id": "18-10-0005-01",
                "product_id": "18100005",
                "url": "https://www150.statcan.gc.ca/n1/tbl/csv/18100005-eng.zip",
                "landing_url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000501",
                "release_date": CPI_RELEASE_DATE,
                "retrieved_date": RETRIEVED_DATE,
                "raw_files": [
                    {
                        "path": "data/raw/shared/cpi-18100005.zip",
                        "sha256": sha256(cpi_archive),
                    },
                    {
                        "path": "data/raw/shared/cpi-alberta-extract.csv",
                        "sha256": sha256(cpi_extract),
                    },
                ],
                "extraction": {
                    "input": "data/raw/shared/cpi-alberta-extract.csv",
                    "filters": {
                        "GEO": "Alberta",
                        "Products and product groups": "All-items",
                        "UOM": "2002=100",
                        "REF_DATE": "2012 through 2025 inclusive",
                    },
                    "rows": len(selected_cpi),
                    "output": "data/staging/shared/cpi.csv",
                    "note": "No 2026 CPI value is included or extrapolated.",
                },
            },
        ]
    }
    source_records = STAGING_SHARED / "source_records.json"
    source_records.write_text(
        json.dumps(sources, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    notes = f"""# Shared source extraction notes

Prepared on {RETRIEVED_DATE} from local raw source files. This script does not access the network and does not extrapolate values.

## Population

- Source: Statistics Canada Table 17-10-0009-01, `Population estimates, quarterly`.
- Release date: {POPULATION_RELEASE_DATE}; retrieval date: {RETRIEVED_DATE}.
- Raw archive: `data/raw/shared/population-17100009.zip`.
- Filter: `GEO=Alberta`, `UOM=Persons`, `REF_DATE` ending `-01`, year >= 2012. Table metadata defines Q1 as January 1.
- Selected rows: {len(selected_population)} (2012-01 through {selected_population[-1]['REF_DATE']}).
- Raw filtered extract: `data/raw/shared/population-alberta-q1-extract.csv`.
- Staging output: `data/staging/shared/population.csv` with columns `year,population,reference_date,source_id`.
- Source ID: `{POPULATION_SOURCE_ID}`.

## CPI

- Source: Statistics Canada Table 18-10-0005-01, `Consumer Price Index, annual average, not seasonally adjusted`.
- Release date: {CPI_RELEASE_DATE}; retrieval date: {RETRIEVED_DATE}.
- Existing raw extract: `data/raw/shared/cpi-alberta-extract.csv`.
- Filter: `GEO=Alberta`, `Products and product groups=All-items`, `UOM=2002=100`, years 2012-2025 inclusive.
- Selected rows: {len(selected_cpi)}; no 2026 CPI is included or extrapolated.
- Staging output: `data/staging/shared/cpi.csv` with columns `year,cpi,source_id`.
- Source ID: `{CPI_SOURCE_ID}`.

Exact source URLs, local raw-file SHA-256 hashes, filters, and output paths are in `data/staging/shared/source_records.json`.
"""
    (STAGING_SHARED / "extraction_notes.md").write_text(notes, encoding="utf-8")

    print(f"population rows: {len(selected_population)}")
    print(f"population staging: {population_staging}")
    print(f"cpi rows: {len(selected_cpi)}")
    print(f"cpi staging: {cpi_staging}")
    print(f"source records: {source_records}")


if __name__ == "__main__":
    main()
