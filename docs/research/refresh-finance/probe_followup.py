from probe_sources import probe,OUT
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
import json
queries=['title:"2024-2025 school authorities audited financial statements"','title:"2023-2024 school authorities audited financial statements"','title:"school authority audited financial statements"']
urls=[('exact_search_'+str(i),'https://open.alberta.ca/api/3/action/package_search?'+urlencode({'q':q,'rows':100})) for i,q in enumerate(queries)]
urls += [('live_enrolment_metadata','https://open.alberta.ca/api/3/action/package_show?id=ccbcf0fb-615e-44a0-b7ec-681e2ea4e1e7'),('live_combined_metadata','https://open.alberta.ca/api/3/action/package_show?id=2a9487b1-9d7a-47db-9f05-e633c315e447'),('individual_actual2024','https://open.alberta.ca/publications/2828632-2024-2025'),('cpi_daily','https://www150.statcan.gc.ca/n1/daily-quotidien/260914/dq260914a-eng.htm')]
with ThreadPoolExecutor(max_workers=5) as pool:res=list(pool.map(probe,urls))
(OUT/'followup_network_results.json').write_text(json.dumps(res,indent=2)+'\n')
for x in res:print(x['id'],x['status'])
