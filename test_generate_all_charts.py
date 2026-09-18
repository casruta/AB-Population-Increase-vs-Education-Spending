"""Tests for source validation, arithmetic, and non-comparable gaps."""

import csv
import hashlib
import json
import math
import tempfile
import unittest
import zipfile
from pathlib import Path

import pandas as pd

import analysis


ROOT = Path(__file__).resolve().parent


def make_fixture():
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    data = root / "data"
    (data / "raw").mkdir(parents=True)
    raw = data / "raw/evidence.txt"
    raw.write_text("source cell", encoding="utf-8")
    (data / "sources.json").write_text(json.dumps({"src": {
        "title": "Source", "url": "https://example.test", "release_date": "unknown",
        "retrieved_date": "2026-09-17", "raw_files": [{"path": "data/raw/evidence.txt",
        "sha256": hashlib.sha256(raw.read_bytes()).hexdigest()}]}}), encoding="utf-8")
    (data / "series.json").write_text(json.dumps({"sample": {
        "sector": "k12", "measure": "grants", "label": "Sample grants",
        "coverage_ids": ["authority"], "denominator_id": "students", "learner_unit": "headcount",
        "period_basis": "school year", "match_note": "same roster and period", "limitation": "sample",
        "gap_reason": "No reviewed observation.", "target_start": 2012, "target_end": 2015}}), encoding="utf-8")
    pd.DataFrame([
        ["a12", "sample", 2012, "2012-13", 100, "actual", "not_applicable", "authority", "s1", "src", "p1", "True"],
        ["b12", "sample", 2012, "2012-13", 90, "budget", "original", "authority", "s1", "src", "p2", "True"],
        ["f12", "sample", 2012, "2012-13", 95, "forecast", "not_applicable", "authority", "s1", "src", "p3", "True"],
        ["a13", "sample", 2013, "2013-14", 120, "actual", "not_applicable", "authority", "s1", "src", "p4", "True"],
        ["b13", "sample", 2013, "2013-14", 100, "budget", "revised", "authority", "s1", "src", "p5", "True"],
        ["a14", "sample", 2014, "2014-15", 130, "actual", "not_applicable", "authority", "s2", "src", "p6", "True"],
        ["a15", "sample", 2015, "2015-16", 140, "actual", "not_applicable", "authority", "s2", "src", "p7", "True"],
    ], columns=["observation_id", "series_id", "year", "period", "amount_m", "status", "budget_basis",
                "coverage_id", "segment", "source_id", "locator", "selected"]).to_csv(data / "spending.csv", index=False)
    pd.DataFrame([
        ["students", 2012, "2012-13", 50000, "headcount", "final", "authority", "src", "p1", "e1", "True", ""],
        ["students", 2013, "2013-14", 55000, "headcount", "final", "authority", "src", "p2", "e1", "True", ""],
        ["students", 2014, "2014-15", 60000, "headcount", "final", "authority", "src", "p3", "e2", "True", ""],
        ["students", 2015, "2015-16", 65000, "headcount", "preliminary", "authority", "src", "p4", "e2", "False", "Known count defect."],
    ], columns=["denominator_id", "year", "period", "learners", "unit", "status", "coverage_id", "source_id",
                "locator", "segment", "eligible", "note"]).to_csv(data / "enrolment.csv", index=False)
    pd.DataFrame([[2012, 100, "src"], [2013, 125, "src"], [2014, 130, "src"], [2015, 140, "src"]],
                 columns=["year", "cpi", "source_id"]).to_csv(data / "cpi.csv", index=False)
    pd.DataFrame([[year, 1000000, f"{year}-01-01", "src"] for year in range(2012, 2016)],
                 columns=["year", "population", "reference_date", "source_id"]).to_csv(data / "population.csv", index=False)
    return root, temporary


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.root, self.temporary = make_fixture()

    def tearDown(self):
        self.temporary.cleanup()

    def test_real_arithmetic_breaks_and_gap(self):
        result = analysis.build_analysis(self.root)
        rows = result["per_learner"].set_index("year")
        self.assertAlmostEqual(rows.loc[2012, "real_per_learner"], 2000)
        self.assertAlmostEqual(rows.loc[2013, "real_per_learner"], 120 * 100 / 125 * 1_000_000 / 55000)
        self.assertEqual(rows.loc[2012, "segment"], "s1|e1")
        self.assertEqual(rows.loc[2014, "segment"], "s2|e2")
        self.assertTrue(math.isnan(rows.loc[2015, "real_per_learner"]))
        self.assertEqual(rows.loc[2015, "gap_reason"], "Known count defect.")
        self.assertFalse(result["coverage"].set_index("year").loc[2015, "available"])
        self.assertEqual(result["summary"]["latest"]["sample"]["year"], 2014)

    def test_budget_pair_requires_original_and_same_segment(self):
        rows = analysis.build_analysis(self.root)["delivery"]
        self.assertEqual(rows["year"].tolist(), [2012])
        self.assertEqual(rows.iloc[0]["variance_m"], 10)
        self.assertAlmostEqual(rows.iloc[0]["variance_pct"], 100 * 10 / 90)
        path = self.root / "data/spending.csv"
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        frame.loc[frame["observation_id"].eq("b12"), "segment"] = "other"
        frame.to_csv(path, index=False)
        self.assertTrue(analysis.build_analysis(self.root)["delivery"].empty)

    def test_invalid_status_duplicate_and_hash_fail(self):
        path = self.root / "data/spending.csv"
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        frame.loc[frame["observation_id"].eq("a12"), "status"] = "estimate"
        frame.to_csv(path, index=False)
        with self.assertRaisesRegex(ValueError, "financial status"):
            analysis.build_analysis(self.root)
        frame.loc[frame["observation_id"].eq("a12"), "status"] = "actual"
        frame.loc[frame["observation_id"].eq("f12"), "status"] = "actual"
        frame.to_csv(path, index=False)
        with self.assertRaisesRegex(ValueError, "Duplicate selected"):
            analysis.build_analysis(self.root)
        frame.loc[frame["observation_id"].eq("f12"), "status"] = "forecast"
        frame.to_csv(path, index=False)
        (self.root / "data/raw/evidence.txt").write_text("altered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            analysis.build_analysis(self.root)

    def test_mismatched_boundary_has_no_ratio(self):
        path = self.root / "data/enrolment.csv"
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        frame.loc[frame["year"].eq("2013"), "coverage_id"] = "other"
        frame.to_csv(path, index=False)
        row = analysis.build_analysis(self.root)["per_learner"].set_index("year").loc[2013]
        self.assertTrue(math.isnan(row["real_per_learner"]))
        self.assertIn("does not match", row["gap_reason"])

    def test_mismatched_unit_and_period_have_no_ratio(self):
        path = self.root / "data/enrolment.csv"
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        frame.loc[frame["year"].eq("2013"), "unit"] = "FLE"
        frame.to_csv(path, index=False)
        row = analysis.build_analysis(self.root)["per_learner"].set_index("year").loc[2013]
        self.assertTrue(math.isnan(row["real_per_learner"]))
        frame.loc[frame["year"].eq("2013"), "unit"] = "headcount"
        frame.loc[frame["year"].eq("2013"), "period"] = "2014-15"
        frame.to_csv(path, index=False)
        with self.assertRaisesRegex(ValueError, "mismatched period"):
            analysis.build_analysis(self.root)

    def test_boolean_cpi_and_duplicate_json_validation(self):
        path = self.root / "data/spending.csv"
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        frame.loc[0, "selected"] = "yes"
        frame.to_csv(path, index=False)
        with self.assertRaisesRegex(ValueError, "exactly True or False"):
            analysis.build_analysis(self.root)
        frame.loc[0, "selected"] = "True"
        frame.to_csv(path, index=False)
        cpi_path = self.root / "data/cpi.csv"
        cpi = pd.read_csv(cpi_path)
        cpi = cpi.loc[cpi["year"].ne(2013)]
        cpi.to_csv(cpi_path, index=False)
        with self.assertRaisesRegex(ValueError, "Missing CPI"):
            analysis.build_analysis(self.root)
        cpi.loc[len(cpi)] = [2013, 125, "src"]
        cpi.to_csv(cpi_path, index=False)
        source_path = self.root / "data/sources.json"
        source = json.loads(source_path.read_text(encoding="utf-8"))["src"]
        source_path.write_text('{"src": ' + json.dumps(source) + ', "src": ' + json.dumps(source) + '}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate JSON"):
            analysis.build_analysis(self.root)


class PublishedSampleTests(unittest.TestCase):
    def test_archived_cpi_and_2023_school_sample(self):
        with zipfile.ZipFile(ROOT / "data/raw/shared/cpi-18100005.zip") as archive:
            with archive.open("18100005.csv") as raw:
                rows = csv.DictReader(line.decode("utf-8-sig") for line in raw)
                matched = [r for r in rows if r["REF_DATE"] == "2023" and r["GEO"] == "Alberta"
                           and r["Products and product groups"] == "All-items" and r["UOM"] == "2002=100"]
        self.assertEqual(len(matched), 1)
        self.assertEqual(float(matched[0]["VALUE"]), 164.1)
        rows = analysis.build_analysis(ROOT)["per_learner"].set_index(["series_id", "year"])
        row = rows.loc[("k12_operating_expenses", 2023)]
        self.assertEqual(row["amount_m"], 8463.238670)
        self.assertEqual(row["learners"], 726625)
        self.assertAlmostEqual(row["real_per_learner"], 8463.238670 * 127.1 / 164.1 * 1_000_000 / 726625)
        grants = rows.loc[("k12_operating_grants", 2023)]
        self.assertEqual(grants["amount_m"], 7663.506403)
        self.assertEqual(grants["learners"], 726625)
        self.assertAlmostEqual(grants["real_per_learner"], 7663.506403 * 127.1 / 164.1 * 1_000_000 / 726625)

    def test_postsec_subset_is_distinct_from_system_grants(self):
        result = analysis.build_analysis(ROOT)
        rows = result["per_learner"].set_index(["series_id", "year"])
        for year, expense_m, fle, cpi in (
            (2023, 502.428, 26056.497, 164.1),
            (2024, 540.755, 27463.219, 168.9),
        ):
            subset = rows.loc[("postsec_operating_expenses", year)]
            self.assertEqual(subset["coverage_id"], "postsec_undergrad3")
            self.assertEqual(subset["learner_unit"], "FLE")
            self.assertEqual(subset["amount_m"], expense_m)
            self.assertEqual(subset["learners"], fle)
            self.assertAlmostEqual(subset["real_per_learner"], expense_m * 127.1 / cpi * 1_000_000 / fle)
            self.assertEqual(subset["gap_reason"], "")
            system = rows.loc[("postsec_operating_grants", year)]
            self.assertEqual(system["coverage_id"], "alberta_public20_excluding_banff")
            self.assertTrue(math.isnan(system["real_per_learner"]))
            self.assertTrue(system["gap_reason"])
        self.assertEqual(rows.loc[("postsec_operating_grants", 2024), "amount_m"], 2085.226)
        self.assertTrue(result["delivery"].empty)


if __name__ == "__main__":
    unittest.main()
