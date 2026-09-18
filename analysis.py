"""Validate local evidence and calculate publication values without network access."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
SPENDING = {"observation_id", "series_id", "year", "period", "amount_m", "status",
            "budget_basis", "coverage_id", "segment", "source_id", "locator", "selected"}
ENROLMENT = {"denominator_id", "year", "period", "learners", "unit", "status",
             "coverage_id", "source_id", "locator", "segment", "eligible", "note"}
SERIES = {"sector", "measure", "label", "coverage_ids", "denominator_id",
          "learner_unit", "period_basis", "match_note", "limitation", "gap_reason",
          "target_start", "target_end"}
PERIOD = re.compile(r"^(\d{4})-(\d{2})$")


def _fail(message: str) -> None:
    raise ValueError(message)


def _table(path: Path, required: set[str]) -> pd.DataFrame:
    if not path.is_file():
        _fail(f"Missing input: {path}")
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = required - set(frame.columns)
    if missing:
        _fail(f"{path.name} missing columns: {sorted(missing)}")
    return frame


def _json(path: Path) -> dict:
    if not path.is_file():
        _fail(f"Missing input: {path}")
    def reject_duplicate_keys(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                _fail(f"Duplicate JSON ID or key in {path.name}: {key}")
            value[key] = item
        return value

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    if not isinstance(value, dict):
        _fail(f"{path.name} must be an object keyed by ID")
    return value


def _required_text(frame: pd.DataFrame, columns: set[str], name: str) -> None:
    for column in columns:
        if frame[column].astype(str).str.strip().eq("").any():
            _fail(f"{name}.{column} contains a blank value")


def _unique(frame: pd.DataFrame, columns: list[str], name: str) -> None:
    if frame.duplicated(columns).any():
        _fail(f"Duplicate {name}: {columns}")


def _year(frame: pd.DataFrame, name: str) -> None:
    if not frame["year"].str.fullmatch(r"\d{4}").all():
        _fail(f"{name}.year is malformed")
    frame["year"] = frame["year"].astype(int)
    if not frame["year"].between(1900, 2100).all():
        _fail(f"{name}.year is outside the supported calendar range")


def _number(frame: pd.DataFrame, column: str, name: str, *, positive: bool = False) -> None:
    try:
        values = pd.to_numeric(frame[column], errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{name}.{column} is not numeric") from exc
    if not values.map(math.isfinite).all() or (values <= 0 if positive else values < 0).any():
        _fail(f"{name}.{column} must be finite and {'positive' if positive else 'nonnegative'}")
    frame[column] = values


def _boolean(frame: pd.DataFrame, column: str, name: str) -> None:
    if not frame[column].isin({"True", "False"}).all():
        _fail(f"{name}.{column} must be exactly True or False")
    frame[column] = frame[column].eq("True")


def _period(frame: pd.DataFrame, name: str) -> None:
    for year, period in zip(frame["year"], frame["period"]):
        match = PERIOD.fullmatch(period)
        if not match or int(match.group(1)) != year or int(match.group(2)) != (year + 1) % 100:
            _fail(f"{name} has a malformed or mismatched period: {period}")


def _sources(root: Path, sources: dict) -> None:
    if not sources:
        _fail("sources.json is empty")
    for source_id, source in sources.items():
        if not isinstance(source_id, str) or not source_id.strip() or not isinstance(source, dict):
            _fail("Invalid source ID or definition")
        if not str(source.get("title", "")).strip() or not str(source.get("url", "")).strip():
            _fail(f"Missing source title or URL: {source_id}")
        if "release_date" not in source or not str(source.get("retrieved_date", "")).strip():
            _fail(f"Missing release/retrieval metadata: {source_id}")
        if source["release_date"] is None and not str(source.get("release_date_precision", "")).strip():
            _fail(f"Unknown release date needs explicit precision: {source_id}")
        files = source.get("raw_files")
        if not isinstance(files, list) or not files:
            _fail(f"Missing raw_files: {source_id}")
        for item in files:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                _fail(f"Malformed raw file: {source_id}")
            path = (root / item["path"]).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file():
                _fail(f"Missing or outside-root raw file: {item['path']}")
            expected = item.get("sha256", "")
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
                _fail(f"Invalid SHA-256: {item['path']}")
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != expected.lower():
                _fail(f"SHA-256 mismatch: {item['path']}")


def load_inputs(root: Path | None = None) -> dict:
    """Load publication inputs as strings so malformed values cannot be coerced away."""
    root = Path(root or ROOT)
    data = root / "data"
    return {
        "spending": _table(data / "spending.csv", SPENDING),
        "enrolment": _table(data / "enrolment.csv", ENROLMENT),
        "cpi": _table(data / "cpi.csv", {"year", "cpi", "source_id"}),
        "population": _table(data / "population.csv", {"year", "population", "reference_date", "source_id"}),
        "series": _json(data / "series.json"),
        "sources": _json(data / "sources.json"),
    }


def validate_inputs(root: Path | None = None) -> dict:
    """Return typed inputs, failing on ambiguous observations or broken provenance."""
    root = Path(root or ROOT)
    inputs = load_inputs(root)
    spending, enrolment = inputs["spending"], inputs["enrolment"]
    cpi, population = inputs["cpi"], inputs["population"]
    series, sources = inputs["series"], inputs["sources"]
    _sources(root, sources)
    if not series:
        _fail("series.json is empty")
    for series_id, definition in series.items():
        if not isinstance(series_id, str) or not series_id.strip() or not isinstance(definition, dict):
            _fail("Invalid series ID or definition")
        if SERIES - definition.keys():
            _fail(f"Incomplete series definition: {series_id}")
        if definition["sector"] not in {"k12", "postsec"} or definition["measure"] not in {"grants", "expenses"}:
            _fail(f"Invalid sector or measure: {series_id}")
        for field in ("label", "denominator_id", "learner_unit", "period_basis", "match_note", "limitation", "gap_reason"):
            if not isinstance(definition[field], str) or not definition[field].strip():
                _fail(f"Blank {field}: {series_id}")
        if definition["learner_unit"] not in {"headcount", "FTE", "FLE"}:
            _fail(f"Invalid learner unit: {series_id}")
        if not isinstance(definition["coverage_ids"], list) or not definition["coverage_ids"] or not all(isinstance(x, str) and x.strip() for x in definition["coverage_ids"]):
            _fail(f"Invalid coverage_ids: {series_id}")
        for field in ("target_start", "target_end"):
            if isinstance(definition[field], bool) or not isinstance(definition[field], int):
                _fail(f"Invalid {field}: {series_id}")
        if definition["target_start"] > definition["target_end"]:
            _fail(f"Reversed target years: {series_id}")
    for name, frame, text_fields in (
        ("spending", spending, {"observation_id", "series_id", "period", "status", "coverage_id", "segment", "source_id", "locator"}),
        ("enrolment", enrolment, {"denominator_id", "period", "unit", "status", "coverage_id", "source_id", "locator", "segment"}),
        ("cpi", cpi, {"source_id"}),
        ("population", population, {"reference_date", "source_id"}),
    ):
        _required_text(frame, text_fields, name)
        _year(frame, name)
        if not frame["source_id"].isin(sources).all():
            _fail(f"{name} references an unknown source ID")
    _unique(spending, ["observation_id"], "observation ID")
    _unique(enrolment, ["denominator_id", "year"], "denominator year")
    _unique(cpi, ["year"], "CPI year")
    _unique(population, ["year"], "population year")
    _period(spending, "spending")
    _period(enrolment, "enrolment")
    _boolean(spending, "selected", "spending")
    _boolean(enrolment, "eligible", "enrolment")
    _number(spending, "amount_m", "spending")
    _number(enrolment, "learners", "enrolment", positive=True)
    _number(cpi, "cpi", "cpi", positive=True)
    _number(population, "population", "population", positive=True)
    if not spending["status"].isin({"actual", "budget", "forecast"}).all():
        _fail("Unknown financial status")
    if not enrolment["status"].isin({"final", "preliminary"}).all():
        _fail("Unknown enrolment status")
    if not spending["series_id"].isin(series).all():
        _fail("Unknown series ID in spending")
    if not population["reference_date"].eq(population["year"].astype(str) + "-01-01").all():
        _fail("Population reference dates must be January 1 of their year")
    selected = spending.loc[spending["selected"]]
    _unique(selected, ["series_id", "year", "status"], "selected series/year/status")
    if not selected.loc[selected["status"].eq("budget"), "budget_basis"].isin({"original", "revised", "unknown"}).all():
        _fail("Selected budgets need an explicit budget basis")
    for row in spending.itertuples(index=False):
        definition = series[row.series_id]
        if row.coverage_id not in definition["coverage_ids"]:
            _fail(f"Unapproved financial coverage: {row.observation_id}")
        if row.selected and row.status == "actual" and not definition["target_start"] <= row.year <= definition["target_end"]:
            _fail(f"Selected actual falls outside target years: {row.observation_id}")
    approved_ids = {item["denominator_id"] for item in series.values()}
    if not enrolment["denominator_id"].isin(approved_ids).all():
        _fail("Unknown denominator ID")
    if not enrolment["unit"].isin({"headcount", "FTE", "FLE"}).all():
        _fail("Unknown learner unit")
    if 2012 not in set(cpi["year"]):
        _fail("Missing 2012 CPI baseline")
    missing_cpi = set(selected.loc[selected["status"].eq("actual"), "year"]) - set(cpi["year"])
    if missing_cpi:
        _fail(f"Missing CPI for actual years: {sorted(missing_cpi)}")
    return inputs


def build_analysis(root: Path | None = None) -> dict:
    """Calculate ratio, coverage, demand and budget-delivery tables for rendering."""
    inputs = validate_inputs(root)
    series = inputs["series"]
    selected = inputs["spending"].loc[lambda f: f["selected"]].copy()
    actuals = selected.loc[lambda f: f["status"].eq("actual")].copy()
    enrolment = inputs["enrolment"].copy()
    cpi = inputs["cpi"].set_index("year")["cpi"]
    actuals["real_amount_m"] = actuals["amount_m"] * cpi.loc[2012] / actuals["year"].map(cpi)
    rows = []
    demand_rows = []
    coverage_rows = []
    for series_id, definition in series.items():
        subset = enrolment.loc[enrolment["denominator_id"].eq(definition["denominator_id"])].copy()
        subset["series_id"] = series_id
        demand_rows.append(subset)
        observations = actuals.loc[actuals["series_id"].eq(series_id)]
        by_year = {int(row.year): row for row in observations.itertuples(index=False)}
        denom_by_year = {int(row.year): row for row in subset.itertuples(index=False)}
        for year in range(definition["target_start"], definition["target_end"] + 1):
            financial = by_year.get(year)
            denominator = denom_by_year.get(year)
            reason = ""
            if financial is None:
                reason = definition["gap_reason"]
            elif denominator is None:
                reason = "No approved learner denominator for this period."
            elif denominator.period != financial.period or denominator.coverage_id != financial.coverage_id or denominator.unit != definition["learner_unit"]:
                reason = "Learner period, coverage, or unit does not match the financial observation."
            elif not denominator.eligible:
                reason = denominator.note or "Reported learner count is ineligible for a ratio."
            coverage_rows.append({"series_id": series_id, "year": year, "period": financial.period if financial else f"{year}-{(year + 1) % 100:02d}",
                                  "available": bool(financial is not None and not reason), "gap_reason": reason,
                                  "coverage_id": financial.coverage_id if financial else ""})
            if financial is None:
                continue
            item = financial._asdict()
            item.update({"sector": definition["sector"], "measure": definition["measure"],
                         "learners": denominator.learners if denominator else float("nan"),
                         "learner_unit": denominator.unit if denominator else definition["learner_unit"],
                         "enrolment_status": denominator.status if denominator else "",
                         "financial_segment": financial.segment,
                         "enrolment_segment": denominator.segment if denominator else "",
                         "segment": f"{financial.segment}|{denominator.segment}" if denominator and not reason else "",
                         "real_per_learner": financial.real_amount_m * 1_000_000 / denominator.learners if denominator and not reason else float("nan"),
                         "gap_reason": reason, "denominator_id": definition["denominator_id"],
                         "learner_source_id": denominator.source_id if denominator else "",
                         "note": denominator.note if denominator else ""})
            rows.append(item)
    per_learner = pd.DataFrame(rows)
    coverage = pd.DataFrame(coverage_rows)
    demand = pd.concat(demand_rows, ignore_index=True) if demand_rows else pd.DataFrame()
    plans = selected.loc[selected["status"].eq("budget") & selected["budget_basis"].eq("original")]
    pairs = actuals.merge(plans, on=["series_id", "year", "period", "coverage_id", "segment"], suffixes=("_actual", "_budget"))
    delivery = pd.DataFrame({
        "series_id": pairs["series_id"], "year": pairs["year"], "period": pairs["period"],
        "coverage_id": pairs["coverage_id"], "financial_segment": pairs["segment"],
        "sector": pairs["series_id"].map(lambda key: series[key]["sector"]),
        "measure": pairs["series_id"].map(lambda key: series[key]["measure"]),
        "actual_m": pairs["amount_m_actual"], "original_budget_m": pairs["amount_m_budget"],
        "variance_m": pairs["amount_m_actual"] - pairs["amount_m_budget"],
        "variance_pct": 100 * (pairs["amount_m_actual"] - pairs["amount_m_budget"]) / pairs["amount_m_budget"].replace(0, float("nan")),
        "actual_source_id": pairs["source_id_actual"], "budget_source_id": pairs["source_id_budget"],
    })
    summary = {"base_year": 2012, "latest": {}}
    if not per_learner.empty:
        for series_id, frame in per_learner.dropna(subset=["real_per_learner"]).groupby("series_id"):
            row = frame.sort_values("year").iloc[-1]
            summary["latest"][series_id] = {"year": int(row["year"]), "period": row["period"],
                                            "real_per_learner": float(row["real_per_learner"]),
                                            "segment": row["segment"]}
    return {"series": series, "per_learner": per_learner, "delivery": delivery,
            "coverage": coverage, "demand": demand, "population": inputs["population"], "summary": summary}
