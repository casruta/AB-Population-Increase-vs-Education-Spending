"""Describe published authority headcounts; snapshot timing prevents causal attribution."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import csv, hashlib, json
ROOT=Path(__file__).resolve().parents[3]
NS={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
ALLOWED={'Public','Separate','Francophone','Charter'}

def load(path):
    with ZipFile(path) as z:
        strings=[''.join(t.text or '' for t in si.findall('.//x:t',NS)) for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall('x:si',NS)]
        rows=[]
        for row in E.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//x:row',NS):
            d={}
            for c in row.findall('x:c',NS):
                v=c.find('x:v',NS); val=v.text if v is not None else ''
                if c.get('t')=='s':val=strings[int(val)]
                d[''.join(i for i in c.get('r') if i.isalpha())]=val
            if d.get('A') not in ALLOWED:continue
            code=d['C'].zfill(4)
            if code in {'3170','4870'}:continue
            grades=[int(d.get(c,'0') or 0) for c in 'DEFGHIJKLMNOP']
            total=int(d['Q'])
            assert sum(grades)==total,(code,grades,total)
            rows.append({'code':code,'category':d['A'],'name':d['B'],'headcount':total})
    assert len({r['code'] for r in rows})==len(rows)
    return {r['code']:r for r in rows}

paths=[ROOT/'data/raw/k12/ecc-authority-enrolment-data-2024-2025.xlsx',ROOT/'data/raw/k12/ecc-preliminary-authority-enrolment-data-2025-2026.xlsx']
a,b=map(load,paths)
rows=[]
for code in sorted(set(a)|set(b)):
    x,y=a.get(code),b.get(code)
    rows.append({'code':code,'name':(y or x)['name'],'category':(y or x)['category'],'headcount_2024_25':x['headcount'] if x else '', 'headcount_2025_26':y['headcount'] if y else '', 'change':y['headcount']-x['headcount'] if x and y else '', 'growth':y['headcount']/x['headcount']-1 if x and y and x['headcount'] else '', 'roster_status':'matched' if x and y else 'one-year-only'})
out=Path(__file__).parent
with (out/'authority_headcounts.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
summary={'scope':'Public/separate/francophone/charter; ECS included; both Lloydminster excluded', 'snapshot_warning':'2024–25 published final September headcount versus 2025–26 preliminary December 2025 count. Differences are published school-year snapshots, not a migration attribution or same-month experimental comparison.', 'totals':[sum(x['headcount'] for x in v.values()) for v in [a,b]], 'roster_sizes':[len(a),len(b)],'unmatched':[r for r in rows if r['roster_status']!='matched'],'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths], 'large_authority_examples': sorted([r for r in rows if r['roster_status']=='matched' and r['headcount_2024_25']>=5000],key=lambda r:r['growth'],reverse=True)[:8]}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
