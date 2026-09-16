#!/usr/bin/env python3
"""Send knowledge files to a self-hosted Cognee through its HTTP API.

    python3 scripts/ingest.py --all                          # every file in every mapped folder
    python3 scripts/ingest.py projects/acme.md decisions/x.md  # only these files

Method, learned in production:
  add each file as a NAMED file (raw text uploads lose their name),
  delete a previous version with the same name first (a changed file is a new document),
  then ONE cognify per touched dataset (parallel writes fail on embedded graph stores),
  wait for DATASET_PROCESSING_COMPLETED, then print the dataset inventory.

Configuration:
  datasets.json      folder -> dataset name (repo root)
  COGNEE_BASE_URL    default http://localhost:8000
  COGNEE_API_KEY     from the environment, or from ~/.cognee/.env
"""
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATASETS = {k: v for k, v in json.loads((ROOT / "datasets.json").read_text()).items() if not k.startswith("_")}
BASE = os.environ.get("COGNEE_BASE_URL", "http://localhost:8000").rstrip("/")


def api_key():
    key = os.environ.get("COGNEE_API_KEY")
    envfile = pathlib.Path.home() / ".cognee" / ".env"
    if not key and envfile.exists():
        for line in envfile.read_text().splitlines():
            if line.startswith("COGNEE_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"')
    if not key:
        sys.exit("COGNEE_API_KEY not set (environment or ~/.cognee/.env)")
    return key


HEADERS = {"X-Api-Key": api_key()}


def req(method, path, body=None, ctype=None):
    hdrs = dict(HEADERS)
    if body is not None and ctype is None:
        body, ctype = json.dumps(body).encode(), "application/json"
    if ctype:
        hdrs["Content-Type"] = ctype
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + path, data=body, method=method, headers=hdrs), timeout=120) as r:
            text = r.read().decode()
            return r.status, (json.loads(text) if text else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def frontmatter(p):
    m = re.match(r"^---\n(.*?)\n---", p.read_text(encoding="utf-8"), re.S)
    fm = {}
    for line in (m.group(1).splitlines() if m else []):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip("[]").replace('"', "")
    return fm


def node_set(p):
    fm = frontmatter(p)
    tags = {fm.get("type", p.parent.name), p.stem}
    if fm.get("project", "none") != "none":
        tags.add(fm["project"])
    tags |= {t.strip() for t in fm.get("tags", "").split(",") if t.strip()}
    return sorted(tags)


def add_file(p, dataset, ns):
    b = uuid.uuid4().hex

    def field(name, value):
        return f'--{b}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()

    body = (field("datasetName", dataset) + field("node_set", json.dumps(ns))
            + f'--{b}\r\nContent-Disposition: form-data; name="data"; filename="{p.name}"\r\nContent-Type: text/markdown\r\n\r\n'.encode()
            + p.read_bytes() + f"\r\n--{b}--\r\n".encode())
    return req("POST", "/api/v1/add", body, f"multipart/form-data; boundary={b}")


def dataset_ids():
    _, ds = req("GET", "/api/v1/datasets")
    return {d["name"]: d["id"] for d in (ds or [])}


def main(argv):
    if "--all" in argv:
        files = sorted(f for folder in DATASETS for f in (ROOT / folder).glob("*.md"))
    else:
        files = [(ROOT / a).resolve() for a in argv]
    if not files:
        print(__doc__)
        return 2
    ids = dataset_ids()
    touched = set()
    for p in files:
        folder = p.parent.name
        if folder not in DATASETS:
            print(f"skip {p}: folder `{folder}` not in datasets.json")
            continue
        dataset = DATASETS[folder]
        if dataset in ids:
            _, docs = req("GET", f"/api/v1/datasets/{ids[dataset]}/data")
            for d in docs or []:
                if d["name"] == p.stem:
                    st, _ = req("DELETE", f"/api/v1/datasets/{ids[dataset]}/data/{d['id']}")
                    print(f"del  {dataset}/{p.name} (previous version) HTTP {st}")
        st, out = add_file(p, dataset, node_set(p))
        print(f"add  {dataset}/{p.name:50} HTTP {st}" + ("" if st == 200 else f" {out}"), flush=True)
        if st != 200:
            return 1
        touched.add(dataset)
    ids = dataset_ids()
    for dataset in sorted(touched):
        st, _ = req("POST", "/api/v1/cognify", {"datasets": [dataset], "runInBackground": True})
        print(f"cognify {dataset}: HTTP {st}", flush=True)
    done, t0 = set(), time.time()
    while len(done) < len(touched) and time.time() - t0 < 3600:
        time.sleep(30)
        for dataset in sorted(touched - done):
            _, out = req("GET", f"/api/v1/datasets/status?dataset={ids[dataset]}")
            s = json.dumps(out)
            if "COMPLETED" in s:
                done.add(dataset)
                print(f"ok   {dataset} completed after {int(time.time() - t0)} s", flush=True)
            elif "ERROR" in s.upper():
                done.add(dataset)
                print(f"err  {dataset}: {s[:300]}", flush=True)
    for dataset in sorted(touched):
        _, docs = req("GET", f"/api/v1/datasets/{ids[dataset]}/data")
        print(f"\n{dataset} ({len(docs or [])} documents): " + ", ".join(sorted(d["name"] for d in docs or [])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
