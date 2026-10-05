"""Extract 2024-25 AFS program-operation expense rows; fail closed on ambiguities.
Requires pdftotext; raw downloads remain under ignored work/finance-downloads.
No automatic admission into historical comparable series.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from decimal import Decimal as D
import csv,json,re,subprocess,sys
from reconcile import ROOT,OUT,P,enrolment,cpi
MAN=json.loads((OUT/'individual_actuals_manifest.json').read_text());WORK=ROOT/'work/finance-downloads/actual2024-25'
NUM=re.compile(r'(?<![\w])\(?-?\d[\d,]*\)?|(?<!\w)-(?!\w)')
def amount(s):
 s=s.strip().replace(',','')
 return 0 if s=='-' else -int(s[1:-1]) if s.startswith('(') else int(s)
def normalize(s):
 s=s.strip().casefold();s=re.sub(r'^the ','',s);s=s.replace('footprints for learning society','footprints for learning');return s
EN=enrolment(P/'enrolment2024_live');roster={normalize(r['name']):r for r in EN['rows'] if r['code'] not in ['3170','4870']}
def extract(r):
 row={k:r[k] for k in ['index','name','url','sha256'] if k in r}
 try:
  assert r['status']=='downloaded',r.get('error')
  en=roster[normalize(r['name'])];row.update(authority_code=en['code'],headcount=en['count'])
  pdf=ROOT/r['file'];txt=pdf.with_suffix('.txt')
  if not txt.exists():subprocess.run(['pdftotext','-layout',str(pdf),str(txt)],check=True,capture_output=True)
  text=txt.read_text();pages=text.split('\f')
  found=[]
  for i,page in enumerate(pages):
   if re.search(r'\(34\)\s+TOTAL EXPENSES',page):found.append((i+1,page))
  assert len(found)==1,f'schedule candidates {len(found)}'
  page_no,page=found[0];lines=page.splitlines()
  line34=next(t for t in lines if re.search(r'\(34\)\s+TOTAL EXPENSES',t))
  # numeric row label excluded; six program cells + current TOTAL + prior TOTAL
  tail=line34[line34.find('TOTAL EXPENSES')+len('TOTAL EXPENSES'):]
  matches=list(NUM.finditer(tail));assert len(matches)==8, f'row34 cells {len(matches)}'
  start=line34.find('TOTAL EXPENSES')+len('TOTAL EXPENSES')
  right=start+matches[-2].end();total=amount(matches[-2].group())
  program_sum=sum(amount(t.group()) for t in matches[:6]);assert abs(program_sum-total)<=1,f'program sum{program_sum} vs{total}'
  components=[]
  for n in range(24,29):
   candidates=[t for t in lines if re.search(rf'\({n}\)\s+Amortization',t)]
   assert len(candidates)==1,f'row{n} candidates{len(candidates)}'
   line=candidates[0];cands=[m for m in NUM.finditer(line) if abs(m.end()-right)<=3]
   assert len(cands)==1,f'row{n} total rightedge{right}; matches{len(cands)}'
   components.append({'row':n,'label':line.split('$')[0].strip(),'cad':amount(cands[0].group()),'source_line':line})
  amort=sum(c['cad'] for c in components)
  # independently reconcile the Statement of Operations current actual total.
  op=[]
  for i,p in enumerate(pages):
   if 'STATEMENT OF OPERATIONS' in p and re.search(r'Total expenses\s+\$',p,re.I):
    for line in p.splitlines():
     if re.search(r'Total expenses\s+\$',line,re.I):
      cells=line.split('$')[1:]
      nums=[amount(NUM.search(x).group()) for x in cells if NUM.search(x)]
      if len(nums)==3:op.append((i+1,nums[1]))
  assert any(t==total for _,t in op),f'operations total not reconciled {op}'
  row.update(status='extracted',schedule_pdf_page=page_no,total_expenses_cad=total,amortization_cad=amort,expenses_excluding_amortization_cad=total-amort,program_sum_cad=program_sum,program_sum_rounding_difference_cad=program_sum-total,operations_pdf_page=next(i for i,t in op if t==total),components=components,total_source_line=line34,audit_qualified_marker=bool(re.search(r'Qualified Opinion|Basis for Qualified Opinion',text,re.I)))
 except Exception as e:row.update(status='unresolved',error=str(e))
 return row
def main():
 snapshot=json.loads((OUT/'review_snapshot_hashes.json').read_text())['individual_actuals']
 assert {r['catalog_resource_id']:r.get('sha256') for r in MAN['resources']}==snapshot,'Individual statements changed: repeat independent review before admitting revised actuals'
 with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(extract,MAN['resources']))
 (OUT/'actual2024_25_extraction.json').write_text(json.dumps({'school_year':'2024-25','admission_status':'research only; independent validation required','formula':'Schedule3 row34 actual2025Total minus sum rows24through28 actual2025Total','records':rows},indent=2)+'\n')
 fields=['index','authority_code','name','headcount','status','schedule_pdf_page','operations_pdf_page','total_expenses_cad','amortization_cad','expenses_excluding_amortization_cad','audit_qualified_marker','error']
 with (OUT/'actual2024_25_extraction.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
 print('extracted',sum(r['status']=='extracted' for r in rows),'of',len(rows))
 for r in rows:
  if r['status']!='extracted':print(r['index'],r['name'],r['error'])
 if all(r['status']=='extracted' for r in rows):
  assert {r['authority_code'] for r in rows}=={r['code'] for r in roster.values()}
  assert sum(r['headcount'] for r in rows)==EN['matched_headcount']
  _,monthly=cpi(False);months=[f'2024-{m:02}' for m in range(9,13)]+[f'2025-{m:02}' for m in range(1,9)]
  avg=sum(monthly[m] for m in months)/D(12);total=sum(r['expenses_excluding_amortization_cad'] for r in rows);per=D(total)/D(EN['matched_headcount'])
  out={'period':'2024-25','status':'research extraction; not continuous comparable trend','authority_count':len(rows),'matched_headcount':EN['matched_headcount'],'total_expenses_cad':sum(r['total_expenses_cad'] for r in rows),'amortization_cad':sum(r['amortization_cad'] for r in rows),'expenses_excluding_amortization_cad':total,'nominal_expenses_per_student':str(per),'real2025_expenses_per_student':str(per*D('172.2')/avg),'cpi_mean':str(avg),'cpi_months':months,'qualified_audits':[r['name'] for r in rows if r['audit_qualified_marker']]}
  (OUT/'actual2024_25_rollup.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
