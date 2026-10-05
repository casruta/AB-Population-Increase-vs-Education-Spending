"""Read-only HTTPS freshness checks; uses existing proxy and verified default TLS."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import urllib.request, urllib.error, json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
urls=[
('authority_statements','https://www.alberta.ca/k-12-education-financial-statements'),
('student_statistics','https://www.alberta.ca/student-population-statistics'),
('allocation_2025','https://www.alberta.ca/system/files/educ-budget-2025-projected-operational-funding-school-jurisdictions.pdf'),
('allocation_2026','https://www.alberta.ca/system/files/ecc-projected-operational-funding-school-authorities.pdf'),
('open_catalog_search','https://open.alberta.ca/api/3/action/package_search?q=2024-2025%20school%20authorities%20audited%20financial%20statements&rows=10'),
('open_catalog_2023','https://open.alberta.ca/api/3/action/package_show?id=a91a3309-414c-4632-8166-a847273ad73e'),
('statcan_cpi_table','https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401'),
('statcan_cpi_download','https://www150.statcan.gc.ca/n1/tbl/csv/18100004-eng.zip'),
('statcan_cpi_metadata','https://www.statcan.gc.ca/en/developers/wds'),
('statcan_wds_cpi','https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/18100004/en'),
('statcan_cpi_calendar','https://www.statcan.gc.ca/en/subjects-start/prices_and_price_indexes/consumer_price_indexes'),
('cbe_actual_2024','https://cbe.ab.ca/about-us/budget-and-finance/Documents/Financial-Results-2024-25.pdf'),
]
def probe(item):
 name,url=item
 result={'id':name,'url':url,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tls_verification':True}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'FinancialSourceFreshnessReview/1.0'}),timeout=25) as r:
   body=r.read(40*1024*1024)
   result.update(status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type'),last_modified=r.headers.get('Last-Modified'),bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
   path=ROOT/'work/finance-downloads/statcan_cpi_download.zip' if name=='statcan_cpi_download' else OUT/'responses'/name
   path.parent.mkdir(parents=True,exist_ok=True)
   path.write_bytes(body)
   result['body_file']=str(path.relative_to(ROOT))
 except urllib.error.HTTPError as e:
  body=e.read(2048).decode('utf-8','replace')
  result.update(status=e.code,error=body,proxy_error=e.headers.get('X-Squid-Error'))
 except Exception as e:result.update(status=None,error=str(e))
 return result
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(probe,urls))
 (OUT/'network_results.json').write_text(json.dumps(results,indent=2)+'\n')
 for r in results:print(r['id'],r['status'],r.get('error','')[:160])
