#!/usr/bin/env python3
"""Fetch official StatCan snapshots with TLS verification and bounded Alberta extracts.
Run into a NEW directory, then review before replacing evidence. No canonical data writes.
"""
import argparse, csv, datetime, hashlib, io, json, pathlib, urllib.request, zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=pathlib.Path, required=True)
parser.add_argument('--start-year', type=int, default=2021)
parser.add_argument('--as-of', type=datetime.date.fromisoformat, required=True)
parser.add_argument('--products', nargs='+', default=['17100008','17100009','17100014','17100015','17100005','17100040','17100020','17100045','17100059'])
args = parser.parse_args()
assert 1971 <= args.start_year <= args.as_of.year
allowed = {'17100008','17100009','17100014','17100015','17100005','17100040','17100020','17100045','17100059'}
assert set(args.products) <= allowed, 'Only reviewed official population products are supported'
args.output_dir.mkdir(parents=True, exist_ok=False)
records = []
for pid in args.products:
    url = f'https://www150.statcan.gc.ca/n1/tbl/csv/{pid}-eng.zip'
    with urllib.request.urlopen(url, timeout=45) as response:
        assert response.status == 200
        assert response.geturl().startswith('https://www150.statcan.gc.ca/')
        payload = response.read(50_000_001)
        assert len(payload) <= 50_000_000, 'Unexpected payload size'
        modified = response.headers.get('Last-Modified')
        if modified:
            from email.utils import parsedate_to_datetime
            assert parsedate_to_datetime(modified).date() <= args.as_of, 'Source is newer than requested evidence date'
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        assert archive.testzip() is None
        metadata = archive.read(f'{pid}_MetaData.csv')
        assert f'"{pid}"'.encode() in metadata, 'Unexpected metadata product'
        text = io.TextIOWrapper(archive.open(f'{pid}.csv'), encoding='utf-8-sig', newline='')
        reader = csv.DictReader(text)
        required = {'REF_DATE','GEO','UOM','SCALAR_FACTOR','VALUE','STATUS'}
        assert required <= set(reader.fieldnames), 'Unexpected schema'
        selected = []
        seen = set()
        for row in reader:
            geography = row['GEO'] == 'Alberta'
            if pid == '17100045':
                geography = 'Alberta' in row['GEO'] or 'Alberta' in row['Geography, province of destination']
            if not geography or row['REF_DATE'] < str(args.start_year):
                continue
            if 'Gender' in row and row['Gender'] != 'Total - gender':
                continue
            assert row['SCALAR_FACTOR'] == 'units'
            assert row['UOM'] in {'Persons','Number','Years'}
            key = (row['REF_DATE'], row['COORDINATE'])
            assert key not in seen, f'Duplicate observation: {key}'
            seen.add(key)
            selected.append(row)
        assert selected, 'No Alberta rows selected'
        extract = args.output_dir / f'{pid}-alberta.csv'
        with extract.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(selected)
        (args.output_dir / f'{pid}-metadata.csv').write_bytes(metadata)
    records.append(dict(product=pid,url=url,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),last_modified=modified,download_sha256=hashlib.sha256(payload).hexdigest(),download_bytes=len(payload),extract_sha256=hashlib.sha256(extract.read_bytes()).hexdigest(),rows=len(selected),minimum_reference=min(r['REF_DATE'] for r in selected),maximum_reference=max(r['REF_DATE'] for r in selected),filters=dict(geography='Alberta; origin or destination for17100045',gender='Total - gender where applicable',start_year=args.start_year)))
    (args.output_dir / 'download-manifest.json').write_text(json.dumps(records, indent=2)+'\n')
    print(pid, len(selected), records[-1]['maximum_reference'])
