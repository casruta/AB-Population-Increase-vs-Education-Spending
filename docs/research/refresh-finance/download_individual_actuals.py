"""Download official individual statements into ignored working storage, TLS verified."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json,urllib.request,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
WORK=ROOT/'work/finance-downloads/actual2024-25';WORK.mkdir(parents=True,exist_ok=True)
j=json.loads((OUT/'responses/individual2024_metadata').read_text())['result']
def fetch(pair):
 i,r=pair;path=WORK/f'{i:02}.pdf';row={'index':i,'name':r['name'],'url':r['url'],'catalog_resource_id':r['id'],'created':r.get('created'),'last_modified':r.get('last_modified'),'catalog_bytes':r.get('size'),'tls_verification':True}
 try:
  if not path.exists():
   with urllib.request.urlopen(urllib.request.Request(r['url'],headers={'User-Agent':'FinancialSourceFreshnessReview/1.0'}),timeout=30) as response:
    body=response.read();assert body.startswith(b'%PDF');path.write_bytes(body)
  row.update(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),file=str(path.relative_to(ROOT)),status='downloaded')
 except Exception as e:row.update(status='failed',error=str(e))
 return row
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,enumerate(j['resources'])))
(OUT/'individual_actuals_manifest.json').write_text(json.dumps({'catalog_id':j['id'],'issuedate':j['issuedate'],'metadata_modified':j['metadata_modified'],'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'resources':rows},indent=2)+'\n')
print('downloaded',sum(r['status']=='downloaded' for r in rows),'of',len(rows))
