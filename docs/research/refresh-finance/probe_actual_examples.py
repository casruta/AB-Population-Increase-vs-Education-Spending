from probe_sources import probe,OUT
from concurrent.futures import ThreadPoolExecutor
import json
j=json.loads((OUT/'responses/individual2024_metadata').read_text())['result']
select=['The Calgary School Division','The Edmonton School Division','Alberta Classical Academy Ltd.','The Northland School Division','Valhalla School Foundation']
urls=[]
for i,r in enumerate(j['resources']):
 if r['name'] in select:urls.append(('actual_example_'+str(i),r['url']))
print([(r['name'],i) for i,r in enumerate(j['resources']) if r['name'] in select])
with ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(probe,urls))
(OUT/'actual_examples_network_results.json').write_text(json.dumps(results,indent=2)+'\n')
print([(r['id'],r['status'],r.get('bytes')) for r in results])
