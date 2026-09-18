"""Prepare post-secondary grants and FLE staging tables from archived sources.

Grant amounts and FLE rows are extracted automatically from existing PDF text
extracts and the official workbook. Source selection, coverage exclusions,
comparability segments and eligibility are reviewed decisions encoded below;
they are not inferred by the parser. This script does not download sources or
regenerate PDF text. Run it from any working directory after archiving inputs.
"""

import csv
import hashlib
import json
import re
from pathlib import Path

import openpyxl

out = Path(__file__).resolve().parent
raw = out.parents[1] / "raw" / "postsec"


def save(name, rows):
    """Write rows with their existing field order and CSV serialization."""
    with (out / name).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


# Build the registry from archived metadata; preserve unknown release dates.
registry = []
for metafile in [
    "annual-reports-metadata.json",
    "early-annual-metadata.json",
    "iae-metadata.json",
]:
    metadata = json.loads((raw / metafile).read_text(encoding="utf-8-sig"))["result"]
    for resource in metadata["resources"]:
        name = resource["name"]
        year = 2014 if name.startswith("Innovation") else int(name[:4])
        source_file = raw / f"ae-{year}-{year + 1}.pdf"
        if year >= 2015:
            release_date = resource["created"][:10]
            release_precision = "resource publication date"
        elif year == 2012:
            release_date = "2013-07-01"
            release_precision = "metadata issuedate; day may be catalog placeholder"
        else:
            release_date = None
            release_precision = "unconfirmed; not imputed"
        registry.append(dict(
            source_id=f"ae_ar_{year}",
            title=f"{metadata['title']}: {year}-{year + 1}",
            url=resource["url"],
            release_date=release_date,
            retrieval_date="2026-09-17",
            raw_file="data/raw/postsec/" + source_file.name,
            sha256=hashlib.sha256(source_file.read_bytes()).hexdigest(),
            release_date_precision=release_precision,
            notes=(
                "Official annual report; grant category is all department programs, "
                "infrastructure separately reported. Supplemental unaudited "
                "schedules where so titled."
            ),
        ))

rows = []
for source_file in sorted(raw.glob("ae-*.txt")):
    report_year = int(source_file.name[3:7])
    parts = re.split(
        r"---PDF PAGE (\d+)---", source_file.read_text(encoding="utf-8")
    )
    for index in range(1, len(parts), 2):
        text = parts[index + 1]
        if not all(label in text for label in [
            "Operating Grants",
            "Total Public Post-Secondary Institutions",
            "Infrastructure",
        ]):
            continue
        total_line = next(
            line for line in text.splitlines()
            if "Total Public Post-Secondary Institutions" in line
        )
        banff_line = next(
            line for line in text.splitlines()
            if "Banff" in line and re.search(r"\d,\d{3}", line)
        )
        totals = [
            int(value.replace(",", ""))
            for value in re.findall(r"\b\d[\d,]*\b", total_line)
        ]
        banff = [
            int(value.replace(",", ""))
            for value in re.findall(r"\b\d[\d,]*\b", banff_line)
        ]
        # Public institution rows run from Athabasca to the row before Banff.
        institution_lines = text[
            text.index("Athabasca University"):text.index(banff_line)
        ].splitlines()
        amounts = []
        for line in institution_lines:
            matches = re.findall(r"\b\d[\d,]*\b", line)
            if len(matches) >= 2:
                amounts.append([
                    int(value.replace(",", "")) for value in matches[:2]
                ])
        assert len(amounts) == 20, (source_file, len(amounts))
        for column, label in [(0, "current"), (1, "previous")]:
            calculated = sum(values[column] for values in amounts)
            reported = totals[column] - banff[column]
            assert abs(calculated - reported) <= 2, (
                source_file, f"sum mismatch {label}", calculated, reported
            )
        (out / f"grant-table-{report_year}.txt").write_text(
            re.sub(" +", " ", text), encoding="utf8"
        )
        for column, year in enumerate([report_year, report_year - 1]):
            if year < 2012:
                continue
            if year < 2014:
                segment = "department_programs_2012_2013"
            elif year < 2022:
                segment = "department_programs_2014_2021"
            else:
                segment = "department_programs_2022_onward"
            rows.append(dict(
                observation_id=f"postsec_grants_{year}_ar{report_year}",
                series_id="postsec_operating_grants",
                year=year,
                period=f"{year}-{str(year + 1)[2:]}",
                amount_m=round((totals[column] - banff[column]) / 1000, 3),
                status="actual",
                budget_basis="",
                segment=segment,
                source_id=f"ae_ar_{report_year}",
                locator=(
                    f"PDF p{parts[index]}, Funding Provided to Post-Secondary "
                    f"Institutions table, Operating Grants {year + 1} column, "
                    "Total Public Post-Secondary Institutions minus Banff Centre; "
                    "20 institution rows reconcile within CAD2000 table rounding"
                ),
                selected=False,
                public21_grants_m=totals[column] / 1000,
                excluded_banff_m=banff[column] / 1000,
                source_vintage_year=report_year,
                notes=(
                    "Comparative column; may be restated."
                    if column else "Current-year actual column."
                ),
            ))

# Explicit reviewed selection map; see COVERAGE.md for each decision.
selected_map = {
    2012: 2013,
    2013: 2014,
    2014: 2015,
    2015: 2016,
    2016: 2017,
    2017: 2018,
    2018: 2019,
    2019: 2019,
    2020: 2021,
    2021: 2022,
    2022: 2023,
    2023: 2024,
    2024: 2024,
}
for record in rows:
    record["selected"] = (
        selected_map[record["year"]] == record["source_vintage_year"]
    )
save("grants.csv", rows)

# Archive all institution FLE rows; mark the reviewed 20-public-institution set.
workbook = openpyxl.load_workbook(raw / "system-fle.xlsx", data_only=True)
institution_fle = []
for index, values in enumerate(workbook["By Sector and Institution"].values, 1):
    if index == 1 or not values[0]:
        continue
    category, period, sector, institution, fle = values
    if "Total" in institution or sector == "System Total":
        continue
    institution_fle.append(dict(
        year=int(period[:4]),
        period=period,
        institution=institution,
        sector=sector,
        fle=fle,
        public20=sector != "Independent Academic Institutions",
        source_id="alberta_lers_fle_2024_25",
        locator=f"By Sector and Institution!E{index}",
    ))
save("fle_institutions.csv", institution_fle)

notes = []
for index, values in enumerate(workbook["Reporting Changes"].values, 1):
    if index > 3 and values[0]:
        notes.append(dict(
            year=int(values[0].strip()[:4]),
            institution=values[1],
            note=values[2],
            locator=f"Reporting Changes!A{index}:C{index}",
        ))
save("fle_reporting_changes.csv", notes)

segments = {
    2015: "fle_2015_2016",
    2016: "fle_2015_2016",
    2017: "fle_2017",
    2018: "fle_2018",
    2019: "fle_2019_2020",
    2020: "fle_2019_2020",
    2021: "fle_2021",
    2022: "fle_2022",
    2023: "fle_2023_ineligible",
    2024: "fle_2024_ineligible",
}
summary = []
for year in range(2015, 2025):
    selected_rows = [
        row for row in institution_fle if row["year"] == year and row["public20"]
    ]
    assert len(selected_rows) == 20
    local_notes = [row for row in notes if row["year"] == year]
    summary.append(dict(
        denominator_id="postsec_public20_approved_fle",
        year=year,
        period=f"{year}-{str(year + 1)[2:]}",
        learners=round(sum(row["fle"] for row in selected_rows), 3),
        unit="FLE",
        status="final",
        coverage_id="alberta_public20_excluding_banff",
        source_id="alberta_lers_fle_2024_25",
        locator=(
            "By Sector and Institution; sum institution rows with sector other "
            "than Independent Academic Institutions; omit all subtotal/system rows"
        ),
        segment=segments[year],
        eligible=year < 2023,
        note=" | ".join(
            row["institution"] + ": " + row["note"] for row in local_notes
        ),
    ))
save("fle.csv", summary)

registry.append(dict(
    source_id="alberta_lers_fle_2024_25",
    title=(
        "System-Wide Full Load Equivalent (FLE) Enrolment within the Alberta "
        "Post-Secondary Education System"
    ),
    url=(
        "https://open.alberta.ca/dataset/ffcaf092-af60-4149-aeec-005c8476e321/"
        "resource/1a1ceeab-c738-41ec-ba8e-42a454488d80/download/"
        "system-full-load-equivalent-fle-enrolment-within-the-alberta-"
        "post-secondary-education-system.xlsx"
    ),
    release_date="2026-04-17",
    retrieval_date="2026-09-17",
    raw_file="data/raw/postsec/system-fle.xlsx",
    sha256=hashlib.sha256((raw / "system-fle.xlsx").read_bytes()).hexdigest(),
    notes=(
        "All Learners, exact20 public institution rows; independent academic "
        "institutions and all subtotals excluded. Banff absent by source design. "
        "Complete reporting-change notes archived."
    ),
))
(out / "sources.json").write_text(json.dumps(registry, indent=2), encoding="utf8")
(out / "fle_metadata.json").write_text(
    json.dumps({
        name: list(workbook[name].values)
        for name in ["Information", "Dictionary", "Reporting Changes"]
    }, indent=2),
    encoding="utf8",
)
print("SELECTED GRANTS", [
    (row["year"], row["amount_m"]) for row in rows if row["selected"]
])
print("FLE", [
    (row["year"], row["learners"], row["eligible"]) for row in summary
])
