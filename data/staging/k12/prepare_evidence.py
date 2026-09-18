"""Prepare auditable K-12 evidence from archived official source observations.

This is source preparation, not the maintained publication pipeline.
Manual financial readings are retained as individual components, not only net results.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import openpyxl
from pypdf import PdfReader

OUT = Path(__file__).resolve().parent
RAW = OUT.parents[1] / 'raw' / 'k12'
REPO = OUT.parents[2]
sources = {}

def write_csv(name, rows):
    with (OUT / name).open('w', newline='', encoding='utf8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def source(year, kind):
    meta = json.loads((RAW / f'metadata-{year}-{year+1}.json').read_text(encoding='utf-8-sig'))
    resource = next(r for r in meta['resources'] if r['name'].strip().lower() == kind.lower())
    sid = f'k12_{year}_{kind.lower().replace(" ", "_")}'
    path = RAW / f'{year}-{year+1}-{resource["url"].rsplit("/",1)[-1]}'
    sources[sid] = dict(title=meta['title'] + ': ' + resource['name'], url=resource['url'],
        release_date=meta['issuedate'], release_date_basis='Official catalogue issuedate; historical original-release timing not independently reconstructed', retrieved_date='2026-09-18',
        raw_file=path.relative_to(REPO).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        coverage_notes=meta['notes'], extraction_notes='PDF page 1; exact row and column in component table. Current-year actual as originally compiled; later restated comparators retained separately.')
    return sid, path

# Columns: statement revenue from GoA (education + other GoA before 2018),
# total expenses, cash-flow amortization, reported total-expense budget.
observations = {
2012: (6152157533+39643931,6791950650,292984714,6747206409),
2013: (6257310643+39174759,6944521778,297071704,6811246304),
2014: (6516337371+39366029,7228040463,305046656,7114845666),
2015: (6821409566+37198551,7538460294,316480964,7435912007),
2016: (6938219068+33922358,7740445060,338472018,7699249195),
2017: (7181611812+37212704,7964542426,385384207,7918526698),
2018: (7288910958,8097032842,409591407,8090714675),
2019: (7059125323,7757851883,426686923,8166752612),
2020: (7442290617,7895651070,435043678,8074866321),
2021: (7484308299,8169673854,450782523,8107654944),
2022: (7649105742,8476086027,465646709,8257719106),
2023: (8050631396,8955338793,492100123,8840729106),
}
# Government-source capital revenue recognized. 2012 is not split by origin;
# 2013's catalogue links a 2012/13 schedule. Neither is admitted.
capital_amortization = {
2014:(220336818,3209846),2015:(228559413,2087423),
2016:(243751467,6389636),2017:(271816728,20865723),
2018:(45070003,268684659),2019:(32067956,297473929),
2020:(46432898,296518507),2021:(56625370,305984760),
2022:(64494132,302468171),2023:(71594701,301140808),
}
# Signed recognised revenue from unspent capital contributions; positive =
# revenue recognised (deduct), negative = reversal (add back).
udcc_revenue = {2018:(-838788,249028),2019:(523337,359929),
2020:(874691,544069),2021:(1174198,257833),
2022:(1166132,116819),2023:(827050,4945019)}
interschool = {2018:8096532,2019:6765099,2020:7461200,
2021:7487674,2022:8180964,2023:8617415}

components=[]; spending=[]; budgets=[]; restated=[]
for year,(gov,expenses,amortization,budget) in observations.items():
    period=f'{year}-{str(year+1)[-2:]}'
    op_sid, op_path = source(year,'Statement of operations')
    cash_sid, cash_path = source(year,'Statement of cash flows')
    op_text = PdfReader(op_path).pages[0].extract_text()
    cash_text = PdfReader(cash_path).pages[0].extract_text()
    assert f'{expenses:,}' in op_text and f'{budget:,}' in op_text
    assert f'{amortization:,}' in cash_text
    def component(name,value,sid,locator):
        components.append(dict(year=year,period=period,component=name,amount_cad=value,source_id=sid,locator=locator))
    component('statement_goa_revenue',gov,op_sid,'PDF page 1; Actual current year; Government of Alberta (before 2018: Alberta Education + Other Government of Alberta)')
    component('total_expenses',expenses,op_sid,'PDF page 1; Actual current year; Total expenses')
    component('total_amortization',amortization,cash_sid,'PDF page 1; Actual current year; Total amortization expense / Amortization of tangible capital assets')
    segment = ('k12_complete_pre_aro' if year <= 2021 else
               'k12_2022_without_valhalla_aro' if year == 2022 else 'k12_2023_complete_aro_draft_northland')
    spending.append(dict(observation_id=f'k12_expenses_{year}',series_id='k12_operating_expenses',year=year,period=period,
        amount_m=(expenses-amortization)/1e6,status='actual',budget_basis='',segment=segment,
        source_id=op_sid,locator='Total expenses less total amortization; exact source components in k12_components.csv',selected=True))
    budgets.append(dict(year=year,period=period,amount_cad=budget,measure='total_expenses_including_amortization',
        status='budget',budget_basis='unknown',source_id=op_sid,locator='PDF page 1; Budget current year; Total expenses',admitted=False,
        reason='Statement labels Budget; original/adopted vs revised is not established. No comparable budget amortization extracted.'))
    if year in capital_amortization:
        capital_kind='Schedule of capital revenue' if year<2018 else 'Schedule of deferred contributions'
        cap_sid,cap_path = source(year,capital_kind)
        cap_text='\n'.join(p.extract_text() for p in PdfReader(cap_path).pages)
        norm = re.sub(r'(?<=\d)[ ,\n]+(?=\d)','',cap_text)
        for name,value in zip(['capital_recognition_education','capital_recognition_other_goa'],capital_amortization[year]):
            assert str(value) in norm
            component(name,value,cap_sid,'PDF page 1; Capital revenue recognized (2014-17) / SDCC-EDCC amounts recognized as revenue (2018+); Alberta Education or Total Other GoA Ministries')
        direct=(0,0)
        if year>=2018:
            direct=udcc_revenue[year]
            for name,value in zip(['udcc_revenue_education','udcc_revenue_other_goa'],direct):
                assert str(abs(value)) in norm
                component(name,value,cap_sid,'PDF page 1; UDCC section; transfer (to) grant/donation revenue; Education / Total Other GoA. Sign converted to recognised revenue.')
            prog_sid,prog_path=source(year,'Schedule of program operations')
            ptext=PdfReader(prog_path).pages[0].extract_text()
            assert f'{interschool[year]:,}' in ptext
            component('interschool_revenue_in_goa',interschool[year],prog_sid,'PDF page 1; Revenue row Other Alberta school authorities; current-year TOTAL')
        grant=gov-sum(capital_amortization[year])-sum(direct)-interschool.get(year,0)
        grant_segment = (('k12_grants_pre_2018_reclassification' if year<2018 else 'k12_grants_2018_2021') if year<=2021 else segment)
        spending.append(dict(observation_id=f'k12_grants_{year}',series_id='k12_operating_grants',year=year,period=period,
            amount_m=grant/1e6,status='actual',budget_basis='',segment=grant_segment,source_id=op_sid,
            locator='GoA revenue less interschool revenue and GoA capital recognition (spent and unspent); exact source components in k12_components.csv',selected=True))

enrolment=[]; authorities=[]
emeta=json.loads((RAW/'enrolment-metadata.json').read_text())['result']
for resource in emeta['resources']:
    if 'authority' not in resource['name']: continue
    year=int(resource['name'][:4]); path=RAW/resource['url'].rsplit('/',1)[-1]
    sid=f'k12_enrolment_{year}'
    sources[sid]=dict(title=resource['name'],url=resource['url'],release_date=resource['created'][:10],release_date_basis='Portal resource-created timestamp; upload date proxy, not independently verified original publication date',retrieved_date='2026-09-18',
        raw_file=path.relative_to(REPO).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        coverage_notes='ECS to grade12 headcount by authority; see explicit included/excluded rows in k12_authority_enrolment.csv',
        extraction_notes='Read cached numeric Total values; filter Public/Separate/Francophone/Charter and exclude Lloydminster3170/4870; for2022 exclude Valhalla0224.')
    sheet=openpyxl.load_workbook(path,data_only=True).active
    rows=list(sheet.values); header=list(rows[0]); idx={v:i for i,v in enumerate(header)}
    ccat=idx['School Authority Category'];ccode=idx['School Authority Code'];cname=idx['School Authority Name'];ctotal=idx['Total']
    count=0;selected_rows=[];school_codes=[]
    for n,row in enumerate(rows[1:],2):
        if row[ccat] not in {'Public','Separate','Francophone','Charter'}:continue
        code=str(row[ccode]).zfill(4); value=row[ctotal]
        assert isinstance(value,(int,float)) and value>=0
        assert sum(v or 0 for v in row[idx['ECS']:ctotal])==value
        exclude=code in {'3170','4870'} or (year==2022 and code=='0224')
        reason='Lloydminster school board excluded from financial rollup' if code in {'3170','4870'} else 'Valhalla financial statements absent from 2022-23 rollup' if exclude else ''
        locator=f"'{sheet.title}'!{openpyxl.utils.get_column_letter(ctotal+1)}{n}"
        authorities.append(dict(year=year,authority_code=code,authority_name=row[cname].strip(),category=row[ccat],learners=int(value),included=not exclude,exclusion_reason=reason,source_id=sid,locator=locator))
        if not exclude: count+=value;selected_rows.append(n);school_codes.append(code)
    assert len(school_codes)==len(set(school_codes))
    enrolment.append(dict(denominator_id='k12_matched_headcount',year=year,period=f'{year}-{str(year+1)[-2:]}',learners=int(count),unit='headcount',
        status='preliminary' if 'Preliminary' in resource['name'] else 'final',coverage_id='k12_without_valhalla' if year==2022 else 'k12_alberta_reporting_authorities',
        source_id=sid,locator=f"'{sheet.title}': sum Total column for admitted authority rows; row-by-row cells in k12_authority_enrolment.csv"))

roster_checks=[]
for year in range(2016,2024):
    meta_path=RAW/(f'summary-{year}-{year+1}-metadata.json' if year<2023 else 'summary2024-metadata.json')
    meta=json.loads(meta_path.read_text())['result']
    resource=next(r for r in meta['resources'] if 'expenses by program' in r['name'].lower())
    path=RAW/((f'{year}-{year+1}-' if year<2023 else '')+resource['url'].rsplit('/',1)[-1])
    text='\n'.join(p.extract_text() for p in PdfReader(path).pages)
    financial_codes=set(re.findall(r'^\s*(\d{4})\s+',text,re.M))-{str(year),str(year+1)}
    enrolment_codes={r['authority_code'] for r in authorities if r['year']==year and r['included']}
    assert financial_codes==enrolment_codes, (year,financial_codes^enrolment_codes)
    sid=f'k12_authority_roster_{year}'
    sources[sid]=dict(title=meta['title']+': '+resource['name'],url=resource['url'],release_date=meta['issuedate'],
        release_date_basis='Official catalogue issuedate',retrieved_date='2026-09-18',raw_file=path.relative_to(REPO).as_posix(),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),coverage_notes=meta['notes'],
        extraction_notes='Both PDF pages: Juris.Code rows; exact equality to admitted enrolment authority codes verified.')
    roster_checks.append(dict(year=year,financial_authorities=len(financial_codes),enrolment_authorities=len(enrolment_codes),exact_code_match=True,source_id=sid))
(OUT/'roster_checks.json').write_text(json.dumps(roster_checks,indent=2))
write_csv('k12_components.csv',components)
write_csv('k12_spending.csv',sorted(spending,key=lambda r:(r['series_id'],r['year'])))
write_csv('k12_reported_budgets_not_admitted.csv',budgets)
write_csv('k12_enrolment.csv',sorted(enrolment,key=lambda r:r['year']))
write_csv('k12_authority_enrolment.csv',sorted(authorities,key=lambda r:(r['year'],r['authority_code'])))
(OUT/'k12_sources.json').write_text(json.dumps(sources,indent=2),encoding='utf8')
print('Financial observations',len(spending),'source components',len(components),'enrolment years',len(enrolment))
for row in sorted(enrolment,key=lambda r:r['year']): print(row['period'],row['learners'])
