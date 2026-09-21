"""Regression checks for matched funding, school-year inflation, and source snapshots."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd
import report_analysis as report


class CurrentReportTests(unittest.TestCase):
    def test_matched_scope_and_no_forecast_denominator(self):
        hist, latest, cpi = report.load_current_data()
        self.assertEqual(latest.operational_allocation_cad.tolist(), [7716613874, 8361644972, 8896073124])
        self.assertEqual(latest.enrolment_headcount.iloc[:2].tolist(), [748521, 754880])
        self.assertTrue(pd.isna(latest.allocation_per_student_cad.iloc[2]))
        self.assertTrue(pd.isna(latest.real_2025_per_student.iloc[2]))
        self.assertAlmostEqual(latest.allocation_per_student_cad.iloc[1], 11076.787001907587)
        old = hist[hist.year <= 2021]
        self.assertAlmostEqual(old.real_2025_per_student.iloc[-1]/old.real_2025_per_student.iloc[0]-1, -0.12381098205796427)
        self.assertTrue((cpi.months == 12).all())

    def test_reject_duplicate_or_missing_cpi_month(self):
        monthly = pd.read_csv(report.LATEST / 'alberta_monthly_cpi.csv')
        with self.assertRaisesRegex(ValueError, 'unique'):
            report.school_year_cpi(pd.concat([monthly, monthly.iloc[:1]], ignore_index=True))
        with self.assertRaisesRegex(ValueError, '12 unique'):
            report.school_year_cpi(monthly.iloc[1:])
        corrupted = monthly.copy()
        corrupted.loc[0, 'GEO'] = 'Canada'
        with self.assertRaisesRegex(ValueError, 'Alberta'):
            report.school_year_cpi(corrupted)

    def test_historical_mismatch_never_produces_ratio(self):
        spending = pd.read_csv(report.ROOT / 'data/spending.csv')
        enrolment = pd.read_csv(report.ROOT / 'data/enrolment.csv')
        cpi = report.school_year_cpi(pd.read_csv(report.LATEST / 'alberta_monthly_cpi.csv'))
        row = enrolment[(enrolment.denominator_id == 'k12_matched_headcount') & (enrolment.year == 2016)].index[0]
        for field, value in [('eligible', False), ('period', '2017-18'), ('coverage_id', 'other'), ('unit', 'FTE'), ('status', 'preliminary')]:
            with self.subTest(field=field):
                changed = enrolment.copy()
                changed.loc[row, field] = value
                with self.assertRaises(ValueError):
                    report.matched_historical_spending(spending, changed, cpi)
        changed = spending.copy()
        changed.loc[(changed.series_id == 'k12_operating_expenses') & (changed.year == 2016), 'status'] = 'budget'
        with self.assertRaisesRegex(ValueError, 'actual'):
            report.matched_historical_spending(changed, enrolment, cpi)

    def test_current_periods_cannot_drift(self):
        latest = pd.DataFrame(json.loads((report.LATEST / 'school_funding_inputs.json').read_text()))
        for changed in [latest.iloc[:2], pd.concat([latest, latest.iloc[:1]], ignore_index=True), latest.assign(year=latest.year+1)]:
            with self.assertRaisesRegex(ValueError, 'exactly years'):
                report.validate_current_periods(changed)
        latest.loc[0, 'school_year'] = '2023-24'
        with self.assertRaisesRegex(ValueError, 'labels'):
            report.validate_current_periods(latest)

    def test_source_snapshots(self):
        manifest = json.loads((report.LATEST / 'source_manifest.json').read_text())
        for relative, expected in manifest['checked_files_sha256'].items():
            with self.subTest(path=relative):
                self.assertEqual(hashlib.sha256((report.ROOT / relative).read_bytes()).hexdigest(), expected)

    def test_outputs_and_headline_arithmetic(self):
        with tempfile.TemporaryDirectory() as directory:
            headline = report.build_current_report(directory)
            self.assertAlmostEqual(headline['current_real_change'], 0.04643069635463304, places=10)
            self.assertAlmostEqual(headline['broad2026_per_resident'], 19388000000/5057077)
            for name in ['historical_spending.png', 'historical_spending.svg', 'recent_funding.png', 'recent_funding.svg', 'education_evidence.csv', 'school_year_cpi.csv']:
                self.assertGreater((Path(directory)/('plots' if name.endswith(('.png', '.svg')) else 'budget_data')/name).stat().st_size, 100)
            evidence = pd.read_csv(Path(directory)/'budget_data/education_evidence.csv')
            future = evidence[(evidence.period == '2026-27') & (evidence.measure == 'School operational allocation')].iloc[0]
            self.assertTrue(pd.isna(future.nominal_per_student))
            broad = evidence[evidence.measure == 'Consolidated education function expense']
            self.assertTrue(broad.students.isna().all())


if __name__ == '__main__':
    unittest.main()
