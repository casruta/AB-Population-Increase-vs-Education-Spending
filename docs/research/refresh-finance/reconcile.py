"""Validate official refresh against archived inputs without mutating canonical files.
Default runs fully offline against downloaded evidence; --archived-only uses repo originals.
"""
import argparse,csv,datetime,hashlib,io,json,subprocess,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;P=OUT/'responses'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def enrolment(path):
 with zipfile.ZipFile(path) as z:
  strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
  rows=[]
  sheetrows=ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//s:row',NS)
  headers={}
  for cell in sheetrows[0]:
   value=cell.findtext('s:v',None,NS)
   if value is not None and cell.attrib.get('t')=='s':headers[strings[int(value)].strip()]=''.join(t for t in cell.attrib['r'] if t.isalpha())
  required=['School Authority Category','School Authority Name','School Authority Code','Total']
  assert all(k in headers for k in required),headers
  for row in sheetrows[1:]:
   values={}
   for c in row:
    v=c.findtext('s:v',None,NS)
    if v is not None: values[''.join(t for t in c.attrib['r'] if t.isalpha())]=strings[int(v)] if c.attrib.get('t')=='s' else v
   if values.get(headers['School Authority Category']) in ['Public','Separate','Francophone','Charter']:
    rows.append({'category':values[headers['School Authority Category']],'name':values[headers['School Authority Name']],'code':str(values[headers['School Authority Code']]).zfill(4),'count':int(values[headers['Total']])})
 assert len(set(r['code'] for r in rows))==len(rows)
 excluded=[r for r in rows if r['code'] in ['3170','4870']]
 assert len(excluded)==2
 return {'public_headcount':sum(r['count'] for r in rows),'lloydminster_headcount':sum(r['count'] for r in excluded),'matched_headcount':sum(r['count'] for r in rows if r not in excluded),'matched_authority_count':len(rows)-2,'excluded':excluded,'rows':rows}
def cpi(archived):
 if archived:
  rows=list(csv.DictReader((ROOT/'data/latest/alberta_monthly_cpi.csv').open()))
 else:
  path=P/'statcan_cpi_download'
  if not path.exists():path=ROOT/'work/finance-downloads/statcan_cpi_download.zip'
  with zipfile.ZipFile(path) as z:
   with z.open('18100004.csv') as f:rows=[r for r in csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig')) if r['VECTOR']=='v41692327' and '2016-09'<=r['REF_DATE']]
 assert all(r['GEO']=='Alberta' and r['Products and product groups']=='All-items' for r in rows)
 assert len({r['REF_DATE'] for r in rows})==len(rows)
 out={r['REF_DATE']:D(r['VALUE']) for r in rows}
 return rows,out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--archived-only',action='store_true');a=ap.parse_args()
 manifest=json.loads((ROOT/'data/latest/source_manifest.json').read_text())
 if not a.archived_only:
  for year in [2025,2026]:
   assert sha(P/f'allocation_{year}')==manifest['checked_files_sha256'][f'data/raw/current/operational-{year}.pdf'],f'Allocation{year}changed: manually review before using archived amounts'
 rows,monthly=cpi(a.archived_only)
 if not a.archived_only:
  with (OUT/'verified_alberta_monthly_cpi.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=['REF_DATE','VECTOR','GEO','Products and product groups','VALUE']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in rows)
 archived={r['REF_DATE']:D(r['VALUE']) for r in csv.DictReader((ROOT/'data/latest/alberta_monthly_cpi.csv').open())}
 changes=[{'month':k,'archived':str(v),'reviewed':str(monthly.get(k))} for k,v in archived.items() if monthly.get(k)!=v]
 amounts=json.loads((ROOT/'data/latest/school_funding_inputs.json').read_text());periods=[]
 for r in amounts:
  y=r['year'];year=r['school_year'];amount=r['public_allocation_cad']-r['lloydminster_allocation_cad']
  out={'school_year':year,'matched_allocation_cad':amount,'status':r['status'],'allocation_publication_date':'2025-09-16' if y==2024 else '2026-05-13','allocation_reference_vintage':'August2025' if y==2024 else 'April2026'}
  if y<2026:
   file='ecc-authority-enrolment-data-2024-2025.xlsx' if y==2024 else 'ecc-preliminary-authority-enrolment-data-2025-2026.xlsx'
   original=ROOT/'data/raw/k12'/file
   live=P/('enrolment2024_live' if y==2024 else 'enrolment2025_live')
   en=enrolment(original if a.archived_only else live)
   assert en['public_headcount']==r['public_headcount'] and en['lloydminster_headcount']==r['lloydminster_headcount']
   months=[f'{y}-{m:02}' for m in range(9,13)]+[f'{y+1}-{m:02}' for m in range(1,9)]
   assert len(months)==12 and all(m in monthly for m in months)
   avg=sum(monthly[m] for m in months)/D(12);nominal=D(amount)/D(en['matched_headcount']);real=nominal*D('172.2')/avg
   out.update(matched_headcount=en['matched_headcount'],matched_authority_count=en['matched_authority_count'],enrolment_sha256=sha(original if a.archived_only else live),enrolment_matches_archived=sha(original if a.archived_only else live)==sha(original),enrolment_status='final' if y==2024 else 'preliminary',enrolment_count_timing='September30 school-year headcount' if y==2024 else 'December2025 count (official page footnote); preliminary school-year headcount',enrolment_upload_date_proxy='2026-02-05',cpi_months=months,cpi_mean=str(avg),nominal_per_student=str(nominal),real_2025_per_student=str(real),excluded_authorities=en['excluded'])
  else:out['matched_headcount']=None;out['real_2025_per_student']=None
  periods.append(out)
 change=(D(periods[1]['real_2025_per_student'])/D(periods[0]['real_2025_per_student'])-1)*100
 result={'checked_date':'2026-10-05','mode':'archived-only' if a.archived_only else 'live-response-reconciliation','publication_snapshot_date':'2026-09-20','school_funding':periods,'real_allocation_percent_change_2024_to_2025':str(change),'illustrative_100_dollars_per_student_annual_cad':periods[1]['matched_headcount']*100,'cpi_latest_reference_month':max(monthly),'cpi_release_date':'2026-09-14','cpi_changes_from_archived':changes,'actuals':{'latest_combined_period_on_official_listing':'2023-24','combined_publication_date':'2025-07-08','continuous_comparable_actual_trend_end':'2021-22','individual_2024_25_statements_available':True,'individual_publication_date':'2025-12-16','combined_or_summary_2024_25_found':False,'government_combined_2024_25_status':'No government-published combined or summary2024-25 total was located; individual statements are available.'},'limitations':['Source availability describes checked official pages/catalog searches; cannot prove no unpublished or unindexed file exists.','2025-26 denominator remains preliminary;2026-27 has no matched headcount.','CPI general purchasing power is not school input cost inflation.']}
 if (OUT/'actual2024_25_rollup.json').exists():
  result['actuals']['reconstruction_status']='Accepted standalone83-authority reconstruction within the scope and caveats in rollup-review.md; not a government-issued combined total.'
  result['actuals']['reconstructed_2024_25_level']=json.loads((OUT/'actual2024_25_rollup.json').read_text())
  result['actuals']['individual_source_metadata_modified']='2026-04-21T15:50:48.507824'
  result['actuals']['individual_latest_resource_update']='2026-04-08T17:43:11.717866'
  result['actuals']['reconstruction_review']='Full83independent source-column,hash,total,amortization review passed; see rollup-review.md'
 file=OUT/('archived_summary.json' if a.archived_only else 'reviewed_summary.json');file.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'mode':result['mode'],'funding_real_change_pct':str(change),'cost_100_cad':result['illustrative_100_dollars_per_student_annual_cad'],'cpi_changes':changes,'latest_CPI':max(monthly)},indent=2))
if __name__=='__main__':main()
