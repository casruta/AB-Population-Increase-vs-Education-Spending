"""Build the October2026 reviewed supplement from bounded, source-backed evidence."""
from pathlib import Path
import json
import hashlib
import pandas as pd
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from report_analysis import ROOT, REPORT_STYLE, NAVY, TEAL, GRAY, load_current_data

RESEARCH = ROOT / 'docs/research'

def load_reviewed_evidence():
    def read(path):
        return json.loads((RESEARCH / path).read_text())
    migration = read('migration/reviewed_summary.json')
    outcomes = read('refresh-outcomes/reviewed_summary.json')
    actual = read('refresh-finance/actual2024_25_rollup.json')
    if actual['period'] != '2024-25':
        raise ValueError('Actual period changed: update report labels before admission')
    classes = read('refresh-outcomes/class-size-summary.json')
    cohort = read('refresh-finance/comparative79_reviewed_summary.json')
    records = read('refresh-finance/comparative79_research.json')['records']
    if (cohort['prior_school_year'],cohort['current_school_year']) != ('2023-24','2024-25'):
        raise ValueError('Comparative periods changed: update report labels before admission')
    if cohort['accepted_scope'] != 'reported_expenses_only' or len(records) != cohort['common_authority_count'] or len({r['authority_code'] for r in records}) != len(records):
        raise ValueError('Comparative cohort requires scoped independent acceptance')
    for key,pupils,expenses in [('prior','prior_headcount','comparative_expenses_excluding_amortization_cad'),('current','current_headcount','current_expenses_excluding_amortization_cad')]:
        row = cohort[key]
        if sum(r[pupils] for r in records) != row['headcount'] or sum(r[expenses] for r in records) != row['expenses_excluding_amortization_cad']:
            raise ValueError('Comparative cohort totals mismatch')
        real = row['expenses_excluding_amortization_cad']/row['headcount']*172.2/float(row['cpi_mean'])
        if abs(real-float(row['real_2025_per_student'])) > 1e-7:
            raise ValueError('Comparative cohort real ratio mismatch')
    change = 100*(float(cohort['current']['real_2025_per_student'])/float(cohort['prior']['real_2025_per_student'])-1)
    if abs(change-float(cohort['real_reported_expense_per_student_change_percent'])) > 1e-8:
        raise ValueError('Comparative cohort percent change mismatch')
    rows = read('refresh-finance/actual2024_25_extraction.json')['records']
    if len(rows) != actual['authority_count'] or len({r['authority_code'] for r in rows}) != len(rows):
        raise ValueError('Actual extraction must have one record per admitted authority')
    for row in rows:
        if row['status'] != 'extracted' or row['total_expenses_cad'] - row['amortization_cad'] != row['expenses_excluding_amortization_cad']:
            raise ValueError('Invalid actual expense record')
    for key in ['total_expenses_cad','amortization_cad','expenses_excluding_amortization_cad']:
        if sum(r[key] for r in rows) != actual[key]:
            raise ValueError(f'Actual rollup mismatch: {key}')
    if sum(r['headcount'] for r in rows) != actual['matched_headcount']:
        raise ValueError('Actual headcount mismatch')
    hist, funding, _ = load_current_data()
    if actual['matched_headcount'] != funding.iloc[0].enrolment_headcount:
        raise ValueError('Actual denominator does not match2024–25 annual sector coverage')
    real = actual['expenses_excluding_amortization_cad'] / actual['matched_headcount'] * 172.2 / float(actual['cpi_mean'])
    if abs(real - float(actual['real2025_expenses_per_student'])) > 1e-7:
        raise ValueError('Actual purchasing-power calculation mismatch')
    if migration['annual_latest']['period_start'] != '2025-07-01' or migration['annual_latest']['period_end'] != '2026-06-30' or migration['age_5_17_latest']['period'] != '2025/2026':
        raise ValueError('Migration period changed: update report labels before admission')
    for key in ['grade9_math','diploma_math']:
        if (outcomes[key]['earlier_period'],outcomes[key]['later_period']) != ('2023-24','2024-25'):
            raise ValueError('Assessment periods changed: update report labels before admission')
    if classes['observation_date'] != '2025-11-24':
        raise ValueError('Class snapshot changed: update report labels before admission')
    for row in migration['annual_all_age']:
        international = row['Immigrants'] - row['Net emigration'] + row['Net non-permanent residents']
        net = international + row['Net interprovincial migration']
        if international != row['Net international migration'] or net != row['Total net migration'] or net + row['Natural increase'] != row['population_end'] - row['population_start']:
            raise ValueError('Migration stock-flow identity failed')
    for row in migration['age_5_17_trend']:
        international = row['Immigrants'] - row['Net emigration'] + row['Net non-permanent residents']
        if international != row['Net international migration'] or international + row['Net-migration'] != row['Total net migration']:
            raise ValueError('Child-age migration identity failed')
    for key in ['grade9_math','grade9_language_arts','diploma_math','diploma_language_arts','completion_5year']:
        row = outcomes[key]
        if abs(row['later'] - row['earlier'] - row['change_pp']) > 1e-8:
            raise ValueError('Outcome change must use percentage points')
    source = outcomes['source']
    if hashlib.sha256((ROOT / source['local_pdf']).read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('Assessment source checksum mismatch')
    for row in classes['grade_bands'].values():
        if row['class_records'] != row['disclosed_records'] + row['suppressed_under10'] or abs(100*row['over30_records']/row['class_records']-row['over30_percent_of_all_included_records']) > 1e-8:
            raise ValueError('Class-record denominator mismatch')
    return {'migration':migration,'outcomes':outcomes,'actual':actual,'classes':classes,'cohort':cohort}

@plt.rc_context(REPORT_STYLE)
def build_extended_report(destination):
    destination = Path(destination)
    plots = destination / 'plots'; plots.mkdir(parents=True,exist_ok=True)
    tables = destination / 'budget_data'; tables.mkdir(parents=True,exist_ok=True)
    reviewed = load_reviewed_evidence()
    hist, funding, _ = load_current_data()
    old = hist[hist.year<=2021]
    cohort = reviewed['cohort']
    def save(fig,name):
        fig.savefig(plots / f'{name}.png',dpi=170)
        fig.savefig(plots / f'{name}.svg',metadata={'Date':None})
        plt.close(fig)
    fig = Figure(figsize=(9.8,6.4))
    left,right = fig.subplots(1,2)
    fig.subplots_adjust(left=.08,right=.97,bottom=.35,top=.78,wspace=.34)
    fig.text(.03,.96,'Reported expenses fell; later allocations rose',fontsize=17,weight='bold')
    fig.text(.03,.905,'Alberta schools • dollars per student, adjusted to 2025 purchasing power',fontsize=11)
    for ax,values,labels,title in [
        (left,[float(cohort['prior']['real_2025_per_student']),float(cohort['current']['real_2025_per_student'])],['2023–24','2024–25'],f"79 continuing authorities: {float(cohort['real_reported_expense_per_student_change_percent']):.1f}%"),
        (right,[funding.iloc[0].real_2025_per_student,funding.iloc[1].real_2025_per_student],['2024–25','2025–26'],f"Revised allocations: {100*(funding.iloc[1].real_2025_per_student/funding.iloc[0].real_2025_per_student-1):+.1f}%")]:
        ax.bar([0,1],values,color=[GRAY,TEAL],width=.55)
        ax.set_title(title,loc='left',fontsize=12,pad=16)
        ax.set_xticks([0,1],labels);ax.set_ylim(0,16500)
        ax.set_yticks([0,5000,10000,15000]);ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'${x:,.0f}'))
        ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True);ax.tick_params(length=0)
        for i,value in enumerate(values):ax.text(i,value+350,f'${value:,.0f}',ha='center',fontsize=13,weight='bold')
    actual=reviewed['actual']
    fig.text(.03,.23,f"Latest reconstructed actual level (2024–25, 83 authorities): ${float(actual['real2025_expenses_per_student']):,.0f} per student",fontsize=11,weight='bold')
    fig.text(.03,.18,'Actuals include accounting restatements and Valhalla’s qualified audit; this is not a harmonized resource trend.',fontsize=10)
    fig.text(.03,.125,'Expenses exclude amortization and include all authority funding sources. Allocations are provincial funding.',fontsize=10,color=GRAY)
    fig.text(.03,.065,'Public, separate, francophone and charter authorities; ECS included; Lloydminster excluded.\n2025–26 source count is preliminary and labelled “as of December 2025”.',fontsize=10,color=GRAY)
    fig.text(.03,.025,'Sources: Alberta authority statements and allocations; Statistics Canada school-year CPI. Verified 5 October 2026.',fontsize=10,color=GRAY)
    save(fig,'funding_and_actuals')
    trend=reviewed['migration']['age_5_17_trend']
    fig = Figure(figsize=(9.8,5.8)); ax=fig.subplots()
    fig.subplots_adjust(left=.09,right=.96,bottom=.28,top=.77)
    fig.text(.03,.95,'Net migration of children remains positive',fontsize=18,weight='bold')
    fig.text(.03,.89,'Alberta • ages 5–17 at start-year July 1 • demographic estimates, not enrolment',fontsize=11)
    international=[r['Net international migration'] for r in trend]
    interprov=[r['Net-migration'] for r in trend]
    positions=list(range(len(trend)))
    ax.bar(positions,international,color=TEAL,label='Net international migration',width=.58)
    ax.bar(positions,interprov,bottom=international,color='#70449B',label='Net interprovincial migration',width=.58)
    ax.set_xticks(positions,[r['period'].replace('/','–') for r in trend]);ax.set_ylim(0,36000)
    ax.set_yticks([0,10000,20000,30000]);ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x/1000:.0f}k'))
    ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True);ax.tick_params(length=0)
    for i,row in enumerate(trend):ax.text(i,row['Total net migration']+700,f"{row['Total net migration']:,}",ha='center',fontsize=11)
    ax.legend(frameon=False,loc='upper left',fontsize=10)
    fig.text(.03,.175,'Net international migration includes permanent-resident admissions, net emigration and NPR changes.',fontsize=10,color=GRAY)
    fig.text(.03,.11,'July–June periods; 2025–26 preliminary. Ages 5–17 exclude younger ECS pupils and students 18+.\nThese estimates do not replace local enrolment and assessed-needs records.',fontsize=10,color=GRAY)
    fig.text(.03,.04,'Source: Statistics Canada Tables 17-10-0014-01 and 17-10-0015-01.\nSeptember 23, 2026 vintage; earlier years use the same revisions.',fontsize=10,color=GRAY)
    save(fig,'migration_demand')
    pd.DataFrame(trend).to_csv(tables/'migration_age_5_17.csv',index=False)
    (tables/'actual2024_25.json').write_text(json.dumps(actual,indent=2)+'\n')
    return reviewed
