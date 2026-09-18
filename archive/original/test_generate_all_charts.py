"""Regression tests for the integrated chart data and headline values."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

import generate_all_charts as charts


class IntegratedDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frame = charts.load_data()
        cls.population = charts.load_population_series()
        cls.metrics = charts.headline_metrics(cls.frame)

    def test_population_overview_has_complete_study_period(self) -> None:
        self.assertEqual(
            self.population["Year"].tolist(), list(range(2012, 2026))
        )
        self.assertTrue((self.population["Population"] > 0).all())

    def test_years_are_sorted_and_sparse_gap_is_explicit(self) -> None:
        self.assertEqual(self.frame["Year"].tolist(), [2012, 2013, 2023, 2024, 2025])
        self.assertEqual(
            set(range(2014, 2023)).intersection(self.frame["Year"]), set()
        )

    def test_totals_equal_component_budgets(self) -> None:
        pd.testing.assert_series_equal(
            self.frame["Total_M"],
            self.frame["K12_M"] + self.frame["PostSec_M"],
            check_names=False,
        )

    def test_spending_rows_have_auditable_official_sources(self) -> None:
        spending = pd.read_csv(charts.SCRIPT_DIR / "spending_data.csv")
        self.assertFalse(spending[["Source_Detail", "Source_URL"]].isnull().any().any())
        self.assertTrue(
            spending["Source_URL"].str.startswith(
                "https://open.alberta.ca/", na=False
            ).all()
        )

    def test_baseline_and_budget_status_are_explicit(self) -> None:
        baseline = self.frame.set_index("Year").loc[2012]
        endpoint = self.frame.set_index("Year").loc[2025]
        self.assertAlmostEqual(baseline["CPI_Deflator"], 1.0)
        self.assertEqual(endpoint["Budget_Status"], "Budget-plan figure")
        self.assertEqual(baseline["Budget_Status"], "Budget-plan figure")

    def test_headline_growth_metrics(self) -> None:
        expected = {
            "cpi_inflation_pct": 35.4052,
            "population_growth_pct": 30.4978,
            "k12_nominal_growth_pct": 59.9450,
            "postsec_nominal_growth_pct": 132.3179,
            "total_nominal_growth_pct": 82.8224,
            "k12_real_growth_pct": 18.1232,
            "postsec_real_growth_pct": 71.5724,
            "total_real_growth_pct": 35.0187,
            "k12_real_per_capita_growth_pct": -9.4826,
            "postsec_real_per_capita_growth_pct": 31.4752,
            "total_real_per_capita_growth_pct": 3.4641,
        }
        self.assertEqual(set(self.metrics), set(expected))
        for name, value in expected.items():
            with self.subTest(metric=name):
                self.assertAlmostEqual(self.metrics[name], value, places=3)

    def test_duplicate_spending_year_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "spending.csv"
            source = pd.read_csv(charts.SCRIPT_DIR / "spending_data.csv")
            pd.concat([source, source.iloc[[0]]]).to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "duplicate years"):
                charts.load_data(spending_path=path)

    def test_missing_cpi_year_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cpi.csv"
            source = pd.read_csv(charts.SCRIPT_DIR / "cpi_data.csv")
            source[source["Year"] != 2025].to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "no values for years"):
                charts.load_data(cpi_path=path)


if __name__ == "__main__":
    unittest.main()
