"""Reproduce finance research checks; never changes canonical inputs or report.
--archived-only validates original repo inputs without network.
Default reads saved official responses and ignored downloaded PDFs.
--download refreshes official responses and downloads individual actuals first.
"""
from pathlib import Path
import argparse,subprocess,sys
P=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--archived-only',action='store_true');p.add_argument('--download',action='store_true');a=p.parse_args()
assert not (a.archived_only and a.download)
def run(script,*args):subprocess.run([sys.executable,str(P/script),*args],check=True)
if a.archived_only:run('reconcile.py','--archived-only')
else:
 if a.download:
  for s in ['probe_sources.py','probe_followup.py','probe_resources.py','download_individual_actuals.py']:run(s)
 run('extract_actuals.py');run('reconcile.py');run('extract_comparatives.py')
