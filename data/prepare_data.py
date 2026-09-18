"""Assemble reviewed extracts into the publication inputs; no network access."""

from pathlib import Path
import json
import shutil

import pandas as pd


DATA = Path(__file__).resolve().parent
STAGING = DATA / "staging"
SPENDING_COLUMNS = [
    "observation_id", "series_id", "year", "period", "amount_m", "status",
    "budget_basis", "coverage_id", "segment", "source_id", "locator", "selected",
]
ENROLMENT_COLUMNS = [
    "denominator_id", "year", "period", "learners", "unit", "status",
    "coverage_id", "source_id", "locator", "segment", "eligible", "note",
]


def source_records():
    shared = json.loads((STAGING / "shared/source_records.json").read_text())
    k12 = json.loads((STAGING / "k12/k12_sources.json").read_text())
    postsec = json.loads((STAGING / "postsec/sources.json").read_text())
    universities = json.loads((STAGING / "postsec/undergraduate3_sources.json").read_text())
    records = shared["sources"] + [dict(source_id=k, **v) for k, v in k12.items()] + postsec + universities
    sources = {}
    for record in records:
        record = record.copy()
        key = record.pop("source_id")
        if key in sources:
            raise ValueError(f"Duplicate source: {key}")
        if "raw_files" not in record:
            record["raw_files"] = [{"path": record.pop("raw_file"), "sha256": record.pop("sha256")}]
        if "retrieval_date" in record:
            record["retrieved_date"] = record.pop("retrieval_date")
        if record.get("release_date") is None:
            record.setdefault("release_date_precision", "unknown; not independently confirmed")
        sources[key] = record
    sources["postsec_ug3_2024_25_financials"] = {
        "title": "Three undergraduate universities: 2024–25 audited financial statements and 2023–24 comparators",
        "url": "data/staging/postsec/undergraduate3_sources.json",
        "release_date": None,
        "release_date_precision": "Composite of three reports; individual release dates not independently confirmed",
        "retrieved_date": "2026-09-17",
        "raw_files": [item for source in universities for item in sources[source["source_id"]]["raw_files"]],
        "notes": "Composite record; individual official URLs and exact expense components are retained in undergraduate3_sources.json and undergraduate3_expense_components.csv."
    }
    return sources


def main():
    schools = pd.read_csv(STAGING / "k12/k12_spending.csv")
    schools["coverage_id"] = schools["year"].map(
        lambda year: "k12_without_valhalla" if year == 2022 else "k12_alberta_reporting_authorities"
    )
    grants = pd.read_csv(STAGING / "postsec/grants.csv")
    grants["coverage_id"] = "alberta_public20_excluding_banff"
    expenses = pd.read_csv(STAGING / "postsec/undergraduate3_expenses.csv")
    expenses["series_id"] = "postsec_operating_expenses"
    expenses["coverage_id"] = "postsec_undergrad3"
    spending = pd.concat([schools, grants, expenses], ignore_index=True)
    spending["budget_basis"] = spending["budget_basis"].fillna("not_applicable")
    spending[SPENDING_COLUMNS].sort_values(["series_id", "year", "observation_id"]).to_csv(
        DATA / "spending.csv", index=False, lineterminator="\n"
    )

    schools = pd.read_csv(STAGING / "k12/k12_enrolment.csv")
    schools["segment"] = schools["coverage_id"]
    schools["eligible"] = True
    schools["note"] = schools["year"].map(
        lambda year: "Valhalla excluded to match the financial rollup." if year == 2022
        else "Preliminary December 2025 count." if year == 2025 else ""
    )
    postsec = pd.read_csv(STAGING / "postsec/fle.csv")
    universities = pd.read_csv(STAGING / "postsec/undergraduate3_fle.csv")
    universities["denominator_id"] = "postsec_undergrad3_fle"
    universities["coverage_id"] = "postsec_undergrad3"
    pd.concat([schools, postsec, universities], ignore_index=True)[ENROLMENT_COLUMNS].sort_values(
        ["denominator_id", "year"]
    ).to_csv(DATA / "enrolment.csv", index=False, lineterminator="\n")

    for filename in ("cpi.csv", "population.csv"):
        shutil.copyfile(STAGING / "shared" / filename, DATA / filename)
    (DATA / "sources.json").write_text(
        json.dumps(source_records(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("Assembled reviewed source extracts; series definitions are maintained separately.")


if __name__ == "__main__":
    main()
