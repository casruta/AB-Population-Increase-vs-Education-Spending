#!/usr/bin/env python3
"""Recompute bounded migration evidence. No canonical inputs are modified."""
import csv, hashlib, json
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
for record in json.loads((BASE / "downloads.json").read_text()):
    retained = record.get("retained_extract", record.get("retained_data"))
    assert retained is not None
    source_path = ROOT / retained["path"]
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == retained["sha256"], source_path
    metadata_path = ROOT / record["metadata_path"]
    assert hashlib.sha256(metadata_path.read_bytes()).hexdigest() == record["metadata_sha256"], metadata_path

def rows(pid, alberta_only=True):
    p = BASE / f"{pid}-alberta.csv"
    if not p.exists():
        p = BASE / pid / f"{pid}.csv"
    with p.open(encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if not alberta_only or r["GEO"] == "Alberta"]

def unique_value(data, expected_uom="Persons", **filters):
    selected = [r for r in data if all(r[k] == v for k, v in filters.items())]
    assert len(selected) == 1, (filters, len(selected))
    r = selected[0]
    assert r["UOM"] == expected_uom and r["SCALAR_FACTOR"] == "units"
    assert r["VALUE"] and r["STATUS"] not in {"..", "x", "F"}, r
    return int(r["VALUE"])

annual_data = rows("17100008")
stocks = rows("17100009")
annual = []
ages = []
for year in range(2021, 2026):
    period = f"{year}/{year+1}"
    names = [r["Components of population growth"] for r in annual_data
             if r["REF_DATE"] == period and r["VALUE"]]
    components = {name: unique_value(annual_data, REF_DATE=period,
                  **{"Components of population growth":name}) for name in names}
    assert len([r for r in annual_data if r["REF_DATE"] == period and r["VALUE"]]) == len(components)
    assert components["Net emigration"] == components["Emigrants"] - components["Returning emigrants"]
    assert components["Net non-permanent residents"] == components["Non-permanent residents, inflows"] - components["Non-permanent residents, outflows"]
    components["Natural increase"] = components["Births"] - components["Deaths"]
    components["Net international migration"] = components["Immigrants"] - components["Net emigration"] + components["Net non-permanent residents"]
    components["Total net migration"] = components["Net international migration"] + components["Net interprovincial migration"]
    start = unique_value(stocks, REF_DATE=f"{year}-07-01")
    end = unique_value(stocks, REF_DATE=f"{year+1}-07-01")
    components["Population growth"] = end - start
    components["Reconciliation gap"] = end-start-components["Natural increase"]-components["Total net migration"]
    assert components["Reconciliation gap"] == 0
    for name in ["Immigrants", "Emigrants", "Returning emigrants", "Net emigration", "Net non-permanent residents"]:
        assert unique_value(rows("17100014"), REF_DATE=period,
               **{"Type of migrant":name, "Age group":"All ages", "Gender":"Total - gender"}) == components[name]
    assert unique_value(rows("17100015"), REF_DATE=period,
           **{"Migrants":"Net-migration", "Age group":"All ages", "Gender":"Total - gender"}) == components["Net interprovincial migration"]
    annual.append(dict(period=period, period_start=f"{year}-07-01", period_end=f"{year+1}-06-30", population_start=start, population_end=end, **components))
    for lo, hi in [(5,17), (6,17), (5,18), (3,17)]:
        values = {}
        for pid, dimension, names in [
            ("17100014", "Type of migrant", ["Immigrants", "Emigrants", "Returning emigrants", "Net emigration", "Net non-permanent residents"]),
            ("17100015", "Migrants", ["In-migrants", "Out-migrants", "Net-migration"])]:
            data = rows(pid)
            for name in names:
                values[name] = sum(unique_value(data, REF_DATE=period, **{dimension:name, "Age group":f"{age} years", "Gender":"Total - gender"}) for age in range(lo,hi+1))
        assert values["Net emigration"] == values["Emigrants"]-values["Returning emigrants"]
        assert values["Net-migration"] == values["In-migrants"]-values["Out-migrants"]
        values["Net international migration"] = values["Immigrants"]-values["Net emigration"]+values["Net non-permanent residents"]
        values["Total net migration"] = values["Net international migration"]+values["Net-migration"]
        ages.append(dict(period=period, age_start=lo, age_end=hi, age_definition="Age at July 1 at start of period; demographic proxy, not enrolled students", **values))
age_stocks = []
for year in range(2021, 2027):
    data = rows("17100005")
    count = sum(unique_value(data, REF_DATE=str(year), **{"Age group":f"{age} years", "Gender":"Total - gender"}) for age in range(5,18))
    age_stocks.append(dict(year=year, reference_date=f"{year}-07-01", age_band="5–17", persons=count))
(BASE / "age-population.json").write_text(json.dumps(age_stocks, indent=2)+"\n")
quarters = []
international = rows("17100040")
interprovincial = rows("17100020")
natural = rows("17100059")
matrix = rows("17100045", alberta_only=False)
for period in sorted({r["REF_DATE"] for r in interprovincial}):
    incoming = sum(int(r["VALUE"]) for r in matrix if r["REF_DATE"] == period and r["Geography, province of destination"] == "Alberta, province of destination")
    outgoing = sum(int(r["VALUE"]) for r in matrix if r["REF_DATE"] == period and r["GEO"] == "Alberta, province of origin")
    assert incoming == unique_value(interprovincial, REF_DATE=period, **{"Interprovincial migration":"In-migrants"})
    assert outgoing == unique_value(interprovincial, REF_DATE=period, **{"Interprovincial migration":"Out-migrants"})
for period in sorted({r["REF_DATE"] for r in international if r["REF_DATE"] >= "2021-07"}):
    year, month = map(int, period.split("-"))
    next_year, next_month = (year+1,1) if month == 10 else (year,month+3)
    values = {name: unique_value(international, REF_DATE=period,
              **{"Components of population growth":name})
              for name in ["Immigrants","Emigrants","Returning emigrants","Net emigration","Net non-permanent residents","Non-permanent residents, inflows","Non-permanent residents, outflows"]}
    for name in ["In-migrants","Out-migrants"]:
        values[name] = unique_value(interprovincial, REF_DATE=period,
                                   **{"Interprovincial migration":name})
    for name in ["Births","Deaths"]:
        values[name] = unique_value(natural, expected_uom="Number", REF_DATE=period,
                                   **{"Estimates":name})
    values["Net international migration"] = values["Immigrants"]-values["Net emigration"]+values["Net non-permanent residents"]
    values["Net interprovincial migration"] = values["In-migrants"]-values["Out-migrants"]
    values["Natural increase"] = values["Births"]-values["Deaths"]
    values["Population growth"] = unique_value(stocks, REF_DATE=f"{next_year}-{next_month:02d}-01")-unique_value(stocks, REF_DATE=f"{year}-{month:02d}-01")
    assert values["Net emigration"] == values["Emigrants"]-values["Returning emigrants"]
    assert values["Net non-permanent residents"] == values["Non-permanent residents, inflows"]-values["Non-permanent residents, outflows"]
    assert values["Population growth"] == values["Natural increase"]+values["Net international migration"]+values["Net interprovincial migration"]
    quarters.append(dict(period=period, period_start=f"{year}-{month:02d}-01", period_end_exclusive=f"{next_year}-{next_month:02d}-01", **values))
for record in annual:
    selected = [q for q in quarters if record["period_start"] <= q["period_start"] <= record["period_end"]]
    assert len(selected) == 4
    for name in ["Immigrants","Emigrants","Returning emigrants","Net emigration","Net non-permanent residents","Net international migration","Net interprovincial migration","Natural increase","Population growth"]:
        assert sum(q[name] for q in selected) == record[name], (record["period"], name)
with (BASE / "quarterly-all-age.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(quarters[0]))
    writer.writeheader()
    writer.writerows(quarters)
result = dict(annual_all_age=annual, annual_age_proxies=ages, quarterly_all_age=quarters)
reviewed = json.loads((BASE / "reviewed_summary.json").read_text())
assert reviewed["annual_all_age"] == annual
assert reviewed["annual_latest"] == annual[-1]
school_age_proxy = [record for record in ages if record["age_start"] == 5 and record["age_end"] == 17]
assert reviewed["age_5_17_trend"] == school_age_proxy
assert reviewed["age_5_17_latest"] == school_age_proxy[-1]
assert reviewed["quarterly_latest"] == quarters[-1]
(BASE / "calculated-evidence.json").write_text(json.dumps(result, indent=2)+"\n")
print(f"Validated five annual and {len(quarters)} quarterly stock-flow identities, annual-quarterly component totals, cross-table all-age matches, twenty age-band identities and six age stocks.")
