"""Discover official sources through CKAN and save HTTPS evidence using curl.

Run from any directory. Requires curl; Python uses only the standard library.
TLS checks and platform proxy configuration are retained. No guessed resource
URLs, authentication changes, or certificate exceptions are used.
"""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit

BASE = Path(__file__).resolve().parent
API = "https://open.alberta.ca/api/3/action/"
QUERIES = {
    "all-education-annual-search": 'title:"annual report" AND (title:education OR title:childcare)',
    "class-size-search": 'title:"class size"',
    "assurance-search": 'title:"Assurance" AND title:"Measure"',
}


def fetch(url, path):
    if urlsplit(url).scheme != "https" or urlsplit(url).hostname not in {
            "open.alberta.ca", "www.alberta.ca"}:
        raise ValueError("Expected an official Alberta HTTPS URL")
    result = subprocess.run(
        ["curl", "--silent", "--show-error", "--fail", "--location",
         "--proto", "=https", "--proto-redir", "=https", "--max-time", "45",
         "--output", str(path), "--write-out", "%{http_code}", url],
        text=True, capture_output=True)
    # Error strings are intentionally not saved: proxy configuration can include
    # injected authentication. HTTP code and curl exit code are sufficient here.
    event = {"url": url, "http_code": result.stdout, "curl_exit_code": result.returncode}
    if result.returncode == 0:
        event["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        event["local_path"] = str(path.relative_to(BASE))
    return event


def main():
    log = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "requests": []}
    candidates = []
    for name, query in QUERIES.items():
        path = BASE / (name + ".json")
        event = fetch(API + "package_search?" + urlencode({"q": query, "rows": 100}), path)
        log["requests"].append(event)
        if event["curl_exit_code"] != 0:
            continue
        body = json.loads(path.read_text())
        if not body.get("success"):
            raise ValueError("CKAN returned an unsuccessful response")
        result = body["result"]
        if result["count"] > len(result["results"]):
            event["warning"] = "Search is truncated; paginate before claiming exhaustive discovery"
        for package in result["results"]:
            for resource in package["resources"]:
                candidates.append({"package": package["name"], "title": package["title"],
                                   "package_modified": package["metadata_modified"],
                                   "resource_name": resource.get("name"),
                                   "resource_created": resource.get("created"),
                                   "resource_modified": resource.get("last_modified"),
                                   "url": resource["url"]})
    (BASE / "discovered-resources.json").write_text(json.dumps(candidates, indent=2) + "\n")
    (BASE / "discovery-log.json").write_text(json.dumps(log, indent=2) + "\n")
    failures = sum(event["curl_exit_code"] != 0 for event in log["requests"])
    print(f"Saved {len(candidates)} official resource records; {failures} requests failed.")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
