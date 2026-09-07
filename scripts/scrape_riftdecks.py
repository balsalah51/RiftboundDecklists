#!/usr/bin/env python3
"""Pull complete Aug–Sep 2026 top-finish lists from riftdecks.com into data/scraped-lists.txt."""
from __future__ import annotations

import html as htmlmod
import re
import time
from pathlib import Path
from urllib.parse import urljoin

from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/scraped-lists.txt"
BASE = "https://riftdecks.com"
START = "2026-08-01"
END = "2026-09-07"
TARGET = 320
UA_IMPERSONATE = "chrome"

LEGEND_ALIASES = {
    "Khazix, Voidreaver": "Kha'Zix, Voidreaver",
    "Reksai, Void Burrower": "Rek'Sai, Void Burrower",
    "Leblanc, Deceiver": "LeBlanc, Deceiver",
    "Kai'sa, Daughter of the Void": "Kai'Sa, Daughter of the Void",
}

HOMO = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
    "і": "i", "ѕ": "s", "А": "A", "Е": "E", "О": "O", "Р": "P", "С": "C",
})


def get(url: str, tries: int = 8) -> str:
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, impersonate=UA_IMPERSONATE, timeout=45)
            if r.status_code == 429:
                wait = 8 + i * 6
                print(f"    429 {url.split('/')[-1]} sleep {wait}s", flush=True)
                time.sleep(wait)
                last = "HTTP 429"
                continue
            if r.status_code == 200 and "Just a moment" not in r.text[:400]:
                return r.text
            last = f"HTTP {r.status_code}"
        except Exception as ex:
            last = str(ex)
        time.sleep(0.6 * (i + 1))
    raise RuntimeError(f"fetch failed {url}: {last}")


def clean(s: str) -> str:
    s = htmlmod.unescape(s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def ascii_player(name: str) -> str:
    return clean(name).translate(HOMO)


def parse_placing(text: str) -> int | None:
    text = clean(text)
    m = re.search(r"(\d+)\s*(?:st|nd|rd|th)\b", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"Top\s*(\d+)", text, re.I)
    if m:
        return int(m.group(1))
    return None


def cutoff(field: int) -> int:
    if field >= 1000:
        return 64
    if field >= 400:
        return 32
    if field >= 128:
        return 16
    if field >= 48:
        return 8
    if field >= 24:
        return 4
    if field >= 16:
        return 2
    return 1


def bucket_for(event: str) -> str:
    e = event.lower()
    if any(k in e for k in ("regional qualifier", "regional open", "rq ", " rq")):
        return "regional"
    if any(k in e for k in ("showdown", "10k", "masters", "convergence", "championship series", "online series", "nrg", "5k")):
        return "showdown"
    return "locals"


def list_tournaments() -> list[dict]:
    out = []
    page = 1
    while page <= 40:
        url = f"{BASE}/riftbound-tournaments" + (f"?page={page}" if page > 1 else "")
        html = get(url)
        matches = list(re.finditer(r'<tr[^>]*data-href="([^"]+)"[\s\S]*?</tr>', html))
        if not matches:
            break
        oldest = None
        for m in matches:
            block = m.group(0)
            href = m.group(1)
            date_m = re.search(r">(20\d{2}-\d{2}-\d{2})<", block)
            if not date_m:
                continue
            date = date_m.group(1)
            oldest = date
            if date > END or date < START:
                continue
            if "Constructed" not in block:
                continue
            name_m = re.search(r'class="text-white">([^<]+)</a>', block)
            name = clean(name_m.group(1) if name_m else "Unknown event")
            if "Barcelona - Final Standings" in name:
                continue
            nums = re.findall(r"<td>\s*([\d,]+)\s*</td>", block)
            field = int(nums[0].replace(",", "")) if nums else 0
            out.append({"url": href, "date": date, "name": name, "field": field})
        print(f"  index page {page}: {len(matches)} rows, oldest {oldest}", flush=True)
        if oldest and oldest < START:
            break
        page += 1
    # unique by url
    seen = {}
    for t in out:
        seen[t["url"]] = t
    events = sorted(seen.values(), key=lambda t: (-t["field"], t["date"]))
    print(f"tournaments in window: {len(events)}", flush=True)
    return events


def tournament_entries(t: dict) -> list[dict]:
    html = get(t["url"])
    entries = []
    for m in re.finditer(r'<tr[^>]*id="desktop-deck-(\d+)"[^>]*data-href="([^"]+)"[\s\S]*?</tr>', html):
        block = m.group(0)
        href = m.group(2)
        if "Submit Deck" in block or "Decklist Missing" in block or ">N/A<" in block:
            continue
        rank_m = re.search(r"<strong>([^<]+)</strong>", block)
        placing = parse_placing(rank_m.group(1) if rank_m else "")
        if placing is None:
            continue
        if placing > cutoff(t["field"]):
            continue
        player_m = re.search(r"by ([^<\n]+)", block)
        player = ascii_player(player_m.group(1) if player_m else "Unknown")
        entries.append({
            "url": href if href.startswith("http") else urljoin(BASE, href),
            "placing": placing,
            "player": player,
            "event": t["name"],
            "date": t["date"],
            "field": t["field"],
        })
    # page 1 is rank-sorted and has 64 rows — enough for cutoff <= 64
    return entries


def parse_deck(html: str, meta: dict) -> dict | None:
    low = html.lower()
    if "this deck is incomplete" in low or "missing / not available" in low:
        return None
    if "contains banned cards" in low:
        return None
    cards = {"legend": [], "champion": [], "unit": [], "gear": [], "spell": [], "battlefield": [], "rune": [], "sideboard": []}
    kind_map = {
        "legend": "legend", "champion": "champion", "unit": "unit", "gear": "gear",
        "spell": "spell", "battlefield": "battlefield", "battlefields": "battlefield",
        "rune": "rune", "runes": "rune", "sideboard": "sideboard",
    }
    for m in re.finditer(
        r'data-card-type="([a-z]+)"[^>]*data-quantity="(\d+)"[\s\S]*?<a href="/cards/[^"]*">\s*([^<]+?)\s*</a>',
        html,
    ):
        kind = kind_map.get(m.group(1))
        if not kind:
            continue
        cards[kind].append((int(m.group(2)), clean(m.group(3))))
    if not cards["legend"] or not cards["champion"]:
        return None
    if sum(q for q, _ in cards["battlefield"]) != 3:
        return None
    if sum(q for q, _ in cards["rune"]) != 12:
        return None
    main = cards["unit"] + cards["gear"] + cards["spell"]
    main_n = sum(q for q, _ in main)
    if main_n < 38 or main_n > 40:
        return None
    legend = LEGEND_ALIASES.get(cards["legend"][0][1], cards["legend"][0][1])
    champ = cards["champion"][0][1]
    player = meta["player"]
    if player in ("Unknown", ""):
        pm = re.search(r"a deck by <a[^>]*>([^<]+)</a>", html)
        if pm:
            player = ascii_player(pm.group(1))
    placing = meta["placing"]
    date = meta["date"]
    event = meta["event"]
    field = meta["field"]
    # prefer header date/field if present
    hm = re.search(r"(\d+(?:st|nd|rd|th)|Top\s*\d+)\s+at\s+(.+?)\s+(\d+)\s+players on\s+(20\d{2}-\d{2}-\d{2})", html, re.I | re.S)
    if hm:
        placing = parse_placing(hm.group(1)) or placing
        event = clean(re.sub(r"<[^>]+>", "", hm.group(2))) or event
        field = int(hm.group(3))
        date = hm.group(4)
    desc = re.search(r'meta name="description" content="([^"]+)"', html)
    if desc and placing == meta["placing"]:
        dm = re.search(r"(\d+(?:st|nd|rd|th)|Top\s*\d+)\s+at\s+(.+?)\s+by\s+", htmlmod.unescape(desc.group(1)))
        if dm:
            placing = parse_placing(dm.group(1)) or placing
            event = clean(dm.group(2)) or event
    blob_main = " ".join(f"{q} {n}" for q, n in main)
    blob_bf = " ".join(f"{q} {n}" for q, n in cards["battlefield"])
    blob_runes = " ".join(f"{q} {n}" for q, n in cards["rune"])
    blob_sb = " ".join(f"{q} {n}" for q, n in cards["sideboard"])
    if not blob_sb:
        return None
    body = (
        f"Legend: 1 {legend} Champion: 1 {champ} Main Deck: {blob_main} "
        f"Battlefields: {blob_bf} Rune Pool: {blob_runes} Sideboard: {blob_sb}"
    )
    return {
        "player": player,
        "event": event,
        "date": date,
        "placing": placing,
        "field": field,
        "source": "Public riftdecks tournament list",
        "bucket": bucket_for(event),
        "body": body,
        "legend": legend,
        "key": (ascii_player(player).lower(), event.lower(), placing, legend),
    }


def existing_keys() -> set:
    keys = set()
    extra = ROOT / "data/extra-lists.txt"
    if extra.exists():
        text = extra.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(
            r"player:\s*(.+)\nevent:\s*(.+)\ndate:\s*.+\nplacing:\s*(\d+)",
            text,
        ):
            keys.add((ascii_player(m.group(1)).lower(), clean(m.group(2)).lower(), int(m.group(3))))
    return keys


def format_block(d: dict) -> str:
    return (
        f"===\n"
        f"player: {d['player']}\n"
        f"event: {d['event']}\n"
        f"date: {d['date']}\n"
        f"placing: {d['placing']}\n"
        f"field: {d['field']}\n"
        f"source: {d['source']}\n"
        f"bucket: {d['bucket']}\n"
        f"===\n"
        f"{d['body']}\n"
    )


def main():
    print("listing tournaments", flush=True)
    events = list_tournaments()
    seen_url = set()
    candidates = []
    for t in events:
        try:
            ents = tournament_entries(t)
        except Exception as ex:
            print("  skip tournament", t["name"], ex, flush=True)
            continue
        print(f"  {t['date']} {t['name']} field={t['field']} keep={len(ents)}", flush=True)
        for e in ents:
            if e["url"] in seen_url:
                continue
            seen_url.add(e["url"])
            candidates.append(e)
        if len(candidates) >= TARGET * 3:
            break
    # prefer better finishes in bigger rooms
    candidates.sort(key=lambda e: (-e["field"], e["placing"], e["date"]))
    print(f"candidate decks: {len(candidates)}", flush=True)

    extra_players = existing_keys()
    kept = []
    seen_keys = set()
    print(f"fetching sequentially from {len(candidates)} candidates", flush=True)
    for i, entry in enumerate(candidates, 1):
        if len(kept) >= TARGET:
            break
        try:
            html = get(entry["url"])
            d = parse_deck(html, entry)
        except Exception as ex:
            print("  fail", entry["url"], ex, flush=True)
            time.sleep(1)
            continue
        time.sleep(0.28)
        if not d:
            continue
        k = d["key"]
        if k in seen_keys:
            continue
        if (ascii_player(d["player"]).lower(), d["event"].lower(), d["placing"]) in extra_players:
            continue
        seen_keys.add(k)
        kept.append(d)
        if len(kept) % 10 == 0:
            print(f"  kept {len(kept)} after {i} fetches ({d['event']} #{d['placing']} {d['legend']})", flush=True)
    print(f"kept {len(kept)}", flush=True)
    kept.sort(key=lambda d: (d["date"], d["placing"], d["player"]))
    text = "\n".join(format_block(d) for d in kept).rstrip() + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {len(kept)} lists to {OUT}", flush=True)
    from collections import Counter
    print("by legend", Counter(d["legend"] for d in kept).most_common(12))


if __name__ == "__main__":
    main()
