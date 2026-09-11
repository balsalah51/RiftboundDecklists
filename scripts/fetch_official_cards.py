#!/usr/bin/env python3
"""Download official Riftbound card images used in public lists."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "img" / "cards"
GALLERY_PAGE = "https://playriftbound.com/en-us/card-gallery/"
SET_MAX = {"OGN": 298, "OGS": 24, "SFD": 221, "UNL": 219, "VEN": 166}
SET_RANK = {"VEN": 0, "UNL": 1, "SFD": 2, "OGS": 3, "OGN": 4}
SKIP_NAMES = {"Decks"}


def slugify(name: str) -> str:
    s = name.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "card"


def norm(s: str) -> str:
    s = (s or "").lower().replace("’", "'").replace("‘", "'").replace("`", "'")
    return re.sub(r"\s+", " ", s).strip()


def gallery_json_url() -> str:
    req = urllib.request.Request(GALLERY_PAGE, headers={"User-Agent": "RiftboundDecklists/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", "replace")
    m = re.search(r'"buildId":"([^"]+)"', html)
    if not m:
        raise SystemExit("Could not find Next.js buildId")
    return f"https://playriftbound.com/_next/data/{m.group(1)}/en-us/card-gallery.json"


def fetch_bytes(url: str, tries: int = 4) -> bytes:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RiftboundDecklists/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as err:
            last = err
            time.sleep(1.2 * (i + 1))
    proc = subprocess.run(
        ["curl", "-fsSL", "--retry", "4", "--retry-delay", "2", url],
        capture_output=True,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout:
        return proc.stdout
    raise last or RuntimeError(f"failed {url}")


def jpeg_url(url: str, width: int = 420) -> str:
    parsed = urllib.parse.urlparse(url)
    q = urllib.parse.parse_qs(parsed.query)
    q["w"] = [str(width)]
    q["fm"] = ["jpg"]
    q["q"] = ["78"]
    return urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(q, doseq=True)))


def score_printing(card: dict) -> tuple:
    code = card.get("publicCode") or ""
    set_id = ((card.get("set") or {}).get("value") or {}).get("id") or ""
    raw_n = str(card.get("collectorNumber") or "0")
    n = int(re.sub(r"\D", "", raw_n) or 0)
    cap = SET_MAX.get(set_id, 999)
    star = 1 if "*" in code else 0
    letter = 1 if re.search(r"[A-Za-z]", str(card.get("collectorNumber") or "")) else 0
    over = 1 if n > cap else 0
    return (star, over, letter, SET_RANK.get(set_id, 9), n)


def list_names() -> list[str]:
    sys.path.insert(0, str(ROOT / "scripts"))
    import build

    barcelona = build.parse_barcelona((ROOT / "data/barcelona-top-decks.txt").read_text(encoding="utf-8", errors="replace"))
    extra = build.parse_extra((ROOT / "data/extra-lists.txt").read_text(encoding="utf-8", errors="replace"))
    scraped_path = ROOT / "data/scraped-lists.txt"
    scraped = build.parse_extra(scraped_path.read_text(encoding="utf-8", errors="replace")) if scraped_path.exists() else []
    names = set()
    for d in barcelona + extra + scraped:
        names.add(d["legend"])
        names.add(d["champion"])
        for _q, n in d["main"] + d["battlefields"] + d["runes"] + d["sideboard"]:
            names.add(n)
    clean = []
    for n in names:
        if not n or n in SKIP_NAMES or "##" in n or len(n) < 3:
            continue
        clean.append(n)
    return sorted(set(clean))


def pick_card(index: dict[str, list], name: str):
    key = norm(name)
    hits = index.get(key)
    if not hits and "," in name:
        hits = index.get(norm(name.split(",", 1)[1]))
    if not hits:
        return None
    hits = sorted(hits, key=score_printing)
    return hits[0]


def download_one(name: str, card: dict) -> dict:
    src = (card.get("cardImage") or {}).get("url")
    fname = slugify(name) + ".jpg"
    dest = OUT / fname
    if not (dest.exists() and dest.stat().st_size > 5000):
        dest.write_bytes(fetch_bytes(jpeg_url(src)))
    return {
        "file": fname,
        "code": card.get("publicCode"),
        "officialName": card.get("name"),
        "src": src,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    url = gallery_json_url()
    print("Fetching official card gallery…", url)
    data = json.loads(fetch_bytes(url))
    cards = None
    for b in data["pageProps"]["page"]["blades"]:
        if b.get("cards", {}).get("items"):
            cards = b["cards"]["items"]
            break
    if not cards:
        raise SystemExit("No cards in gallery JSON")

    index = defaultdict(list)
    for c in cards:
        nm = c.get("name") or ""
        if not nm or not (c.get("cardImage") or {}).get("url"):
            continue
        index[norm(nm)].append(c)
        if " - " in nm:
            index[norm(nm.split(" - ", 1)[0])].append(c)

    names = list_names()
    jobs = []
    missing = []
    for name in names:
        card = pick_card(index, name)
        if not card:
            missing.append(name)
            continue
        jobs.append((name, card))

    mapping = {}
    print(f"Downloading {len(jobs)} official printings…")
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(download_one, name, card): name for name, card in jobs}
        done = 0
        for fut in as_completed(futs):
            name = futs[fut]
            try:
                mapping[name] = fut.result()
            except Exception as err:
                print("FAIL", name, err)
                missing.append(name)
            done += 1
            if done % 40 == 0 or done == len(futs):
                print(f"  {done}/{len(futs)}")

    (ROOT / "data" / "official-card-art.json").write_text(
        json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(mapping)} images. Missing: {missing or 'none'}")


if __name__ == "__main__":
    main()
