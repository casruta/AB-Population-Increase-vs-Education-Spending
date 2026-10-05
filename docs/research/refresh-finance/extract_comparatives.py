"""Research-only current/prior expense comparison for unchanged authority cohort.
Does not extend canonical trend or silently fill missing-authority finances with zero.
"""
from pathlib import Path
from decimal import Decimal as D
import csv,json,re
from reconcile import ROOT,OUT,cpi
from extract_actuals import NUM,amount
records=json.loads((OUT/'actual2024_25_extraction.json').read_text())['records']
en=list(csv.DictReader((ROOT/'data/staging/k12/k12_authority_enrolment.csv').open()))
old={r['authority_code']:r for r in en if r['year']=='2023' and r['included']=='True'}
new={r['authority_code']:r for r in records}
common=set(old)&set(new);rows=[]
for code in sorted(common):
 r=new[code];path=ROOT/f"work/finance-downloads/actual2024-25/{r['index']:02}.txt";pages=path.read_text().split('\f');page=pages[r['schedule_pdf_page']-1];lines=page.splitlines()
 line34=next(t for t in lines if re.search(r'\(34\)\s+TOTAL EXPENSES',t));matches=list(NUM.finditer(line34[line34.find('TOTAL EXPENSES')+len('TOTAL EXPENSES'):]))
 offset=line34.find('TOTAL EXPENSES')+len('TOTAL EXPENSES');right=offset+matches[-1].end();prior_total=amount(matches[-1].group());prior=[]
 for n in range(24,29):
  line=next(t for t in lines if re.search(rf'\({n}\)\s+Amortization',t));m=[m for m in NUM.finditer(line) if abs(m.end()-right)<=3]
  assert len(m)<=1
  # Current-total column's right edge forms prior column's left boundary.
  boundary=offset+matches[-2].end()+2
  if m:val=amount(m[0].group());blank=False
  else:
   assert line[boundary:].strip() in ['','$'],f'Unexpected nonnumeric prior value{line[boundary:]}'
   val=0;blank=True
  prior.append({'row':n,'cad':val,'blank_prior_cell_treated_as_zero':blank,'source_line':line})
 net=prior_total-sum(x['cad'] for x in prior)
 rows.append({'authority_code':code,'name':r['name'],'current_headcount':r['headcount'],'prior_headcount':int(old[code]['learners']),'current_expenses_excluding_amortization_cad':r['expenses_excluding_amortization_cad'],'comparative_total_expenses_cad':prior_total,'comparative_amortization_cad':sum(x['cad'] for x in prior),'comparative_expenses_excluding_amortization_cad':net,'prior_components':prior,'schedule_pdf_page':r['schedule_pdf_page'],'source_sha256':r['sha256']})
_,monthly=cpi(False)
def calc(y,amount_cad,count):
 months=[f'{y}-{m:02}' for m in range(9,13)]+[f'{y+1}-{m:02}' for m in range(1,9)];avg=sum(monthly[m] for m in months)/D(12)
 return {'headcount':count,'expenses_excluding_amortization_cad':amount_cad,'cpi_mean':str(avg),'real_2025_per_student':str(D(amount_cad)/D(count)*D('172.2')/avg)}
a=calc(2023,sum(r['comparative_expenses_excluding_amortization_cad'] for r in rows),sum(r['prior_headcount'] for r in rows));b=calc(2024,sum(r['current_expenses_excluding_amortization_cad'] for r in rows),sum(r['current_headcount'] for r in rows))
result={'admission_status':'Independently reviewed for narrow reported-expense comparison only; not a stable-basis resource measure, province-wide total or historical-series extension','common_authority_count':len(rows),'missing_current_authorities':[old[c] for c in sorted(set(old)-set(new))],'new_current_authorities':[{'authority_code':c,'name':new[c]['name'],'headcount':new[c]['headcount']} for c in sorted(set(new)-set(old))],'prior_period_2023_24':a,'current_period_2024_25':b,'common_cohort_real_change_percent':str((D(b['real_2025_per_student'])/D(a['real_2025_per_student'])-1)*100),'records':rows,'limitations':['This cohort omits four new2024authorities and one former2023authority; not a provincial total.','Priorcomparatives are reported in current2024-25statements; restatements and accountingchanges may affect comparison.','Northland final2023individualaudit signed2025-07-23 resolves originalcombined draft; comparativeexpense andamortization exactlymatch finalsource.','Valhalla auditqualification remains.']}
(OUT/'comparative79_research.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['records','missing_current_authorities','new_current_authorities']},indent=2))
