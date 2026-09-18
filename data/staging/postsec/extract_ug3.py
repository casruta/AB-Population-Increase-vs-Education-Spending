"""Prepare the three-university expense subset from reviewed transcriptions.

The numeric specifications below are manual transcriptions of the archived
2024-25 audited expense-by-object schedules, including 2023-24 comparatives.
MRU's financial tables are image-only and were visually transcribed. This
script calculates exclusions and totals; it does not extract those PDF tables
automatically. It matches FLE rows from extract_evidence.py's staging output.
Budget candidates remain unselected because their original-versus-revised
status has not been independently confirmed. Run from any working directory.
"""

import csv
import hashlib
import json
from pathlib import Path

out = Path(__file__).resolve().parent
raw = out.parents[1] / "raw" / "postsec"


def save(name, rows):
    """Write rows with their existing field order and CSV serialization."""
    with (out / name).open("w", newline="", encoding="utf8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


# Each pair is [2023-24, 2024-25], in CAD thousands. Fields are institution,
# source ID, fiscal end, PDF page, printed page, total expense, tangible
# amortization, intangible amortization, identified disposal loss, and the
# budget's total expense, tangible amortization and intangible amortization.
specs = [
    (
        "Grant MacEwan University", "macewan2024-25", "March 31", 88, 82,
        [260105, 278164], [17098, 17322], [0, 0], [1532, 0],
        269803, 16730, 0,
    ),
    (
        "Mount Royal University", "mru2024-25", "March 31", 72, 31,
        [251608, 270508], [15692, 16352], [32, 138], [0, 0],
        269020, 17163, 0,
    ),
    (
        "Alberta University of the Arts", "auarts2024-25", "June 30", 52, 24,
        [26407, 27403], [1338, 1508], [0, 0], [0, 0],
        27150, 1508, 0,
    ),
]
components = []
for (
    institution, source_id, fiscal_end, pdf_page, printed_page, totals,
    tangible, intangible, disposal_loss, budget, budget_tangible, budget_intangible,
) in specs:
    for index, year in enumerate([2023, 2024]):
        excluding_amortization = (
            totals[index] - tangible[index] - intangible[index]
        )
        components.append(dict(
            institution=institution,
            year=year,
            period=f"{year}-{str(year + 1)[2:]}",
            fiscal_end=f"{year + 1} " + fiscal_end,
            status="actual",
            total_expenses_thousands=totals[index],
            amortization_tangible_thousands=tangible[index],
            amortization_intangible_thousands=intangible[index],
            identified_capital_disposal_loss_thousands=disposal_loss[index],
            expenses_excluding_amortization_m=excluding_amortization / 1000,
            expenses_excluding_amortization_and_identified_disposal_m=(
                excluding_amortization - disposal_loss[index]
            ) / 1000,
            source_id=source_id,
            locator=(
                f"PDF p{pdf_page}; financial statement printed p{printed_page}; "
                f"Expense(s) by object; {year + 1} Actual column"
            ),
            notes=(
                "Actual includes all institutional activities including ancillary "
                "services, research and scholarships; capital acquisition excluded "
                "by accrual statement design. Source comparatives may be "
                "reclassified for current presentation."
            ),
        ))
save("undergraduate3_expense_components.csv", components)

expenses = []
for year in [2023, 2024]:
    values = [row for row in components if row["year"] == year]
    expenses.append(dict(
        observation_id=f"postsec_ug3_expenses_{year}",
        series_id="postsec_operating_expenses_ug3",
        year=year,
        period=f"{year}-{str(year + 1)[2:]}",
        amount_m=round(sum(
            row["expenses_excluding_amortization_and_identified_disposal_m"]
            for row in values
        ), 3),
        status="actual",
        budget_basis="",
        segment="ug3_fiscal_2023_2024",
        source_id="postsec_ug3_2024_25_financials",
        locator=(
            "Components in undergraduate3_expense_components.csv; sum all 3 "
            "expense totals less tangible/intangible amortization and separately "
            "identified capital disposal loss"
        ),
        selected=True,
    ))
save("undergraduate3_expenses.csv", expenses)

with (out / "fle_institutions.csv").open(encoding="utf8") as file:
    institution_fle = list(csv.DictReader(file))
enrolment = []
for year in [2023, 2024]:
    selected_rows = [
        row for row in institution_fle
        if int(row["year"]) == year and row["institution"] in [s[0] for s in specs]
    ]
    assert len(selected_rows) == 3
    enrolment.append(dict(
        denominator_id="postsec_ug3_approved_fle",
        year=year,
        period=f"{year}-{str(year + 1)[2:]}",
        learners=round(sum(float(row["fle"]) for row in selected_rows), 3),
        unit="FLE",
        status="final",
        coverage_id="undergraduate_universities_3",
        source_id="alberta_lers_fle_2024_25",
        locator="By Sector and Institution!" + ",".join(
            row["locator"].split("!")[-1] for row in selected_rows
        ),
        segment="ug3_fiscal_2023_2024",
        eligible=True,
        note=(
            "Same 3 institutions as expense numerator. 12-month institutional fiscal "
            "periods; MRU/MacEwan end March 31 and AUArts June 30. Academic-year cycles "
            "align by start-year label, not exact month. These 3 have no 2023/2024 "
            "reporting-change entries in current LERS workbook."
        ),
    ))
save("undergraduate3_fle.csv", enrolment)

budget_candidates = []
for (
    institution, source_id, fiscal_end, pdf_page, printed_page, totals,
    tangible, intangible, disposal_loss, budget, budget_tangible, budget_intangible,
) in specs:
    budget_candidates.append(dict(
        institution=institution,
        year=2024,
        total_expenses_budget_thousands=budget,
        amortization_budget_thousands=budget_tangible + budget_intangible,
        expense_excluding_amortization_budget_m=(
            budget - budget_tangible - budget_intangible
        ) / 1000,
        status="budget",
        budget_basis="board_approved_origin_not_independently_verified",
        selected=False,
        source_id=source_id,
        locator=f"PDF p{pdf_page} Expense by object budget column",
        note=(
            "FS budget note says approved by Board and submitted to Minister; does not "
            "explicitly identify original or revised. Do not admit "
            "original budget delivery until original budget independently matched."
        ),
    ))
save("undergraduate3_budget_candidates.csv", budget_candidates)

urls = {
    "macewan2024-25": "https://www.macewan.ca/c/documents/annual-report-2024-25.pdf",
    "mru2024-25": (
        "https://www.mtroyal.ca/AboutMountRoyal/OfficesGovernance/_pdfs/"
        "pdf_annualreport_2024-2025.pdf"
    ),
    "auarts2024-25": (
        "https://www.auarts.ca/sites/default/files/2025-12/"
        "AUArts%202024-25%20Annual%20Report%20-%20Signed.pdf"
    ),
}
sources = []
for institution, source_id, *_ in specs:
    source_file = raw / (source_id + ".pdf")
    sources.append(dict(
        source_id=source_id,
        title=institution + " Annual Report 2024-25 audited financial statements",
        url=urls[source_id],
        release_date=None,
        retrieval_date="2026-09-17",
        raw_file="data/raw/postsec/" + source_file.name,
        sha256=hashlib.sha256(source_file.read_bytes()).hexdigest(),
        notes=(
            "Release date not independently confirmed. Expense by object "
            "audited statement; see component locator."
        ),
    ))
(out / "undergraduate3_sources.json").write_text(
    json.dumps(sources, indent=2), encoding="utf8"
)
print(expenses)
print(enrolment)
