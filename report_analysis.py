"""Offline reproduction of the September 2026 evidence brief.

Current revised grants remain separate from the legacy audited-expense series.
All monetary inputs are CAD. CPI is Alberta all-items, September through August.
"""
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import Figure

ROOT = Path(__file__).resolve().parent
LATEST = ROOT / "data/latest"

NAVY, TEAL, ORANGE, GRAY = '#17324D', '#007F86', '#BC642B', '#51616F'
REPORT_STYLE = {'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
    'axes.spines.right':False,'axes.spines.left':False,'axes.edgecolor':'#C7D0D7',
    'axes.labelcolor':NAVY,'text.color':NAVY,'xtick.color':GRAY,'ytick.color':GRAY,
    'svg.fonttype':'none','savefig.facecolor':'white', 'svg.hashsalt':'alberta-current-report'}

def school_year_cpi(monthly):
    """Reject duplicates and incomplete school years before averaging inflation."""
    if monthly.REF_DATE.duplicated().any():
        raise ValueError("CPI months must be unique")
    if not ((monthly.GEO == "Alberta") & (monthly["Products and product groups"] == "All-items") & (monthly.VECTOR == "v41692327")).all():
        raise ValueError("CPI must be Alberta all-items")
    dates = pd.to_datetime(monthly.REF_DATE, format="%Y-%m", errors="raise")
    frame = monthly.assign(year=dates.dt.year - (dates.dt.month < 9).astype(int))
    rows = []
    for year, group in frame.groupby("year"):
        expected = set(pd.date_range(f"{year}-09-01", periods=12, freq="MS").strftime("%Y-%m"))
        if set(group.REF_DATE) != expected or len(group) != 12:
            raise ValueError(f"School year {year} requires 12 unique September-August months")
        values = pd.to_numeric(group.VALUE, errors="raise")
        if values.isna().any() or (values <= 0).any():
            raise ValueError("CPI values must be positive")
        avg = values.mean()
        rows.append(dict(year=year, cpi_school_year=avg, months=12, deflator_to_2025=172.2/avg))
    return pd.DataFrame(rows)


def matched_historical_spending(spending, enrolment, cpi):
    """Fail closed when a reviewed historical numerator loses its matched denominator."""
    expected_years = list(range(2016, 2024))
    financial = spending[(spending.series_id == "k12_operating_expenses") &
                         (spending.selected == True) & spending.year.isin(expected_years)].copy()
    if sorted(financial.year.tolist()) != expected_years:
        raise ValueError("Historical report requires exactly one selected expense for each year 2016-2023")
    if not financial.status.eq("actual").all():
        raise ValueError("Historical expenses must be actual")
    expected_periods = financial.year.map(lambda y: f"{y}-{(y+1)%100:02d}")
    if not financial.period.eq(expected_periods).all():
        raise ValueError("Historical financial period does not match its year")
    denominator = enrolment[(enrolment.denominator_id == "k12_matched_headcount") &
                            enrolment.year.isin(expected_years)].copy()
    if sorted(denominator.year.tolist()) != expected_years:
        raise ValueError("Historical report requires exactly one denominator per year")
    if not ((denominator.eligible == True) & denominator.unit.eq("headcount") &
            denominator.status.eq("final") & (denominator.learners > 0)).all():
        raise ValueError("Historical denominator must be eligible final positive headcount")
    hist = financial.merge(denominator[["year", "period", "coverage_id", "learners"]],
        on=["year", "period", "coverage_id"], how="left", validate="one_to_one", indicator=True)
    if not hist["_merge"].eq("both").all():
        raise ValueError("Historical denominator period or coverage does not match expenses")
    hist = hist.drop(columns="_merge").merge(cpi, on="year", how="left", validate="one_to_one")
    if hist.deflator_to_2025.isna().any():
        raise ValueError("Historical school-year inflation is missing")
    hist["nominal_per_student"] = hist.amount_m * 1e6 / hist.learners
    hist["real_2025_per_student"] = hist.nominal_per_student * hist.deflator_to_2025
    return hist.sort_values("year")


def validate_current_periods(latest):
    """The reviewed comparison is fixed; a refresh must explicitly update its periods."""
    if sorted(latest.year.tolist()) != [2024, 2025, 2026]:
        raise ValueError("Current report requires exactly years 2024, 2025 and 2026")
    if not latest.school_year.eq(latest.year.map(lambda y: f"{y}-{(y+1)%100:02d}")).all():
        raise ValueError("Current school-year labels do not match their years")


def load_current_data():
    cpi = school_year_cpi(pd.read_csv(LATEST / "alberta_monthly_cpi.csv"))
    spending = pd.read_csv(ROOT / "data/spending.csv")
    enrolment = pd.read_csv(ROOT / "data/enrolment.csv")
    hist = matched_historical_spending(spending, enrolment, cpi)
    latest = pd.DataFrame(json.loads((LATEST / "school_funding_inputs.json").read_text()))
    validate_current_periods(latest)
    latest["operational_allocation_cad"] = latest.public_allocation_cad - latest.lloydminster_allocation_cad
    latest["enrolment_headcount"] = latest.public_headcount - latest.lloydminster_headcount
    if (latest.operational_allocation_cad <= 0).any() or (latest.enrolment_headcount.dropna() <= 0).any():
        raise ValueError("Matched allocation and enrolment must be positive")
    latest["allocation_per_student_cad"] = latest.operational_allocation_cad / latest.enrolment_headcount
    latest["scope"] = "Public system excluding Lloydminster"
    latest = latest.merge(cpi, on="year", how="left", validate="one_to_one").sort_values("year").reset_index(drop=True)
    latest["real_2025_per_student"] = latest.allocation_per_student_cad * latest.deflator_to_2025
    return hist, latest, cpi


@plt.rc_context(REPORT_STYLE)
def build_current_report(output_dir):
    """Write two PNG/SVG charts and evidence CSV; return reproducible headline ratios."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = output_dir / "plots"
    table_dir = output_dir / "budget_data"
    plot_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)
    hist, latest, cpi = load_current_data()
    old = hist[hist.year <= 2021]
    def chart_save(fig, name):
        fig.savefig(plot_dir/f'{name}.png',dpi=210)
        fig.savefig(plot_dir/f'{name}.svg', metadata={'Date': None})
        plt.close(fig)

    # A common scale and directly labelled endpoints show dollars and purchasing power.
    fig = Figure(figsize=(10.5,4.6))
    ax = fig.subplots()
    fig.subplots_adjust(left=.12,right=.80,bottom=.22,top=.78)
    fig.text(.025,.945,'Actual school spending bought less per student',fontsize=18,weight='bold')
    fig.text(.025,.866,'Alberta public school authorities, 2016-17 to 2021-22',fontsize=12)
    for col, color in [('real_2025_per_student',TEAL),('nominal_per_student',GRAY)]:
        ax.plot(old.year,old[col],color=color,lw=2.8,marker='o',ms=6)
        ax.annotate(f'${old.iloc[0][col]:,.0f}',(2016,old.iloc[0][col]),xytext=(0,12),textcoords='offset points',ha='center',color=color,fontsize=11)
    ax.text(2021.16,old.iloc[-1].real_2025_per_student,
        f'${old.iloc[-1].real_2025_per_student:,.0f}\n2025 dollars',va='center',color=TEAL,weight='bold')
    ax.text(2021.16,old.iloc[-1].nominal_per_student,
        f'${old.iloc[-1].nominal_per_student:,.0f}\nDollars of the day',va='center',color=GRAY)
    ax.set_xlim(2015.75,2021.1); ax.set_ylim(10000,15100)
    ax.set_xticks(old.year,old.period);ax.set_yticks([10000,12000,14000])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'${x:,.0f}'))
    ax.set_ylabel('Expense per student (headcount)',labelpad=10)
    ax.grid(axis='y',alpha=.18);ax.tick_params(axis='both',length=0)
    fig.text(.025,.09,'Expenses exclude amortization; public, separate, francophone and charter authorities; Lloydminster excluded.',fontsize=9,color=GRAY)
    fig.text(.025,.045,'Sources: Alberta combined school financial statements and authority enrolment; Statistics Canada school-year CPI.',fontsize=9,color=GRAY)
    chart_save(fig,'historical_spending')

    # Current funding is deliberately separate from historical expense.
    fig = Figure(figsize=(10.5,4.6))
    axes = fig.subplots(1, 2)
    fig.subplots_adjust(left=.085,right=.965,bottom=.27,top=.71,wspace=.50)
    fig.text(.025,.945,'Recent operating funding per student increased',fontsize=18,weight='bold')
    fig.text(.025,.863,'Matched Alberta public school authorities; revised allocations, not audited spending',fontsize=11.5)
    for ax,col,title,ylim in [(axes[0],'allocation_per_student_cad','Dollars of the day',(0,13000)),
                             (axes[1],'real_2025_per_student','2025 dollars (inflation adjusted)',(0,13000))]:
        vals = latest.iloc[:2][col]
        ax.bar([0,1],vals,color=[GRAY,TEAL],width=.52)
        ax.set_title(title,loc='left',fontsize=12,pad=20)
        for i,v in enumerate(vals):ax.text(i,v+290,f'${v:,.0f}',ha='center',fontsize=12,weight='bold')
        ax.set_xticks([0,1],['2024-25','2025-26'])
        ax.set_ylim(*ylim);ax.set_xlim(-.6,1.6);ax.set_yticks([0,5000,10000])
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'${x:,.0f}'))
        ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True);ax.tick_params(length=0)
    fig.text(.025,.12,'Per student = operating allocation / student headcount. Lloydminster excluded from both amounts and counts.',fontsize=9,color=GRAY)
    fig.text(.025,.075,'2025-26 enrolment is preliminary; CPI averages September-August, including August 2026.',fontsize=9,color=GRAY)
    fig.text(.025,.03,'Sources: Alberta Budget 2025 and 2026 operational funding schedules, student statistics; Statistics Canada CPI.',fontsize=9,color=GRAY)
    chart_save(fig,'recent_funding')

    records=[]
    for _,r in hist.iterrows():
        records.append(dict(measure='School-authority expenses excluding amortization',period=r.period,status='Reported actual',scope=r.coverage_id,
            amount_cad=r.amount_m*1e6,students=r.learners,residents='',cpi_school_year=r.cpi_school_year,
            nominal_per_student=r.nominal_per_student,real_2025_per_student=r.real_2025_per_student,nominal_per_resident='',source_id=r.source_id))
    for _,r in latest.iterrows():
        records.append(dict(measure='School operational allocation',period=r.school_year,status=r.status,scope=r.scope,
            amount_cad=r.operational_allocation_cad,students=r.enrolment_headcount,residents='',cpi_school_year=r.cpi_school_year,
            nominal_per_student=r.allocation_per_student_cad,real_2025_per_student=r.real_2025_per_student,nominal_per_resident='',source_id=r.funding_url))
    for r in json.loads((LATEST/'fiscal_education_inputs.json').read_text()):
        records.append(dict(measure='Consolidated education function expense', period=r['period'], status=r['status'],
            scope='All education; excludes childcare', amount_cad=r['amount_cad'], students='', residents=r['residents'],
            cpi_school_year='', nominal_per_student='', real_2025_per_student='', nominal_per_resident=r['amount_cad']/r['residents'],
            source_id=r['source_id']))
    pd.DataFrame(records).to_csv(table_dir/'education_evidence.csv',index=False)
    cpi.to_csv(table_dir/'school_year_cpi.csv',index=False)
    fiscal = json.loads((LATEST/"fiscal_education_inputs.json").read_text())
    return dict(current_nominal_per_student=float(latest.iloc[1].allocation_per_student_cad),
        broad2024_total=fiscal[0]["amount_cad"], broad2024_per_resident=fiscal[0]["amount_cad"]/fiscal[0]["residents"],
        broad2026_total=fiscal[1]["amount_cad"], broad2026_per_resident=fiscal[1]["amount_cad"]/fiscal[1]["residents"],
        historical_real_change=old.iloc[-1].real_2025_per_student/old.iloc[0].real_2025_per_student-1,
        current_nominal_change=latest.iloc[1].allocation_per_student_cad/latest.iloc[0].allocation_per_student_cad-1,
        current_real_change=latest.iloc[1].real_2025_per_student/latest.iloc[0].real_2025_per_student-1,
        future_allocation_growth=latest.iloc[2].operational_allocation_cad/latest.iloc[1].operational_allocation_cad-1)
