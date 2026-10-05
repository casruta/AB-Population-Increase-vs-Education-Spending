from probe_sources import probe,OUT
from concurrent.futures import ThreadPoolExecutor
import json
p=OUT/'responses'
j=json.loads((p/'live_enrolment_metadata').read_text())['result']
urls=[('enrolment2025_live',j['resources'][0]['url']),('enrolment2024_live',j['resources'][2]['url']),('individual2024_metadata','https://open.alberta.ca/api/3/action/package_show?id=2f4b0aa9-b327-4bfa-86ba-783583eae157')]
with ThreadPoolExecutor(max_workers=3) as pool:r=list(pool.map(probe,urls))
(OUT/'resource_network_results.json').write_text(json.dumps(r,indent=2)+'\n')
print([(x['id'],x['status']) for x in r])
