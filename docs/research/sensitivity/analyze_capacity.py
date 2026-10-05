"""Reproduce multiplicative financial drivers and explicit capacity scenarios."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from report_analysis import load_current_data

hist, latest, _ = load_current_data()
old = hist[hist.year <= 2021]
a, b = old.iloc[0], old.iloc[-1]
c, d, e = latest.iloc[0], latest.iloc[1], latest.iloc[2]

def decompose(total0, total1, pupils0, pupils1, prices0, prices1):
    totals = total1 / total0
    pupils = pupils1 / pupils0
    prices = prices1 / prices0
    real = totals / pupils / prices
    return {'total_nominal_growth': totals - 1, 'pupil_growth': pupils - 1,
            'school_year_cpi_growth': prices - 1, 'real_per_student_growth': real - 1,
            'identity': '(1+total growth)/(1+pupil growth)/(1+CPI growth)-1'}

result = {
  'historical_2016_17_to_2021_22': decompose(a.amount_m,b.amount_m,a.learners,b.learners,a.cpi_school_year,b.cpi_school_year),
  'allocations_2024_25_to_2025_26': decompose(c.operational_allocation_cad,d.operational_allocation_cad,c.enrolment_headcount,d.enrolment_headcount,c.cpi_school_year,d.cpi_school_year),
  'illustrative_100_dollars_per_student_cad': float(d.enrolment_headcount*100),
  '2026_27_scenarios': []
}
cohort = json.loads((Path(__file__).resolve().parents[1]/'refresh-finance/comparative79_reviewed_summary.json').read_text())
x,y=cohort['prior'],cohort['current']
result['reported_expenses_79_authorities_2023_24_to_2024_25']=decompose(x['expenses_excluding_amortization_cad'],y['expenses_excluding_amortization_cad'],x['headcount'],y['headcount'],float(x['cpi_mean']),float(y['cpi_mean']))
result['reported_expenses_79_authorities_2023_24_to_2024_25']['limitation']='Reported expenses only; accounting changes, audit qualification and cohort selection limit resource interpretation.'
funding_growth = e.operational_allocation_cad / d.operational_allocation_cad - 1
for cost_growth in [0.02,0.03,0.04]:
    result['2026_27_scenarios'].append({
        'status':'illustrative break-even scenario; not forecast',
        'total_allocation_growth':float(funding_growth),
        'assumed_cost_growth':cost_growth,
        'maximum_pupil_growth_preserving_resources_per_pupil':float((1+funding_growth)/(1+cost_growth)-1),
        'limitation':'Assumes uniform cost growth and unchanged student needs; local staffing and space may constrain delivery.'})
out = Path(__file__).with_name('capacity_scenarios.json')
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
