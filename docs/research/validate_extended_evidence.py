"""Check reviewed evidence and prove materially inconsistent inputs are rejected."""
from pathlib import Path
from unittest.mock import patch
import json, shutil, tempfile, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import extended_report as report
report.load_reviewed_evidence()
files=['migration/reviewed_summary.json','refresh-outcomes/reviewed_summary.json','refresh-finance/actual2024_25_rollup.json','refresh-outcomes/class-size-summary.json','refresh-finance/comparative79_reviewed_summary.json','refresh-finance/comparative79_research.json','refresh-finance/actual2024_25_extraction.json']
cases=[
 ('actual expense total','refresh-finance/actual2024_25_rollup.json',lambda d:d.update(expenses_excluding_amortization_cad=d['expenses_excluding_amortization_cad']+1000)),
 ('duplicate authority','refresh-finance/actual2024_25_extraction.json',lambda d:d['records'].append(d['records'][0])),
 ('migration identity','migration/reviewed_summary.json',lambda d:d['age_5_17_trend'][0].update(**{'Total net migration':0})),
 ('outcome rate units','refresh-outcomes/reviewed_summary.json',lambda d:d['grade9_math'].update(change_pp=10)),
 ('class suppressed denominator','refresh-outcomes/class-size-summary.json',lambda d:d['grade_bands']['G7-9'].update(suppressed_under10=0)),
 ('unreviewed cohort scope','refresh-finance/comparative79_reviewed_summary.json',lambda d:d.update(accepted_scope='harmonized_resource_change')),
 ('period drift','refresh-finance/actual2024_25_rollup.json',lambda d:d.update(period='2025-26')),
]
for name,relative,mutate in cases:
 with tempfile.TemporaryDirectory() as temporary:
  target=Path(temporary)
  for f in files:
   dest=target/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(report.RESEARCH/f,dest)
  dest=target/relative;data=json.loads(dest.read_text());mutate(data);dest.write_text(json.dumps(data))
  with patch.object(report,'RESEARCH',target):
   try:report.load_reviewed_evidence()
   except ValueError:pass
   else:raise AssertionError(f'Material invalid input was accepted: {name}')
print('Reviewed baseline passes; seven material corruption/period/scope cases rejected.')
