#!/usr/bin/env python3
"""Download official Riftbound legend card images from the Riot card gallery."""
from __future__ import annotations

import json
import re
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "img" / "legends"
GALLERY_PAGE = "https://playriftbound.com/en-us/card-gallery/"


def gallery_json_url() -> str:
    req = urllib.request.Request(GALLERY_PAGE, headers={"User-Agent": "RiftboundDecklists/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", "replace")
    m = re.search(r'"buildId":"([^"]+)"', html)
    if not m:
        raise SystemExit("Could not find Next.js buildId")
    return f"https://playriftbound.com/_next/data/{m.group(1)}/en-us/card-gallery.json"

# LEGEND_META full name -> local filename
TARGETS = {
    "Kennen, Heart of the Tempest": "kennen.jpg",
    "Akali, Rogue Assassin": "akali.jpg",
    "Master Yi, Wuju Bladesman": "yi.jpg",
    "Master Yi, Wuju Master": "yi-master.jpg",
    "Irelia, Blade Dancer": "irelia.jpg",
    "Rengar, Pridestalker": "rengar.jpg",
    "Fiora, Grand Duelist": "fiora.jpg",
    "Azir, Emperor of the Sands": "azir.jpg",
    "Diana, Scorn of the Moon": "diana.jpg",
    "Jayce, Defender of Tomorrow": "jayce.jpg",
    "Ornn, Fire Below the Mountain": "ornn.jpg",
    "Ezreal, Prodigal Explorer": "ezreal.jpg",
    "LeBlanc, Deceiver": "leblanc.jpg",
    "Draven, Glorious Executioner": "draven.jpg",
    "Vex, Gloomist": "vex.jpg",
    "Sett, The Boss": "sett.jpg",
    "Kha'Zix, Voidreaver": "khazix.jpg",
    "Rek'Sai, Void Burrower": "reksai.jpg",
    "Viktor, Herald of the Arcane": "viktor.jpg",
    "Lux, Lady of Luminosity": "lux.jpg",
    "Lillia, Bashful Bloom": "lillia.jpg",
    "Nasus, Curator of the Sands": "nasus.jpg",
    "Pyke, Bloodharbor Ripper": "pyke.jpg",
    "Ambessa, Matriarch of War": "ambessa.jpg",
    "Poppy, Keeper of the Hammer": "poppy.jpg",
    "Vi, Piltover Enforcer": "vi.jpg",
    "Shen, Eye of Twilight": "shen.jpg",
    "Renata Glasc, Chem-Baroness": "renata.jpg",
    "Jax, Grandmaster at Arms": "jax.jpg",
    "Ivern, Green Father": "ivern.jpg",
    "Jhin, Virtuoso": "jhin.jpg",
    "Renekton, Butcher of the Sands": "renekton.jpg",
    "Rumble, Mechanized Menace": "rumble.jpg",
    "Zed, Master of Shadows": "zed.jpg",
    "Sivir, Battle Mistress": "sivir.jpg",
    "Lucian, Purifier": "lucian.jpg",
    "Mel, Soul's Reflection": "mel.jpg",
    "Kai'Sa, Daughter of the Void": "kaisa.jpg",
    "Teemo, Swift Scout": "teemo.jpg",
    "Leona, Radiant Dawn": "leona.jpg",
}

SET_MAX = {"OGN": 298, "OGS": 24, "SFD": 221, "UNL": 219, "VEN": 166}


def subtitle(full: str) -> str:
    if "," in full:
        return full.split(",", 1)[1].strip()
    return full.strip()


def is_legend(card: dict) -> bool:
    types = (card.get("cardType") or {}).get("type") or []
    return any(t.get("id") == "legend" or t.get("label") == "Legend" for t in types)


def score_printing(card: dict) -> tuple:
    code = card.get("publicCode") or ""
    set_id = ((card.get("set") or {}).get("value") or {}).get("id") or ""
    n = int(card.get("collectorNumber") or 0)
    cap = SET_MAX.get(set_id, 999)
    star = 1 if "*" in code else 0
    over = 1 if n > cap else 0
    # Prefer standard frame (not overnumbered, not signature).
    return (star, over, n)


def match_card(cards: list[dict], full: str) -> dict | None:
    sub = subtitle(full).lower()
    legends = [c for c in cards if is_legend(c)]
    hits = []
    for c in legends:
        name = (c.get("name") or "").lower()
        if name == sub or name.startswith(sub + " ") or name.startswith(sub + " -"):
            hits.append(c)
    if not hits:
        # Lux starter is "Lady of Luminosity - Starter"
        for c in legends:
            name = (c.get("name") or "").lower()
            if sub in name:
                hits.append(c)
    if not hits:
        return None
    hits.sort(key=score_printing)
    return hits[0]


def fetch_bytes(url: str, tries: int = 5) -> bytes:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RiftboundDecklists/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as err:
            last = err
            time.sleep(1.5 * (i + 1))
    proc = subprocess.run(
        ["curl", "-fsSL", "--retry", "4", "--retry-delay", "2", url],
        capture_output=True,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout:
        return proc.stdout
    raise last or RuntimeError(f"failed {url}")


def jpeg_url(url: str, width: int = 520) -> str:
    parsed = urllib.parse.urlparse(url)
    q = urllib.parse.parse_qs(parsed.query)
    q["w"] = [str(width)]
    q["fm"] = ["jpg"]
    q["q"] = ["82"]
    return urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(q, doseq=True)))


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

    mapping = {}
    missing = []
    for full, fname in TARGETS.items():
        card = match_card(cards, full)
        if not card:
            missing.append(full)
            print("MISS", full)
            continue
        src = (card.get("cardImage") or {}).get("url")
        if not src:
            missing.append(full)
            print("NOIMG", full)
            continue
        dest = OUT / fname
        if dest.exists() and dest.stat().st_size > 8000:
            print(f"SKIP {full}  ({fname} exists)")
            mapping[full] = {
                "file": fname,
                "code": card.get("publicCode"),
                "officialName": card.get("name"),
                "src": src,
            }
            continue
        jpg = jpeg_url(src)
        print(f"GET  {full}  <- {card.get('publicCode')}  {fname}")
        dest.write_bytes(fetch_bytes(jpg))
        mapping[full] = {
            "file": fname,
            "code": card.get("publicCode"),
            "officialName": card.get("name"),
            "src": src,
        }

    (ROOT / "data" / "official-legend-art.json").write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(mapping)} images. Missing: {missing or 'none'}")


if __name__ == "__main__":
    main()
