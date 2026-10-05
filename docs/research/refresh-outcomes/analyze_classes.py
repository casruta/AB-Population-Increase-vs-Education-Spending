"""Reproduce included-class-record statistics with Python's standard library.

No student records are created; source identifiers are used only for coverage counts.
Run from the repository root. Suppressed groups are known to have fewer than ten
students, so they count in the denominator and cannot count as exceeding 30.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from xml.etree import ElementTree as ET
from zipfile import ZipFile

BASE = Path(__file__).resolve().parent
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def analyze(path):
    groups = defaultdict(list)
    suppressed = Counter()
    authorities, schools = set(), set()
    with ZipFile(path) as archive:
        strings = ["".join(node.itertext()) for node in
                   ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        root = ET.fromstring(archive.read("xl/worksheets/sheet2.xml"))
        for row in root.findall("m:sheetData/m:row", NS)[1:]:
            values = {}
            for cell in row:
                node = cell.find("m:v", NS)
                value = node.text if node is not None else ""
                if cell.get("t") == "s":
                    value = strings[int(value)]
                column = "".join(filter(str.isalpha, cell.get("r")))
                values[column] = value
            if not values.get("A"):
                continue
            authorities.add(values["C"])
            schools.add(values["D"])
            band, value = values["F"], values["G"]
            if value == "*":
                suppressed[band] += 1
            else:
                size = int(value)
                if not 10 <= size <= 60:
                    raise ValueError(f"Unexpected disclosed class size: {size}")
                groups[band].append(size)
    result = {"authority_count": len(authorities), "school_count": len(schools),
              "observation_date": "2025-11-24", "grade_bands": {}}
    for band, sizes in sorted(groups.items()):
        total = len(sizes) + suppressed[band]
        over30 = sum(size > 30 for size in sizes)
        result["grade_bands"][band] = {
            "class_records": total, "disclosed_records": len(sizes),
            "suppressed_under10": suppressed[band], "over30_records": over30,
            "over30_percent_of_all_included_records": 100 * over30 / total,
            "unweighted_mean_disclosed_only": mean(sizes),
        }
    return result


if __name__ == "__main__":
    result = analyze(BASE / "class-size-2025-2026.xlsx")
    (BASE / "class-size-summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
