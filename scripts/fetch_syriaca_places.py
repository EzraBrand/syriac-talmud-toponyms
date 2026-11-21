"""Fetch the Syriac Gazetteer place TEI files from srophe/syriaca-data (data/places/tei).

Uses `gh api` (shell HTTP tools are blocked by policy). Resumable: files that are
already on disk are skipped. Writes sources/syriaca-places-tei/<id>.xml and
sources/syriaca-places-tei/_manifest.json (commit SHA, date, file count).

    py -3.13 -I scripts/fetch_syriaca_places.py
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sources" / "syriaca-places-tei"
REPO = "srophe/syriaca-data"


def gh(args, raw=False):
    cmd = ["gh", "api"]
    if raw:
        cmd += ["-H", "Accept: application/vnd.github.raw"]
    cmd += args
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    head = json.loads(gh([f"repos/{REPO}/commits/master"]))
    sha, date = head["sha"], head["commit"]["committer"]["date"]
    tree = json.loads(gh([f"repos/{REPO}/git/trees/{sha}:data/places/tei"]))
    names = [t["path"] for t in tree["tree"] if t["path"].endswith(".xml")]
    todo = [n for n in names if not (OUT / n).exists()]
    print(f"commit {sha[:10]} {date}; {len(names)} files, {len(todo)} to fetch", flush=True)

    def get(n):
        data = gh([f"repos/{REPO}/contents/data/places/tei/{n}?ref={sha}"], raw=True)
        (OUT / n).write_bytes(data)
        return n

    done = fail = 0
    with ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(get, n): n for n in todo}
        for f in as_completed(futs):
            try:
                f.result()
                done += 1
            except Exception as e:  # report at once, keep going
                fail += 1
                print(f"FAIL {futs[f]}: {e}", flush=True)
            if (done + fail) % 200 == 0:
                print(f"{done + fail}/{len(todo)}", flush=True)
    have = len(list(OUT.glob("[0-9]*.xml")))
    (OUT / "_manifest.json").write_text(json.dumps(
        {"repo": REPO, "path": "data/places/tei", "commit": sha, "commit_date": date,
         "files_in_tree": len(names), "files_on_disk": have}, indent=1))
    print(f"finished: fetched {done}, failed {fail}, on disk {have}/{len(names)}", flush=True)


if __name__ == "__main__":
    main()
