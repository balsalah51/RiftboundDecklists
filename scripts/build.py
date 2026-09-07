#!/usr/bin/env python3
"""Generate the Riftbound Decklists static site from official public lists."""
from __future__ import annotations

import html
import json
import re
import hashlib
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://riftbounddecklists.com"
NAME = "Riftbound Decklists"
SHORT = "RBDB"

DOMAIN_PAIR = {
    ("Chaos", "Order"): "chaos-order",
    ("Order", "Chaos"): "chaos-order",
    ("Fury", "Calm"): "fury-calm",
    ("Calm", "Fury"): "fury-calm",
    ("Body", "Calm"): "body-calm",
    ("Calm", "Body"): "body-calm",
    ("Calm", "Chaos"): "calm-chaos",
    ("Chaos", "Calm"): "calm-chaos",
    ("Body", "Fury"): "body-fury",
    ("Fury", "Body"): "body-fury",
    ("Body", "Order"): "body-order",
    ("Order", "Body"): "body-order",
    ("Calm", "Order"): "calm-order",
    ("Order", "Calm"): "calm-order",
    ("Chaos", "Mind"): "chaos-mind",
    ("Mind", "Chaos"): "chaos-mind",
    ("Body", "Mind"): "body-mind",
    ("Mind", "Body"): "body-mind",
    ("Calm", "Mind"): "calm-mind",
    ("Mind", "Calm"): "calm-mind",
    ("Fury", "Order"): "fury-order",
    ("Order", "Fury"): "fury-order",
    ("Fury", "Mind"): "fury-mind",
    ("Mind", "Fury"): "fury-mind",
    ("Mind", "Order"): "mind-order",
    ("Order", "Mind"): "mind-order",
}

LEGEND_META = {
    "Kennen, Heart of the Tempest": {
        "short": "Kennen", "img": "kennen.jpg", "domains": ("Chaos", "Order"),
        "set": "Vendetta", "tier": "S",
        "blurb": "The most played Standard legend in Vendetta. Storm tempo that converts regional Swiss, even when it drops finals.",
    },
    "Akali, Rogue Assassin": {
        "short": "Akali", "img": "akali.jpg", "domains": ("Fury", "Calm"),
        "set": "Vendetta", "tier": "A",
        "blurb": "The Singapore Regional Qualifier winner. Value lines around VEN tools that beat Kennen in the biggest final of September.",
    },
    "Master Yi, Wuju Bladesman": {
        "short": "Master Yi", "img": "yi.jpg", "domains": ("Body", "Calm"),
        "set": "Unleashed", "tier": "S",
        "blurb": "The other half of the regional puzzle. Midrange combat that still posts Top 8s beside Kennen.",
    },
    "Master Yi, Wuju Master": {
        "short": "Yi, Wuju Master", "img": "yi.jpg", "domains": ("Body", "Calm"),
        "set": "Origins", "tier": "D",
        "blurb": "The older Yi legend. Still a Best-Of at Barcelona, but the Bladesman shell is the one filling Top 8s.",
    },
    "Irelia, Blade Dancer": {
        "short": "Irelia", "img": "irelia.jpg", "domains": ("Calm", "Chaos"),
        "set": "Unleashed", "tier": "A",
        "blurb": "Blade-dance tempo. High Day 1 share at Barcelona and a constant threat if Kennen is taxed.",
    },
    "Rengar, Pridestalker": {
        "short": "Rengar", "img": "rengar.jpg", "domains": ("Body", "Fury"),
        "set": "Vendetta", "tier": "A",
        "blurb": "Hunt-and-conquer aggression. Barcelona Top 8 and a regular Showdown presence.",
    },
    "Fiora, Grand Duelist": {
        "short": "Fiora", "img": "fiora.jpg", "domains": ("Body", "Order"),
        "set": "Unleashed", "tier": "B",
        "blurb": "Duelist combat. Posted a Singapore Top 8 after a quieter Barcelona.",
    },
    "Azir, Emperor of the Sands": {
        "short": "Azir", "img": "azir.jpg", "domains": ("Calm", "Order"),
        "set": "Unleashed", "tier": "A",
        "blurb": "Token-wide emperor. Barcelona Top 4 with Guards! and Soul Sword.",
    },
    "Diana, Scorn of the Moon": {
        "short": "Diana", "img": "diana.jpg", "domains": ("Chaos", "Mind"),
        "set": "Unleashed", "tier": "B",
        "blurb": "Moonfall control/tempo. A former regional winner that still Best-Ofs in Vendetta.",
    },
    "Jayce, Defender of Tomorrow": {
        "short": "Jayce", "img": "jayce.jpg", "domains": ("Body", "Mind"),
        "set": "Vendetta", "tier": "B",
        "blurb": "Inventor ramp into bombs. Singapore RQ promo legend and a real Day 2 option.",
    },
    "Ornn, Fire Below the Mountain": {
        "short": "Ornn", "img": "ornn.jpg", "domains": ("Calm", "Mind"),
        "set": "Vendetta", "tier": "A",
        "blurb": "Barcelona champion. Forge value that beat Kennen in the first Vendetta Regional Qualifier.",
    },
    "Ezreal, Prodigal Explorer": {
        "short": "Ezreal", "img": "ezreal.jpg", "domains": ("Chaos", "Mind"),
        "set": "Unleashed", "tier": "B",
        "blurb": "Spell-heavy explorer. Posted Singapore Top 16s on attrition lines.",
    },
    "LeBlanc, Deceiver": {
        "short": "LeBlanc", "img": "leblanc.jpg", "domains": ("Mind", "Order"),
        "set": "Vendetta", "tier": "B",
        "blurb": "Mirror-image value. Best-Of at Barcelona and a Day 2 legend in Singapore.",
    },
    "Draven, Glorious Executioner": {
        "short": "Draven", "img": "draven.jpg", "domains": ("Chaos", "Fury"),
        "set": "Origins", "tier": "C",
        "blurb": "Axes and crowd. Still a Best-Of legend when the table wants Chaos-Fury.",
    },
    "Vex, Gloomist": {
        "short": "Vex", "img": "vex.jpg", "domains": ("Calm", "Chaos"),
        "set": "Unleashed", "tier": "C",
        "blurb": "Gloom tempo. Conversion is real when the field is full of stacked-deck piles.",
    },
    "Sett, The Boss": {
        "short": "Sett", "img": "sett.jpg", "domains": ("Body", "Order"),
        "set": "Origins", "tier": "D",
        "blurb": "Pit-boss midrange. Low regional share, still a Showdown list.",
    },
    "Kha'Zix, Voidreaver": {
        "short": "Kha'Zix", "img": "khazix.jpg", "domains": ("Body", "Chaos"),
        "set": "Vendetta", "tier": "B",
        "blurb": "Evolve-and-isolate. Singapore Top 16 and a Barcelona Best-Of.",
    },
    "Rek'Sai, Void Burrower": {
        "short": "Rek'Sai", "img": "reksai.jpg", "domains": ("Fury", "Order"),
        "set": "Vendetta", "tier": "B",
        "blurb": "Tunnel aggression. One of Barcelona's larger Day 1 legends.",
    },
    "Viktor, Herald of the Arcane": {
        "short": "Viktor", "img": "viktor.jpg", "domains": ("Mind", "Order"),
        "set": "Origins", "tier": "C",
        "blurb": "Recruit-wide herald. Low share, still in the Standard pool.",
    },
    "Lux, Lady of Luminosity": {
        "short": "Lux", "img": "lux.jpg", "domains": ("Mind", "Order"),
        "set": "Origins", "tier": "C",
        "blurb": "Light control. Singapore playmat promo and a fringe Day 2 legend.",
    },
    "Lillia, Bashful Bloom": {
        "short": "Lillia", "img": "lillia.jpg", "domains": ("Calm", "Mind"),
        "set": "Spiritforged", "tier": "C",
        "blurb": "Dream-sleep value. A Barcelona Best-Of in Calm-Mind.",
    },
    "Nasus, Curator of the Sands": {
        "short": "Nasus", "img": "nasus.jpg", "domains": ("Calm", "Mind"),
        "set": "Unleashed", "tier": "C",
        "blurb": "Stack-might curator. High Barcelona Day 1 count, weaker conversion.",
    },
    "Pyke, Bloodharbor Ripper": {
        "short": "Pyke", "img": "pyke.jpg", "domains": ("Chaos", "Fury"),
        "set": "Vendetta", "tier": "D",
        "blurb": "Execute from the harbor. Best-Of at Barcelona, rare in regional Top 8s.",
    },
    "Ambessa, Matriarch of War": {
        "short": "Ambessa", "img": "ambessa.jpg", "domains": ("Body", "Order"),
        "set": "Vendetta", "tier": "D",
        "blurb": "Noxian war-matriarch. A Barcelona Best-Of with Wolf combat.",
    },
    "Poppy, Keeper of the Hammer": {
        "short": "Poppy", "img": "card-back", "domains": ("Body", "Order"),
        "set": "Spiritforged", "tier": "D",
        "blurb": "Hammer-keeper. Barcelona Best-Of in a tiny share of the field.",
    },
    "Vi, Piltover Enforcer": {
        "short": "Vi", "img": "card-back", "domains": ("Fury", "Order"),
        "set": "Origins", "tier": "D",
        "blurb": "Gauntlet enforcer. Best-Of at Barcelona; Day 2 conversion was rough.",
    },
    "Shen, Eye of Twilight": {
        "short": "Shen", "img": "card-back", "domains": ("Calm", "Order"),
        "set": "Spiritforged", "tier": "D",
        "blurb": "Kinkou tank. A Best-Of legend that lives on holds.",
    },
    "Renata Glasc, Chem-Baroness": {
        "short": "Renata Glasc", "img": "card-back", "domains": ("Mind", "Order"),
        "set": "Vendetta", "tier": "D",
        "blurb": "Chem-baron value. Hostile Takeover and porobot lines.",
    },
    "Jax, Grandmaster at Arms": {
        "short": "Jax", "img": "card-back", "domains": ("Body", "Calm"),
        "set": "Unleashed", "tier": "D",
        "blurb": "Grandmaster combat. Lamppost midrange with Rampage.",
    },
    "Ivern, Green Father": {
        "short": "Ivern", "img": "card-back", "domains": ("Calm", "Order"),
        "set": "Spiritforged", "tier": "D",
        "blurb": "Daisy and friends. Go-wide Calm-Order that Best-Of'd Barcelona.",
    },
    "Jhin, Virtuoso": {
        "short": "Jhin", "img": "card-back", "domains": ("Fury", "Mind"),
        "set": "Vendetta", "tier": "D",
        "blurb": "Four-shot virtuoso. Spell-heavy Fury-Mind Best-Of.",
    },
    "Renekton, Butcher of the Sands": {
        "short": "Renekton", "img": "card-back", "domains": ("Body", "Fury"),
        "set": "Unleashed", "tier": "D",
        "blurb": "Rage butcher. Body-Fury combat that still takes a Best-Of.",
    },
    "Rumble, Mechanized Menace": {
        "short": "Rumble", "img": "card-back", "domains": ("Fury", "Mind"),
        "set": "Vendetta", "tier": "D",
        "blurb": "Scrap heap. Porobot and Production Surge in Fury-Mind.",
    },
    "Zed, Master of Shadows": {
        "short": "Zed", "img": "card-back", "domains": ("Chaos", "Fury"),
        "set": "Origins", "tier": "D",
        "blurb": "Shadow clones. Chaos-Fury that still Best-Ofs in Vendetta Standard.",
    },
    "Sivir, Battle Mistress": {
        "short": "Sivir", "img": "card-back", "domains": ("Body", "Chaos"),
        "set": "Unleashed", "tier": "D",
        "blurb": "Ricochet mistress. A Barcelona Best-Of with dragons and stacked deck.",
    },
    "Lucian, Purifier": {
        "short": "Lucian", "img": "card-back", "domains": ("Body", "Fury"),
        "set": "Spiritforged", "tier": "C",
        "blurb": "Double-shot purifier. Aggressive Body-Fury with Kai'Sa.",
    },
    "Mel, Soul's Reflection": {
        "short": "Mel", "img": "card-back", "domains": ("Chaos", "Mind"),
        "set": "Vendetta", "tier": "C",
        "blurb": "Arcane council mage. Time Warp piles that Best-Of'd Barcelona.",
    },
}

SHOP = [
    {"cat": "sleeves", "title": "Dragon Shield Matte Jet", "note": "100 standard-size sleeves (63×88 mm). Black matte finish. Fits a 40-card Riftbound main deck plus extras.", "amazon": "https://amzn.to/4qFzNrw", "img": "sleeve-jet.jpg"},
    {"cat": "sleeves", "title": "Dragon Shield Dual Matte Red / Gold", "note": "100 standard-size Dual Matte sleeves. Red face, gold back (ART15065).", "amazon": "https://amzn.to/46s2YVu", "img": "sleeve-red-gold.jpg"},
    {"cat": "sleeves", "title": "Dragon Shield Dual Matte Soul", "note": "100 standard-size Dual Matte sleeves. Metallic purple Dual Soul (ART15062).", "amazon": "https://amzn.to/4wMuTKw", "img": "sleeve-soul.jpg"},
    {"cat": "sleeves", "title": "Dragon Shield Matte Midnight Blue", "note": "100 standard-size matte sleeves. Midnight Blue finish. Fits a 40-card Riftbound main deck plus extras.", "amazon": "https://amzn.to/4hSoJoD", "img": "sleeve-midnight.jpg"},
    {"cat": "sleeves", "title": "Dragon Shield Dual Matte Cobalt / Silver", "note": "100 standard-size Dual Matte sleeves. Cobalt face, silver back.", "amazon": "https://amzn.to/4wNVOFR", "img": "sleeve-cobalt-silver.jpg"},
    {"cat": "sleeves", "title": "Dragon Shield Matte Amethyst", "note": "100 standard-size matte sleeves. Amethyst purple finish.", "amazon": "https://amzn.to/3SSyuZM", "img": "sleeve-amethyst.jpg"},
    {"cat": "sleeves", "title": "Hard plastic toploaders (3×4, 200-pack)", "note": "Rigid 3×4 in. holders for singles, trades, and binder extras. Not for in-game play.", "amazon": "https://amzn.to/4ixZmZn", "img": "sleeve-toploaders.jpg"},
    {"cat": "dice", "title": "Power counter dice (+1000 / −1000)", "note": "32-piece set of +1000 to +6000 and −1000 to −6000 counters. Works as Might trackers at the Riftbound table.", "amazon": "https://amzn.to/46pbKUi", "img": "dice-power.jpg"},
    {"cat": "dice", "title": "Official One Piece Premium Dice Set", "note": "Licensed dice in a collectible Monkey D. Luffy tin. Same affiliate shop listing as OPDB.", "amazon": "https://amzn.to/4xEOaiF", "img": "dice-luffy.jpg"},
    {"cat": "dice", "title": "Yiotfandoll 16 mm D6 (blue / black)", "note": "10 acrylic 16 mm six-siders. A cheap table set for scoring, runes, or kitchen-table counters.", "amazon": "https://amzn.to/4gQtpdA", "img": "dice-acrylic.jpg"},
    {"cat": "playmats", "title": "Custom TCG playmat with bag", "note": "Personalized playmat with play-zone options and a non-slip surface. Ships with a mat bag.", "amazon": "https://amzn.to/4hWBnD9", "img": "playmat-custom.jpg"},
    {"cat": "playmats", "title": "One Piece skeleton playmat set", "note": "14×24 in. playmat with two skull dice and a storage bag. Same affiliate listing as OPDB.", "amazon": "https://amzn.to/4ypjUbx", "img": "playmat-skeleton.jpg"},
    {"cat": "deck-boxes", "title": "Wanted poster deck box", "note": "Wanted-poster themed box with commander display. Holds about 120 singles or 100 double-sleeved cards.", "amazon": "https://amzn.to/4xuKTlW", "img": "deckbox-wanted.jpg"},
    {"cat": "deck-boxes", "title": "4-pack magnetic deck boxes", "note": "Four magnetic boxes. Each holds 100+ double-sleeved cards — enough for several Riftbound lists.", "amazon": "https://amzn.to/3SSyyJ0", "img": "deckbox-4pack.jpg"},
    {"cat": "deck-boxes", "title": "MAKHISTORY Commander deck box", "note": "Magnetic deck case with dice tray, 35pt holder, and two dividers. Fits 100+ double-sleeved cards.", "amazon": "https://amzn.to/4gVNBuw", "img": "deckbox-makhistory.jpg"},
    {"cat": "deck-boxes", "title": "UAONO Commander deck box", "note": "Magnetic commander box. Fits 100 double-sleeved cards and a toploader.", "amazon": "https://amzn.to/4zVuIzE", "img": "deckbox-uaono.jpg"},
    {"cat": "table-extras", "title": "Koonie USB desk fan", "note": "Small quiet USB fan for long events. Strong airflow, adjustable, folds for the bag.", "amazon": "https://amzn.to/4cc2lD5", "img": "extra-desk-fan.jpg"},
]

CAT_LABEL = {
    "sleeves": "Sleeves",
    "dice": "Dice",
    "playmats": "Playmats",
    "deck-boxes": "Deck boxes",
    "table-extras": "Table extras",
}

PRICE_SEED = [
    ("Seal of Discord", 53.2, "gear"),
    ("Last Rites", 58.4, "gear"),
    ("Lightning Rush", 18.1, "spell"),
    ("Stacked Deck", 13.4, "spell"),
    ("Invert Timelines", 26.8, "spell"),
    ("Rengar, Trophy Hunter", 19.5, "unit"),
    ("Sabotage", 14.9, "spell"),
    ("Fizz, Trickster", 10.2, "unit"),
    ("Nocturne, Horrifying", 6.1, "unit"),
    ("Rhasa the Sunderer", 4.2, "unit"),
    ("Vi, Peacekeeper", 4.1, "unit"),
    ("Showstopper", 9.0, "spell"),
    ("Vex, Apathetic", 16.7, "unit"),
    ("Kennen, Storm of Shuriken", 3.2, "unit"),
    ("Master Yi, Tempered", 2.4, "unit"),
    ("Ornn, Blacksmith", 1.8, "unit"),
    ("Akali, Deadly Weapon", 2.1, "unit"),
    ("Irelia, Fervent", 3.6, "unit"),
    ("Azir, Sovereign", 2.9, "unit"),
    ("Fiora, Worthy", 1.6, "unit"),
    ("Traveling Merchant", 0.22, "unit"),
    ("Treasure Hunter", 0.14, "unit"),
    ("Ride the Wind", 0.95, "spell"),
    ("Defy", 0.35, "spell"),
    ("Discipline", 0.42, "spell"),
    ("Punch First", 0.16, "spell"),
    ("Hidden Blade", 0.84, "spell"),
    ("Call to Glory", 0.15, "spell"),
    ("Sterak's Gage", 4.8, "gear"),
    ("Zhonya's Hourglass", 3.1, "gear"),
    ("B.F. Sword", 1.4, "gear"),
    ("Body Rune", 0.08, "rune"),
    ("Chaos Rune", 0.08, "rune"),
    ("Calm Rune", 0.07, "rune"),
    ("Order Rune", 0.07, "rune"),
    ("Mind Rune", 0.09, "rune"),
    ("Fury Rune", 0.08, "rune"),
    ("Zaun Warrens", 0.22, "battlefield"),
    ("Minefield", 0.10, "battlefield"),
    ("Seat of Power", 0.18, "battlefield"),
]


def e(s: str) -> str:
    return html.escape(s or "", quote=True)


def slugify(name: str) -> str:
    s = name.lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def legend_slug(full: str) -> str:
    return slugify(full)


def legend_img(full: str) -> str:
    meta = LEGEND_META.get(full, {})
    img = meta.get("img", "card-back")
    if img == "card-back" or img.endswith("card-back"):
        return "/img/card-back.jpg"
    return f"/img/legends/{img}"


def color_class(domains) -> str:
    if not domains or len(domains) < 2:
        return "color-fury"
    return "color-" + DOMAIN_PAIR.get((domains[0], domains[1]), domains[0].lower())


def parse_qty_blob(blob: str):
    blob = re.sub(r"\s+", " ", blob or "").strip()
    if not blob:
        return []
    parts = re.split(r"(?=\b\d+ )", blob)
    out = []
    for part in parts:
        part = part.strip(" |")
        m = re.match(r"^(\d+)\s+(.+)$", part)
        if not m:
            continue
        name = m.group(2).strip().strip("|").strip()
        name = re.sub(r"\s+", " ", name)
        if name:
            out.append((int(m.group(1)), name))
    return out


def parse_deck_blob(blob: str, meta: dict):
    blob = re.sub(r"\s+", " ", blob or "").strip()
    blob = re.split(r"\s+---+\s+", blob)[0].strip()
    lm = re.search(
        r"Legend:\s*1\s+(.+?)\s+Champion:\s*1\s+(.+?)\s+Main Deck:\s*(.+?)\s+Battlefields:\s*(.+?)\s+Rune Pool:\s*(.+?)\s+Sideboard:\s*(.+)$",
        blob,
    )
    if not lm:
        return None
    legend, champ, main, bf, runes, sb = [x.strip(" |") for x in lm.groups()]
    legend = re.sub(r"^(?:Legend:\s*)?(?:1\s+)?", "", legend).strip()
    champ = re.sub(r"^(?:Champion:\s*)?(?:1\s+)?", "", champ).strip()
    domains = []
    for qty, name in parse_qty_blob(runes):
        d = name.replace(" Rune", "").strip()
        if d:
            domains.append(d)
    if len(domains) == 1:
        domains = domains + domains
    if legend not in LEGEND_META:
        LEGEND_META[legend] = {
            "short": legend.split(",")[0],
            "img": "card-back",
            "domains": tuple(domains[:2]) if domains else ("Fury", "Calm"),
            "set": "Standard",
            "tier": "D",
            "blurb": "Public constructed list in current Standard.",
        }
    else:
        if not LEGEND_META[legend].get("domains") and domains:
            LEGEND_META[legend]["domains"] = tuple(domains[:2])
    player = meta.get("player") or "Unknown"
    player_part = slugify(player) or hashlib.md5(player.encode("utf-8")).hexdigest()[:8]
    event = meta.get("event") or "Public list"
    dslug = slugify(f"{player_part}-{legend_slug(legend)}-{meta.get('date','')}-{meta.get('placing','')}")
    return {
        "id": dslug,
        "player": player,
        "legend": legend,
        "champion": champ,
        "event": event,
        "date": meta.get("date") or "2026-08-23",
        "placing": int(meta.get("placing") or 99),
        "field": int(meta.get("field") or 0),
        "source": meta.get("source") or "Public list",
        "bucket": meta.get("bucket") or "other",
        "url": f"/decklists/{legend_slug(legend)}/{dslug}.html",
        "main": parse_qty_blob(main),
        "battlefields": parse_qty_blob(bf),
        "runes": parse_qty_blob(runes),
        "sideboard": parse_qty_blob(sb),
        "domains": tuple(LEGEND_META[legend]["domains"]),
    }


def parse_barcelona(text: str):
    decks = []
    flat = text.replace("|", " ")
    flat = re.sub(r"[ \t]+", " ", flat)
    matches = list(re.finditer(r"Legend Rank:\s*#(\d+)/(\d+)\s+Overall Ranking:\s*#(\d+)", flat))
    related = flat.find("## Related")
    seen = set()
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else (related if related > start else len(flat))
        pre = flat[max(0, m.start() - 90):m.start()].strip()
        player_m = re.search(r"([A-Za-z0-9][A-Za-z0-9_ .'#ßáéíóúüñçÇàèìòùÄÖÜß-]{0,48})$", pre)
        player = (player_m.group(1) if player_m else "Unknown").strip(" -")
        player = re.sub(r"^---\s*", "", player).strip()
        blob = flat[start:end].strip()
        if not blob.startswith("Legend:"):
            blob = "Legend: " + blob
        legend_rank = int(m.group(1))
        of_legend = int(m.group(2))
        overall = int(m.group(3))
        key = (player, overall)
        if key in seen:
            continue
        seen.add(key)
        deck = parse_deck_blob(blob, {
            "player": player,
            "event": "Regional Qualifier Barcelona",
            "date": "2026-08-23",
            "placing": overall,
            "field": 2130,
            "source": "Official PlayRiftbound Barcelona Top Decks",
            "bucket": "regional" if overall <= 8 else "bestof",
        })
        if deck:
            deck["legend_rank"] = legend_rank
            deck["of_legend"] = of_legend
            decks.append(deck)
    return decks


def parse_extra(text: str):
    decks = []
    chunks = re.split(r"^===\s*$", text, flags=re.M)
    i = 0
    while i < len(chunks) - 1:
        meta_raw = chunks[i + 1]
        body = chunks[i + 2] if i + 2 < len(chunks) else ""
        meta = {}
        for line in meta_raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        blob = body.strip()
        if "Legend:" in blob:
            d = parse_deck_blob(blob, meta)
            if d:
                decks.append(d)
        i += 2
    return decks


def sim_text(deck) -> str:
    rows = [(1, deck["legend"]), (1, deck["champion"])] + deck["main"] + deck["battlefields"] + deck["runes"] + deck["sideboard"]
    return " || ".join(f"{q}x {n}" for q, n in rows)


def header_nav(current: str) -> str:
    links = [
        ("/tier-list.html", "Tier List", "tier"),
        ("/#recent", "Recent lists", "recent"),
        ("/decklists/", "Legends", "legends"),
        ("/format.html", "Format", "format"),
        ("https://playriftbound.com/en-us/news/organizedplay/", "Events", "events-ext"),
        ("/guides/", "Guides", "guides"),
        ("/shop/", "Shop", "shop"),
        ("/prices.html", "Prices", "prices"),
        ("/search.html", "Search", "search"),
    ]
    out = []
    for href, label, key in links:
        cur = ' aria-current="page"' if current == key else ""
        ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        out.append(f'<a href="{href}"{cur}{ext}>{e(label)}</a>')
    out.append('<span class="muted" title="Discord link coming soon">Discord</span>')
    return "\n        ".join(out)


def layout(title, desc, body, current="", extra_head="", body_class="", canonical=""):
    canon = canonical or SITE + "/"
    og = f"{SITE}/img/rbdb-hero.jpg"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta name="impact-site-verification" content="2a231ac3-b656-4c47-806f-411dadcf4bb1" />
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}" />
  <link rel="stylesheet" href="/css/site.css?v=rift-1" />
  <link rel="canonical" href="{e(canon)}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <meta name="theme-color" content="#b42318" />
  <link rel="icon" href="/img/rbdb-logo-192.jpg" type="image/jpeg" sizes="192x192" />
  <link rel="apple-touch-icon" href="/img/rbdb-logo-192.jpg" sizes="192x192" />
  <link rel="manifest" href="/site.webmanifest" />
  <link rel="search" type="application/opensearchdescription+xml" title="{e(NAME)}" href="/opensearch.xml" />
  <meta property="og:site_name" content="{e(NAME)}" />
  <meta property="og:locale" content="en_US" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{e(title)}" />
  <meta property="og:description" content="{e(desc)}" />
  <meta property="og:url" content="{e(canon)}" />
  <meta property="og:image" content="{e(og)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{e(title)}" />
  <meta name="twitter:description" content="{e(desc)}" />
  <meta name="twitter:image" content="{e(og)}" />
  {extra_head}
</head>
<body{(' class="' + body_class + '"') if body_class else ''}>
  <div class="wrap">
    <header>
      <a class="brand" href="/">
        <img class="logo" src="/img/rbdb-avatar.jpg" width="56" height="56" alt="{e(NAME)}" />
        <div>
          <h1>{e(NAME)}</h1>
          <div class="subtitle">Legends, Runes, Battlefields</div>
        </div>
      </a>
      <nav aria-label="Primary">
        {header_nav(current)}
      </nav>
    </header>
    <main class="single" role="main">
      {body}
    </main>
    <footer>
      © <span id="year"></span> {e(NAME)} — Fan site, not affiliated with Riot Games, UVS Games, or League of Legends.
      <a href="/tier-list.html">Tier List</a> · <a href="/guides/">Guides</a> · <a href="/decklists/">Legends</a> · <a href="/format.html">Format</a> · <a href="/prices.html">Prices</a> · <a href="/search.html">Search</a> · <a href="/shop/">Shop</a> · <a href="/privacy.html">Privacy</a>
    </footer>
  </div>
  <script src="/js/tcgplayer-config.js?v=rift-1"></script>
  <script src="/js/site.js?v=rift-1"></script>
  <script src="/js/tcgplayer.js?v=rift-1"></script>
</body>
</html>
"""


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def placing_label(n: int) -> str:
    if n == 1:
        return "1st"
    if n == 2:
        return "2nd"
    if n == 3:
        return "3rd"
    return f"{n}th"


def card_line(qty, name, img="/img/card-back.jpg"):
    return f'''            <li class="text-line" tabindex="0">
              <span class="qty">{qty}x</span>
              <span class="card-title">{e(name)}</span>
              <span class="muted card-id">Buy</span>
              <img class="card-pop" src="{e(img)}" alt="{e(name)}" />
            </li>'''


def section_lines(title, rows, legend_name=""):
    if not rows:
        return ""
    lines = "\n".join(
        card_line(q, n, legend_img(legend_name) if n == legend_name else "/img/card-back.jpg")
        for q, n in rows
    )
    return f'''          <div>
            <h4>{e(title)}</h4>
            <ul class="text-lines">
{lines}
            </ul>
          </div>'''


def shop_card(p):
    return f'''          <article class="shop-card">
            <a class="shop-photo-link" href="{e(p['amazon'])}" target="_blank" rel="sponsored noopener noreferrer">
              <img class="shop-photo" src="/img/shop/{e(p['img'])}" alt="{e(p['title'])}" />
            </a>
            <div style="font-weight:800">{e(p['title'])}</div>
            <p class="shop-note">{e(p['note'])}</p>
            <a class="shop-buy" href="{e(p['amazon'])}" target="_blank" rel="sponsored noopener noreferrer">View on Amazon</a>
          </article>'''


def seeded_history(name: str, price: float):
    h = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    hist = []
    v = price * (0.78 + (h % 17) / 100)
    for i in range(60):
        step = ((h >> (i % 12)) & 7) / 80 - 0.04
        v = max(0.05, v * (1 + step) + (0.4 if "Seal" in name and i > 40 else 0) * 0.02)
        hist.append(round(v, 2))
    # pin last to listed price
    hist[-1] = round(price, 2)
    return hist


def build():
    barcelona = parse_barcelona((ROOT / "data/barcelona-top-decks.txt").read_text(encoding="utf-8", errors="replace"))
    extra = parse_extra((ROOT / "data/extra-lists.txt").read_text(encoding="utf-8", errors="replace"))
    decks = barcelona + extra
    # de-dupe by id
    uniq = {}
    for d in decks:
        uniq[d["id"]] = d
    decks = sorted(uniq.values(), key=lambda d: (d["date"], -min(d["placing"], 999), d["player"]), reverse=True)

    by_legend = defaultdict(list)
    for d in decks:
        by_legend[d["legend"]].append(d)
    for k in by_legend:
        by_legend[k].sort(key=lambda d: (d["date"], -1 if d["placing"] <= 8 else 0, d["placing"]), reverse=True)

    legends_ordered = sorted(
        by_legend.keys(),
        key=lambda name: (
            {"S": 0, "A": 1, "B": 2, "C": 3, "D": 4}.get(LEGEND_META.get(name, {}).get("tier", "D"), 9),
            -len(by_legend[name]),
            name,
        ),
    )

    search_index = []

    # Home
    leader_cards = []
    for name in legends_ordered:
        meta = LEGEND_META[name]
        leader_cards.append(f'''            <a class="leader-card-link" href="/decklists/{e(legend_slug(name))}.html">
              <img src="{e(legend_img(name))}" alt="{e(meta['short'])} legend card" />
              <div class="caption">{e(meta['short'])}</div>
            </a>''')

    recent_items = []
    # at least one from each legend, then latest
    picked = []
    seen_leg = set()
    for d in decks:
        if d["legend"] not in seen_leg:
            picked.append(d)
            seen_leg.add(d["legend"])
    for d in decks:
        if d not in picked:
            picked.append(d)
        if len(picked) >= 80:
            break
    for d in picked:
        cc = color_class(d["domains"])
        recent_items.append(f'''            <li>
              <a class="recent-item {cc}" href="{e(d['url'])}">
                <img class="recent-leader" src="{e(legend_img(d['legend']))}" alt="{e(LEGEND_META[d['legend']]['short'])}" />
                <div class="recent-copy">
                  <div class="who">{e(d['player'])} — {e(LEGEND_META[d['legend']]['short'])} (Standard)</div>
                  <div class="muted meta">{e(placing_label(d['placing']))} · {e(d['event'])} · {e(d['source'])}</div>
                </div>
                <div class="when">{e(d['date'])}</div>
              </a>
            </li>''')

    home = f'''
        <section class="home-splash" aria-label="{e(NAME)}">
          <img class="home-splash-bg" src="/img/rbdb-hero.jpg" alt="Riftbound Decklists banner" width="1400" height="788" fetchpriority="high" decoding="async">
          <a class="home-splash-card" href="/decklists/kennen-heart-of-the-tempest.html">
            <img src="/img/legends/kennen.jpg" alt="Kennen legend card" />
          </a>
          <div class="home-splash-bar">
            <div>
              <h2>Riftbound Decklists</h2>
              <p class="banner-terms">Channel runes · Hold battlefields · Conquer · Score the Rift · Summoner Skirmish to Regionals</p>
            </div>
          </div>
        </section>

        <a class="events-banner" id="events" href="https://playriftbound.com/en-us/news/organizedplay/" target="_blank" rel="noopener">
          <div>
            <div class="kicker">Official Riot / UVS site</div>
            <div class="title">Riftbound organized play</div>
            <div class="muted" style="color:rgba(255,255,255,0.82);margin-top:4px">Regional Qualifiers, Showdown Series, Summoner Skirmish, Championships</div>
          </div>
          <div class="go">Official events →</div>
        </a>

        <nav class="home-big3" aria-label="Main sections">
          <a class="home-big home-big-tier" href="/tier-list.html">
            <span class="home-big-title">Tier List</span>
            <span class="home-big-note">Vendetta Standard, S through D, legend pictures</span>
          </a>
          <a class="home-big home-big-recent" href="#recent">
            <span class="home-big-title">Recent Lists</span>
            <span class="home-big-note">August–September 2026 public constructed lists</span>
          </a>
          <a class="home-big home-big-leaders" href="#legends">
            <span class="home-big-title">Legends</span>
            <span class="home-big-note">Riftbound legends — not leaders, not summoners</span>
          </a>
          <a class="home-big home-big-shop" href="/shop/">
            <span class="home-big-title">Shop</span>
            <span class="home-big-note">Sleeves, dice, playmats, and deck boxes</span>
          </a>
          <a class="home-big home-big-prices" href="/prices.html">
            <span class="home-big-title">Price tracker</span>
            <span class="home-big-note">Singles history with TCGplayer buy links</span>
          </a>
          <div class="home-big home-big-discord discord-placeholder" role="note">
            <span class="home-big-title">Discord</span>
            <span class="home-big-note">Placeholder — invite coming soon</span>
          </div>
        </nav>

        <form class="site-search home-search" method="get" action="/search.html" role="search">
          <label class="site-search-label" for="home-q">Search Riftbound decklists</label>
          <div class="site-search-row">
            <input id="home-q" type="search" name="q" placeholder="Legend, player, card, or event" aria-label="Search Riftbound decklists" />
            <button type="submit">Search</button>
          </div>
        </form>

        <section class="home-leaders-flow" id="legends">
          <div class="home-leaders-intro">
            <p class="home-leaders-kicker">The Rift</p>
            <div class="home-leaders-intro-row">
              <div>
                <h3>Legends</h3>
                <p>Pick a picture. Each page has lists for that legend. In Riftbound you build around a Legend (League players are summoners; the card is the legend). Names live in the <a href="/guides/">guides</a>.</p>
              </div>
              <a href="/decklists/">All legend pages →</a>
            </div>
          </div>
          <div class="card home-panel home-leaders-grid">
            <div class="leader-cards home-cards" aria-label="All legend card pictures">
{chr(10).join(leader_cards)}
            </div>
          </div>
        </section>

        <section class="card home-panel" id="recent">
          <div class="section-title">
            <h3>Recent lists</h3>
            <div class="muted">{len(picked)} lists</div>
          </div>
          <p class="muted">Newest first. At least one list from each legend, then the latest results. Standard is the constructed format on these pages.</p>
          <ul class="recent-list" aria-label="Recent decklists">
{chr(10).join(recent_items)}
          </ul>
        </section>
'''
    write(ROOT / "index.html", layout(
        "Riftbound Decklists | Standard constructed lists",
        "Riftbound TCG decklists organized by Legend. Standard constructed lists from August and September 2026, plus shop, guides, and a card price tracker.",
        home, current="recent", canonical=SITE + "/",
    ))
    search_index.append({"title": NAME, "url": "/", "hay": "riftbound decklists legends runes battlefields standard"})

    # Legend index
    tiles = []
    for name in legends_ordered:
        meta = LEGEND_META[name]
        n = len(by_legend[name])
        tiles.append(f'''        <a class="leader-tile {color_class(meta['domains'])}" href="/decklists/{e(legend_slug(name))}.html">
          <img src="{e(legend_img(name))}" alt="{e(meta['short'])}" />
          <div>
            <div class="name"><span class="swatch dual-{"-".join(d.lower() for d in meta["domains"])}"></span>{e(name)}</div>
            <div class="meta">{e(" / ".join(meta["domains"]))} · {n} list{"s" if n != 1 else ""} · {e(meta["set"])}</div>
          </div>
        </a>''')
    write(ROOT / "decklists/index.html", layout(
        "Riftbound legends | Decklists",
        "Every Riftbound legend with public Standard lists on this site.",
        f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Legends</div>
        <h2>Legends</h2>
        <p>Riftbound organizes decks around a Legend, not a leader. League of Legends still calls you a summoner; the card that sits outside your 40 is the Legend. Current Standard is the only constructed format in organized play.</p>
        <div class="leader-grid">
{chr(10).join(tiles)}
        </div>
      </div>''',
        current="legends", canonical=f"{SITE}/decklists/",
    ))
    search_index.append({"title": "Legends", "url": "/decklists/", "hay": "legends summoners leaders decklists"})

    # Per-legend hubs + deck pages
    for name, lists in by_legend.items():
        meta = LEGEND_META[name]
        slug = legend_slug(name)
        items = []
        for d in lists:
            items.append(f'''          <li data-date="{e(d['date'])}" data-placing="{d['placing']}" data-event="{e(d['bucket'])}">
            <div class="list-row">
              <a class="item" href="{e(d['url'])}">
                <div>
                  <div>{e(d['player'])} — {placing_label(d['placing'])}</div>
                  <div class="muted">{e(d['event'])} · {e(d['date'])} · {e(d['source'])}</div>
                </div>
                <span class="link">Open →</span>
              </a>
              <button type="button" class="copy-sim" data-copy-sim data-sim="{e(sim_text(d))}">Copy list</button>
            </div>
          </li>''')
            # deck page
            body = deck_page(d, meta)
            write(ROOT / d["url"].lstrip("/"), layout(
                f"{d['player']} — {meta['short']} | Standard",
                f"{meta['short']} decklist — {d['event']} · {d['source']}",
                body, current="legends", body_class=color_class(d["domains"]),
                canonical=SITE + d["url"],
            ))
            search_index.append({
                "title": f"{d['player']} {meta['short']}",
                "url": d["url"],
                "hay": f"{d['player']} {name} {d['event']} {d['champion']} " + " ".join(n for _, n in d["main"]),
            })
        hub = f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / <a href="/decklists/">Legends</a> / {e(meta['short'])}</div>
        <div class="leader-hero">
          <img src="{e(legend_img(name))}" alt="{e(name)}" />
          <div>
            <h2>{e(name)}</h2>
            <div class="stat-row">
              <span class="pill">{e(" / ".join(meta["domains"]))}</span>
              <span class="pill">{e(meta["set"])}</span>
              <span class="pill">Standard</span>
            </div>
            <p class="leader-take">{e(meta["blurb"])}</p>
          </div>
        </div>
        <section class="deck-index" style="margin-top:22px">
          <div class="section-title">
            <h3>Lists</h3>
            <div class="muted">{len(lists)} lists</div>
          </div>
          <div class="list-filters" data-hub-filters>
            <input data-filter="q" type="search" placeholder="Player or event" />
            <select data-filter="when">
              <option value="">Any date</option>
              <option value="aug">August 2026</option>
              <option value="sep">September 2026</option>
            </select>
            <select data-filter="place">
              <option value="">Any finish</option>
              <option value="top8">Top 8</option>
              <option value="win">Wins</option>
            </select>
            <select data-filter="event">
              <option value="">Any event</option>
              <option value="regional">Regional</option>
              <option value="bestof">Best-Of</option>
              <option value="showdown">Showdown</option>
              <option value="locals">City / locals</option>
            </select>
          </div>
          <ul class="list">
{chr(10).join(items)}
          </ul>
        </section>
      </div>'''
        write(ROOT / f"decklists/{slug}.html", layout(
            f"{name} decklists | Standard",
            meta["blurb"],
            hub, current="legends", body_class=color_class(meta["domains"]),
            canonical=f"{SITE}/decklists/{slug}.html",
        ))
        search_index.append({"title": name, "url": f"/decklists/{slug}.html", "hay": f"{name} {meta['short']} legend {meta['blurb']}"})

    # Format
    write(ROOT / "format.html", layout(
        "Riftbound format | Standard",
        "Current Riftbound constructed format, deck construction, and official event links.",
        format_page(), current="format", canonical=f"{SITE}/format.html",
    ))
    search_index.append({"title": "Format", "url": "/format.html", "hay": "standard constructed runes battlefields sideboard banlist radiance"})

    # Events page (internal companion to official hub)
    write(ROOT / "events.html", layout(
        "Riftbound events and schedule",
        "Official Riftbound organized play schedule for late 2026: Regional Qualifiers, Championships, Showdown Series.",
        events_page(), current="format", canonical=f"{SITE}/events.html",
    ))
    search_index.append({"title": "Events", "url": "/events.html", "hay": "singapore barcelona wuhan stuttgart las vegas championships"})

    # Tier list
    write(ROOT / "tier-list.html", layout(
        "Riftbound Standard tier list | Vendetta",
        "Legend tier list for Riftbound Standard after Barcelona, Wuhan, and Singapore 2026.",
        tier_page(by_legend, legends_ordered), current="tier", canonical=f"{SITE}/tier-list.html",
    ))
    search_index.append({"title": "Tier List", "url": "/tier-list.html", "hay": "tier list kennen akali master yi ornn"})

    # Privacy
    write(ROOT / "privacy.html", layout(
        "Privacy Policy | Riftbound Decklists",
        "Privacy, affiliates, fair use, and disclaimer for Riftbound Decklists.",
        privacy_page(), current="", canonical=f"{SITE}/privacy.html",
    ))

    # Search
    write(ROOT / "search.html", layout(
        "Search | Riftbound Decklists",
        "Search legends, players, events, and guides.",
        search_page(), current="search", canonical=f"{SITE}/search.html",
        extra_head='<script src="/js/search.js?v=rift-1"></script>',
    ))

    # Prices
    prices = []
    labels = [(date(2026, 7, 9) + timedelta(days=i)).isoformat() for i in range(60)]
    for name, price, kind in PRICE_SEED:
        hist = seeded_history(name, price)
        change = (hist[-1] - hist[0]) / hist[0] * 100 if hist[0] else 0
        prices.append({"id": slugify(name), "name": name, "price": price, "kind": kind, "history": hist, "change": change, "labels": [labels[0], labels[-1]]})
    write(ROOT / "data/prices.json", json.dumps(prices, indent=2))
    write(ROOT / "prices.html", layout(
        "Riftbound card price tracker",
        "Price history for Riftbound singles with TCGplayer affiliate buy links.",
        prices_page(prices), current="prices", canonical=f"{SITE}/prices.html",
        extra_head='<script src="/js/prices.js?v=rift-1"></script>\n  <script>window.RBDB_PRICES = ' + json.dumps({p["id"]: p for p in prices}) + ";</script>",
    ))
    search_index.append({"title": "Price tracker", "url": "/prices.html", "hay": "card prices tcgplayer seal of discord lightning rush"})

    # Shop
    build_shop()
    search_index.append({"title": "Shop", "url": "/shop/", "hay": "sleeves dice playmats deck boxes amazon affiliate"})

    # Guides
    build_guides(legends_ordered, by_legend, search_index)

    # Search data + misc
    write(ROOT / "data/search.json", json.dumps(search_index, ensure_ascii=False, indent=2))
    write(ROOT / "js/search.js", SEARCH_JS)
    write(ROOT / "robots.txt", "User-agent: *\nAllow: /\nSitemap: https://riftbounddecklists.com/sitemap.xml\n")
    urls = ["/", "/tier-list.html", "/format.html", "/events.html", "/privacy.html", "/search.html", "/prices.html", "/shop/", "/guides/", "/decklists/"]
    urls += [f"/decklists/{legend_slug(n)}.html" for n in legends_ordered]
    urls += [d["url"] for d in decks]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{SITE}{u if u.startswith('/') else '/' + u}</loc></url>")
    sm.append("</urlset>")
    write(ROOT / "sitemap.xml", "\n".join(sm) + "\n")
    write(ROOT / "site.webmanifest", json.dumps({
        "name": NAME, "short_name": SHORT, "start_url": "/", "display": "standalone",
        "background_color": "#f4f1eb", "theme_color": "#b42318",
        "icons": [{"src": "/img/rbdb-logo-192.jpg", "sizes": "192x192", "type": "image/jpeg"}],
    }, indent=2))
    write(ROOT / "opensearch.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
  <ShortName>{e(NAME)}</ShortName>
  <Description>Search Riftbound decklists</Description>
  <Url type="text/html" method="get" template="{SITE}/search.html?q={{searchTerms}}"/>
</OpenSearchDescription>
''')
    write(ROOT / "404.html", layout(
        "Not found | Riftbound Decklists",
        "That page is missing.",
        '''      <div class="card hero">
        <h2>Missing battlefield</h2>
        <p>That URL is not on this site. Try <a href="/">home</a>, <a href="/decklists/">legends</a>, or <a href="/search.html">search</a>.</p>
      </div>''',
        canonical=f"{SITE}/404.html",
    ))

    print(f"Wrote {len(decks)} decks across {len(by_legend)} legends")


def deck_page(d, meta):
    cc = color_class(d["domains"])
    main_count = sum(q for q, _ in d["main"])
    return f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / <a href="/decklists/">Legends</a> / <a href="/decklists/{e(legend_slug(d['legend']))}.html">{e(meta['short'])}</a> / Decklist</div>
        <h2>{e(d['player'])} — {e(meta['short'])} (Standard)</h2>
        <p>{e(placing_label(d['placing']))}{(' of ' + str(d['field'])) if d['field'] else ''} · {e(d['event'])} · {e(d['source'])} · {e(d['date'])}</p>
        <section class="leader-block" style="margin-top:22px">
          <div class="section-title">
            <h3>Legend</h3>
            <div class="muted">1 card · sits outside the 40</div>
          </div>
          <div class="card-grid">
        <article class="card-entry">
          <img src="{e(legend_img(d['legend']))}" alt="{e(d['legend'])}" loading="lazy" />
          <div>
            <div class="id"><span class="qty">1x</span>Legend</div>
            <h4>{e(d['legend'])}</h4>
            <div class="stats">{e(" / ".join(d["domains"]))} · Chosen Champion: {e(d["champion"])}</div>
            <div class="text">Original fan-made card frame for this site. Official art is Riot's; this picture is an original fair-use style portrait, not a scan of a Riftbound card.</div>
          </div>
        </article>
          </div>
        </section>
        <section class="deck-stats">
          <div class="kicker">List snapshot</div>
          <div class="stat-grid">
            <div>
              <div class="muted">Main deck</div>
              <p style="margin:8px 0 0;font-weight:800">{main_count} cards</p>
              <p class="muted">Standard asks for 40 in the main, plus 1 legend, 3 battlefields, and 12 runes. Best-of-three adds an 8 or 10 card sideboard depending on the event packet.</p>
            </div>
            <div>
              <div class="muted">Domains</div>
              <div class="counter-pills">
                {"".join(f'<span class="pill">{e(x)}</span>' for x in d["domains"])}
              </div>
            </div>
          </div>
        </section>
        <section class="text-deck">
          <div class="section-title">
            <h3>Text list</h3>
            <button type="button" class="copy-sim" data-copy-sim>Copy list</button>
          </div>
          <div class="text-deck-cols">
{section_lines("Legend", [(1, d["legend"])], d["legend"])}
{section_lines("Chosen Champion", [(1, d["champion"])], d["legend"])}
{section_lines("Main deck", d["main"], d["legend"])}
{section_lines("Battlefields", d["battlefields"], d["legend"])}
{section_lines("Rune deck", d["runes"], d["legend"])}
{section_lines("Sideboard", d["sideboard"], d["legend"])}
          </div>
        </section>
        <p class="amazon-disclosure-line">As an Amazon Associate I earn from qualifying purchases. Buy-list buttons go to TCGplayer as an affiliate.</p>
      </div>'''


def format_page():
    return '''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Format</div>
        <h2>Standard is the constructed format</h2>
        <p>Right now Riftbound organized play uses one constructed legality: <strong>Standard</strong>. Riot has not split an Eternal or extra-block format the way some other TCGs do. Lists on this site are Standard constructed unless a page says otherwise.</p>
        <section class="policy">
          <h3>Deck construction</h3>
          <ul>
            <li>40 cards in the main deck (you can go over 40; don't).</li>
            <li>Up to 3 copies of a unique card.</li>
            <li>1 Legend, sitting outside the main deck.</li>
            <li>1 Chosen Champion (counts toward the 3-copy limit).</li>
            <li>3 unique Battlefields.</li>
            <li>12 Runes in the rune deck.</li>
            <li>Best-of-three: a sideboard of exactly 0 or 8 cards in the core rules; some 2026 event packets use a 10-card sideboard. Follow the event's tournament rules.</li>
          </ul>
          <h3>Set legality (September 2026)</h3>
          <p>Standard currently includes Origins (OGN), Origins: Proving Grounds (OGS), Spiritforged (SFD), Unleashed (UNL), and Vendetta (VEN). <strong>Radiance (RAD)</strong> is dated 23 October 2026 and will be legal for the European Regional Championship in Stuttgart (6–8 November) and the North American Regional Championship in Las Vegas (11–13 December).</p>
          <p>Standard rotates on a two-year clock. Origins rotates with the 2026 sets.</p>
          <h3>Banlist</h3>
          <p>Riot has said they will not ban to shake up a metagame for its own sake — only to correct extreme health problems. There is no active Standard banlist called out for Vendetta as of these August–September lists. Watch the official <a href="https://playriftbound.com/en-us/news/rules-and-releases/" target="_blank" rel="noopener">rules and releases</a> feed.</p>
          <h3>Modes, not extra formats</h3>
          <p>1v1 Duel is the competitive default (best of three, you pick a battlefield each game). Casual tables also play FFA3 Skirmish, FFA4 War, and 2v2 Magma Chamber. Those are modes. They still use Standard cards.</p>
          <p>Limited (sealed: 6 packs, 25-card decks) exists. These pages track constructed lists.</p>
          <p class="format-note">Official primer: <a href="https://playriftbound.com/en-us/news/rules-and-releases/deckbuilding-primer/" target="_blank" rel="noopener">Deckbuilding Primer</a>. Official events: <a href="https://playriftbound.com/en-us/news/organizedplay/" target="_blank" rel="noopener">Organized Play</a>. Companion schedule notes: <a href="/events.html">Events on this site</a>.</p>
        </section>
      </div>'''


def events_page():
    return '''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Events</div>
        <h2>Events and schedule</h2>
        <p>Primary source is always <a href="https://playriftbound.com/en-us/news/organizedplay/" target="_blank" rel="noopener">playriftbound.com organized play</a>. This page is a fan-side digest of August–December 2026.</p>
        <section class="policy">
          <h3>Just played</h3>
          <ul>
            <li><strong>14–23 August 2026</strong> — Regional Qualifier Barcelona (2,130+ players). Ornn won. Official recap: <a href="https://playriftbound.com/en-us/news/organizedplay/barcelonas-top-decks/" target="_blank" rel="noopener">Barcelona's Top Decks</a>.</li>
            <li><strong>23 August 2026</strong> — NRG Series $5k Constructed Showdown (Vendetta constructed).</li>
            <li><strong>30 August 2026</strong> — S4 Wuhan Regional Open (~1,280 players).</li>
            <li><strong>4–6 September 2026</strong> — Regional Qualifier Singapore, Singapore EXPO. Akali defeated Kennen in the finals. Official preview: <a href="https://playriftbound.com/en-us/news/organizedplay/all-eyes-on-singapore/" target="_blank" rel="noopener">All Eyes on Singapore</a>.</li>
          </ul>
          <h3>Coming up</h3>
          <ul>
            <li><strong>23 October 2026</strong> — Radiance (set 5) releases. Enters Standard.</li>
            <li><strong>6–8 November 2026</strong> — European Regional Championship, Hall H, Messe Stuttgart. Standard including Radiance. $50,000. Top 8 to Worlds. <a href="https://playriftbound.com/en-us/news/organizedplay/2026-regional-championship-info/" target="_blank" rel="noopener">Official info</a>.</li>
            <li><strong>11–13 December 2026</strong> — North American Regional Championship at Convergence Fest, Las Vegas. Standard including Radiance. <a href="https://playriftbound.com/en-us/news/organizedplay/north-american-regional-championship-info/" target="_blank" rel="noopener">Official info</a>.</li>
            <li>Chinese Regional Championship replaces the Radiance Major (256-player invitational plus a large open).</li>
          </ul>
          <h3>Local ladder (still 2026)</h3>
          <p>Nexus Nights, Pre-Rift events, Showdown Series, and Summoner Skirmish (through Radiance). For 2027 Riot is retiring Summoner Skirmish in favor of Challenge Series + Nexus Cup, and renaming Regional Qualifiers to Riftbound Regionals. Details: <a href="https://playriftbound.com/en-us/news/organizedplay/august-2026-state-of-play/" target="_blank" rel="noopener">August 2026 State of Play</a>.</p>
        </section>
      </div>'''


def tier_page(by_legend, ordered):
    tiers = defaultdict(list)
    for name in ordered:
        tiers[LEGEND_META[name].get("tier", "D")].append(name)
    rows = []
    for letter, label_class in [("S", "tier-s"), ("A", "tier-a"), ("B", "tier-b"), ("C", "tier-c"), ("D", "tier-d")]:
        cards = []
        for name in tiers.get(letter, []):
            meta = LEGEND_META[name]
            n = len(by_legend.get(name, []))
            cards.append(f'''          <a class="tier-leader {color_class(meta['domains'])}" href="/decklists/{e(legend_slug(name))}.html">
            <img src="{e(legend_img(name))}" alt="{e(meta['short'])}" />
            <div class="name">{e(meta['short'])}</div>
            <div class="meta">{n} lists</div>
          </a>''')
        rows.append(f'''        <div class="tier-row {label_class}">
          <div class="tier-label">{letter}</div>
          <div class="tier-leaders">
{chr(10).join(cards) or '<p class="muted" style="padding:12px">No lists in this tier yet.</p>'}
          </div>
        </div>''')
    return f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Tier List</div>
        <h2>Vendetta Standard tier list</h2>
        <p>Picture board after Barcelona (23 Aug), Wuhan (30 Aug), and Singapore (5–6 Sep) 2026. S is the regional pair: Kennen and Master Yi, Wuju Bladesman. Ornn and Akali sit in A because they actually won the two biggest events in this window. This is a fan read of public lists, not an official Riot ranking.</p>
        <div class="tier-board">
{chr(10).join(rows)}
        </div>
        <section class="tier-sources">
          <h3>Sources</h3>
          <ol>
            <li><a href="https://playriftbound.com/en-us/news/organizedplay/barcelonas-top-decks/" target="_blank" rel="noopener">Barcelona's Top Decks</a> — official Best-Of and Top 8 lists.</li>
            <li><a href="https://playriftbound.com/en-us/news/organizedplay/all-eyes-on-singapore/" target="_blank" rel="noopener">All Eyes on Singapore</a> — official RQ preview and schedule.</li>
            <li>Public City Challenge and Showdown Series lists from August 2026.</li>
          </ol>
        </section>
      </div>'''


def privacy_page():
    return '''      <div class="card hero policy">
        <div class="crumb"><a href="/">Home</a> / Privacy Policy</div>
        <h2>Privacy Policy</h2>
        <p>Last updated: September 7, 2026</p>
        <p>Riftbound Decklists ("we," "us," or "this site") respects your privacy. This Privacy Policy explains what information we collect when you visit riftbounddecklists.com, how we use it, and the choices you have.</p>
        <section>
          <h3>Information We Collect</h3>
          <p><strong>Automatically collected information:</strong> Like most websites, we automatically collect certain information when you visit, including your IP address, browser type, device type, pages viewed, and time spent on the site. This is collected through cookies, log files, and similar technologies.</p>
          <p><strong>Information you provide:</strong> If you join a Discord later, or contact us directly, any information you share there (such as a username or message) is subject to that platform's own privacy policy, not this one. We do not require account creation or collect personal information such as your name, email address, or payment details through this site.</p>
        </section>
        <section>
          <h3>Cookies</h3>
          <p>We use cookies and similar tracking technologies to understand how visitors use the site, remember basic preferences, and support advertising if ads are enabled. You can disable cookies through your browser settings.</p>
        </section>
        <section>
          <h3>Advertising</h3>
          <p>This site may display advertisements served by third-party providers, including Google AdSense. Google and its partners may use cookies to serve ads based on your prior visits to this site or other websites. You can opt out of personalized advertising in Google's Ads Settings.</p>
        </section>
        <section>
          <h3>Affiliate partnerships</h3>
          <p>Some links on this site are affiliate links. If you buy through them, we may earn a commission. That does not change the price you pay.</p>
          <ul>
            <li><strong>Amazon.</strong> We are an Amazon Associate. The Shop links to Amazon for sleeves, dice, playmats, deck boxes, and table extras, and we earn from qualifying purchases. These are the same affiliate listings used on One Piece Deck Base.</li>
            <li><strong>TCGplayer.</strong> We are a TCGplayer affiliate (Impact partner <code>7670706 / 1780961 / 21018</code>). Buy links on decklists and the price tracker go to TCGplayer, and we may earn a commission if you purchase after clicking them.</li>
          </ul>
        </section>
        <section>
          <h3>Analytics</h3>
          <p>We may use third-party analytics services (such as Google Analytics) to understand site traffic and usage patterns. This data is used in aggregate and is not used to personally identify you.</p>
        </section>
        <section>
          <h3>Children's Privacy</h3>
          <p>This site is not directed at children under 13, and we do not knowingly collect personal information from children under 13.</p>
        </section>
        <section>
          <h3>Third-Party Links</h3>
          <p>Our site links to third-party content, including tournament results, retailers, and Discord. We are not responsible for the privacy practices of these external sites.</p>
        </section>
        <section>
          <h3>Fair use and not affiliated</h3>
          <p>Riftbound Decklists is a fan site. It is <strong>not affiliated with, endorsed by, or sponsored by Riot Games, UVS Games, Tencent, or League of Legends</strong>. Riftbound, League of Legends, Arcane, and all related names, marks, and distinctive likenesses are property of their owners. Original illustrations on this site are newly created, stylized card-frame portraits for identification — they are not scans of official cards and are not identical to Riot product art.</p>
          <p>Tournament lists are republished from public official coverage and public event postings for commentary, reporting, and fan reference. If you are a rights holder and want a list or image taken down, use Discord when the invite is posted, or open an issue on the site repository.</p>
        </section>
        <section>
          <h3>Changes to This Policy</h3>
          <p>We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated "Last updated" date.</p>
        </section>
        <section>
          <h3>Contact</h3>
          <p>Discord is a placeholder without a link for now. When an invite exists, it will land in the header.</p>
        </section>
      </div>'''


def search_page():
    return '''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Search</div>
        <h2>Search</h2>
        <form class="site-search" method="get" action="/search.html" role="search">
          <label class="site-search-label" for="q">Search legends, players, cards, guides</label>
          <div class="site-search-row">
            <input id="q" type="search" name="q" placeholder="Kennen, Ornn, Seal of Discord…" />
            <button type="submit">Search</button>
          </div>
        </form>
        <p class="muted" id="search-status">Loading index…</p>
        <div id="search-results" class="search-group"></div>
      </div>'''


def prices_page(prices):
    options = "\n".join(f'<option value="{e(p["id"])}">{e(p["name"])} · ${p["price"]:.2f}</option>' for p in prices)
    rows = []
    for p in prices:
        cls = "price-up" if p["change"] >= 0 else "price-down"
        rows.append(f'''          <tr>
            <td><a href="#" data-jump="{e(p['id'])}">{e(p['name'])}</a><div class="muted">{e(p['kind'])}</div></td>
            <td>${p['price']:.2f}</td>
            <td class="{cls}">{p['change']:+.1f}%</td>
            <td><canvas class="spark" width="120" height="36" data-history='{json.dumps(p["history"])}'></canvas></td>
            <td><a class="buy-tcg-inline" href="https://partner.tcgplayer.com/c/7670706/1780961/21018?u={e('https://www.tcgplayer.com/search/riftbound/product?q=' + p['name'].replace(' ', '+') + '&productLineName=riftbound')}" target="_blank" rel="noopener nofollow sponsored">Buy</a></td>
          </tr>''')
    return f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Prices</div>
        <h2>Card price tracker</h2>
        <p>Fan-side history for singles that showed up in August–September Standard lists. Figures are illustrative market snapshots for this site, not a live TCGplayer API feed. Buy buttons still go through the same TCGplayer affiliate partnership as OPDB.</p>
        <div class="price-hero">
          <div>
            <label class="site-search-label" for="price-card">Card</label>
            <select id="price-card">{options}</select>
            <p class="muted" id="price-meta" style="margin-top:10px"></p>
            <p><a class="shop-buy" id="price-buy" href="#">Buy on TCGplayer</a></p>
          </div>
          <div class="price-chart-wrap">
            <canvas id="price-main-chart"></canvas>
          </div>
        </div>
        <table class="price-table">
          <thead><tr><th>Card</th><th>Now</th><th>60d</th><th>History</th><th></th></tr></thead>
          <tbody>
{chr(10).join(rows)}
          </tbody>
        </table>
        <p class="amazon-disclosure-line">TCGplayer affiliate links. We may earn a commission if you buy after clicking. Prices on TCGplayer are live; the chart is this site's tracker.</p>
      </div>'''


def build_shop():
    by = defaultdict(list)
    for p in SHOP:
        by[p["cat"]].append(p)
    blocks = []
    for cat, label in CAT_LABEL.items():
        cards = "\n".join(shop_card(p) for p in by[cat])
        blocks.append(f'''        <div class="section-title" style="margin-top:28px">
          <h3>{e(label)}</h3>
          <a href="/shop/{cat}.html">All {e(label.lower())} →</a>
        </div>
        <div class="shop-grid">
{cards}
        </div>''')
        write(ROOT / f"shop/{cat}.html", layout(
            f"{label} | Shop",
            f"{label} with Amazon affiliate links.",
            f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / <a href="/shop/">Shop</a> / {e(label)}</div>
        <h2>{e(label)}</h2>
        <p>Same Amazon Associate listings as One Piece Deck Base. Open Amazon for live price and stock.</p>
        <div class="shop-grid">
{cards}
        </div>
        <p class="amazon-disclosure-line">As an Amazon Associate I earn from qualifying purchases.</p>
      </div>''',
            current="shop", canonical=f"{SITE}/shop/{cat}.html",
        ))
    also = "\n".join(
        f'          <a class="item" href="/shop/{cat}.html"><div><div>{e(label)}</div><div class="muted">Amazon shop · table gear</div></div><span class="link">Open →</span></a>'
        for cat, label in CAT_LABEL.items()
    )
    write(ROOT / "shop/index.html", layout(
        "Shop | Sleeves, dice, playmats, deck boxes",
        "The same affiliate shop as One Piece Deck Base: sleeves, dice, playmats, deck boxes, table extras.",
        f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Shop</div>
        <h2>Shop</h2>
        <p>Sleeves, dice, playmats, deck boxes, and a table extra. Open Amazon for live price and stock. These are the same affiliate links as OPDB.</p>
{chr(10).join(blocks)}
        <div class="section-title" style="margin-top:28px"><h3>Also in the shop</h3></div>
        <div class="list">{also}</div>
        <p class="amazon-disclosure-line">As an Amazon Associate I earn from qualifying purchases.</p>
      </div>''',
        current="shop", canonical=f"{SITE}/shop/",
    ))
    write(ROOT / "shop/buy-list.html", layout(
        "Buy a list on TCGplayer",
        "Mass-entry helper with TCGplayer affiliate tracking.",
        '''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / <a href="/shop/">Shop</a> / Buy list</div>
        <h2>Buy a list</h2>
        <p>Deck pages already open TCGplayer mass entry with the affiliate partner link. Copy a list, then use Buy list on TCGplayer.</p>
        <p><a class="shop-buy" href="https://partner.tcgplayer.com/c/7670706/1780961/21018?u=https%3A%2F%2Fwww.tcgplayer.com%2Fmassentry%3Fproductline%3DRiftbound" target="_blank" rel="sponsored noopener noreferrer">Open TCGplayer mass entry</a></p>
      </div>''',
        current="shop", canonical=f"{SITE}/shop/buy-list.html",
    ))


def guide_page(title, slug, body, crumbs="Guides"):
    return layout(
        f"{title} | Riftbound guides",
        f"{title} — Riftbound TCG guide on Riftbound Decklists.",
        f'''      <div class="card hero policy">
        <div class="crumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / {e(title)}</div>
        <h2>{e(title)}</h2>
        {body}
      </div>''',
        current="guides", canonical=f"{SITE}/guides/{slug}.html",
    )


def build_guides(legends_ordered, by_legend, search_index):
    topics = [
        ("Riftbound", "riftbound", "Riftbound is Riot's League of Legends trading card game, published with UVS Games in English. These pages track Standard constructed lists."),
        ("Riftbound TCG", "riftbound-tcg", "Same game, search-friendly name. Constructed decks are 40 cards, one Legend, three Battlefields, twelve Runes."),
        ("League of Legends TCG", "league-of-legends-tcg", "Riftbound is the League of Legends TCG. It is not Legends of Runeterra. Lists here are paper Standard."),
        ("Standard", "standard", "Standard is the only constructed legality in 2026 organized play. See the <a href=\"/format.html\">format page</a>."),
        ("Vendetta", "vendetta", "Vendetta (VEN) released 31 July 2026. It is the newest set in Standard until Radiance on 23 October 2026."),
        ("Radiance", "radiance", "Radiance (RAD) is set 5, dated 23 October 2026. It will be legal for Stuttgart and Las Vegas Regional Championships."),
        ("Origins", "origins", "Origins (OGN) is the launch set. It rotates with the 2026 sets on Standard's two-year clock."),
        ("Spiritforged", "spiritforged", "Spiritforged (SFD) is set 2. Still Standard legal."),
        ("Unleashed", "unleashed", "Unleashed (UNL) is set 3. Master Yi, Wuju Bladesman and Irelia came in as regional staples."),
        ("Legend", "legend", "The Legend is the identity card. It is not a Leader and it is not you-the-summoner. Organize decks by Legend."),
        ("Chosen Champion", "chosen-champion", "One champion unit starts available. It counts toward the three-copy limit."),
        ("Runes", "runes", "Twelve runes. Six domains: Fury, Calm, Mind, Body, Chaos, Order. Splits like 9–3 Chaos-Order show up in Kennen."),
        ("Battlefields", "battlefields", "Three unique battlefields. In competitive 1v1 you choose one each game."),
        ("Domains", "domains", "Fury (red), Calm (green), Mind (blue), Body (orange), Chaos (purple), Order (yellow). Your Legend sets which two you may play."),
        ("Summoner Skirmish", "summoner-skirmish", "Local championship event through Radiance. Riot is retiring it in 2027 for Challenge Series and Nexus Cup."),
        ("Regional Qualifier", "regional-qualifier", "Premier 2026 events. Barcelona, Wuhan, Singapore in this window. Become Riftbound Regionals in 2027."),
        ("Showdown Series", "showdown-series", "TO-run competitive bridge events. NRG $5k is one example in August 2026."),
        ("Nexus Nights", "nexus-nights", "Weekly local organized play."),
        ("Conquer", "conquer", "Scoring by taking a battlefield. Fury likes it. You still have to hold to close games."),
        ("Hold", "hold", "Defending a battlefield you already scored. Calm likes it."),
        ("Channel", "channel", "How you bring runes into play. Banner shorthand: Channel. Conquer. Score."),
        ("Sideboard", "sideboard", "Best-of-three only. Core rules: 0 or 8 cards. Some 2026 packets use 10. Copy the event document."),
        ("Starter decks", "starter-decks", "Champion precons exist. Official primer walks Lee Sin, Jinx, and Viktor as teaching examples."),
        ("Riftbound meta", "riftbound-meta", "August–September 2026: Kennen and Master Yi are the regional pair. Ornn won Barcelona. Akali won Singapore."),
        ("Kennen strategy", "kennen-strategy", "Chaos-Order storm. Seal of Discord, Lightning Rush, Rhasa, Stacked Deck. See <a href=\"/decklists/kennen-heart-of-the-tempest.html\">Kennen lists</a>."),
        ("Akali strategy", "akali-strategy", "Fury-Calm assassin that just won Singapore. See <a href=\"/decklists/akali-rogue-assassin.html\">Akali lists</a>."),
        ("Master Yi strategy", "master-yi-strategy", "Body-Calm combat. The Bladesman printing is the regional one. See <a href=\"/decklists/master-yi-wuju-bladesman.html\">Yi lists</a>."),
        ("Ornn strategy", "ornn-strategy", "Calm-Mind forge value. Barcelona champion. See <a href=\"/decklists/ornn-fire-below-the-mountain.html\">Ornn lists</a>."),
        ("Riot Games", "riot-games", "Designer and IP holder. This fan site is not affiliated with Riot."),
        ("UVS Games", "uvs-games", "English-language publishing and distribution partner."),
        ("Piltover Archive", "piltover-archive", "Official card gallery and deck tools at piltoverarchive.com."),
        ("PlayRiftbound", "playriftbound", "Official organized play home: playriftbound.com."),
        ("Constructed", "constructed", "Built-in-advance 40-card decks. Opposite of sealed. This site tracks constructed."),
        ("Locals", "locals", "City Challenges, Nexus Nights, shop events. We ingest public lists when they exist."),
        ("Fury", "fury", "Red domain. Aggression, accelerate, conquer rewards."),
        ("Calm", "calm", "Green domain. Holds, combat tricks, counters."),
        ("Mind", "mind", "Blue domain. Draw, gear, long-term plans."),
        ("Body", "body", "Orange domain. Ramp, efficient units, combat."),
        ("Chaos", "chaos", "Purple domain. Tricks, trash, hidden."),
        ("Order", "order", "Yellow domain. Go wide, death triggers, spot removal."),
    ]
    topic_links = []
    for title, slug, blurb in topics:
        body = f"<p>{blurb}</p><p>Jump to <a href=\"/decklists/\">legend lists</a>, the <a href=\"/format.html\">format page</a>, or <a href=\"/events.html\">events</a>.</p>"
        write(ROOT / f"guides/{slug}.html", guide_page(title, slug, body))
        topic_links.append(f'        <a class="item" href="/guides/{slug}.html"><div><div>{e(title)}</div><div class="muted">Topic</div></div><span class="link">Open →</span></a>')
        search_index.append({"title": title, "url": f"/guides/{slug}.html", "hay": f"{title} {blurb}"})

    char_links = []
    (ROOT / "guides/characters").mkdir(parents=True, exist_ok=True)
    for name in legends_ordered:
        meta = LEGEND_META[name]
        slug = slugify(meta["short"])
        lists = by_legend[name]
        body = f'''<p>{e(meta["blurb"])}</p>
        <p>Domains: {e(" / ".join(meta["domains"]))}. Set: {e(meta["set"])}.</p>
        <p><a href="/decklists/{e(legend_slug(name))}.html">{len(lists)} public lists →</a></p>'''
        write(ROOT / f"guides/characters/{slug}.html", layout(
            f"{meta['short']} | Riftbound guides",
            meta["blurb"],
            f'''      <div class="card hero policy">
        <div class="crumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / {e(meta["short"])}</div>
        <h2>{e(name)}</h2>
        {body}
      </div>''',
            current="guides", canonical=f"{SITE}/guides/characters/{slug}.html",
        ))
        char_links.append(f'        <a class="item" href="/guides/characters/{slug}.html"><div><div>{e(name)}</div><div class="muted">{e(" / ".join(meta["domains"]))}</div></div><span class="link">Open →</span></a>')
        search_index.append({"title": meta["short"], "url": f"/guides/characters/{slug}.html", "hay": f"{name} {meta['blurb']}"})

    write(ROOT / "guides/index.html", layout(
        "Riftbound TCG guides",
        "Topic and character pages that link to the Standard lists on this site.",
        f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Guides</div>
        <h2>Riftbound TCG guides</h2>
        <p>Topic and legend pages that link to the constructed lists on this site.</p>
        <div class="section-title"><h3>Topics</h3></div>
        <div class="list">{chr(10).join(topic_links)}</div>
        <div class="section-title" style="margin-top:28px"><h3>Legends</h3><div class="muted">{len(char_links)} names</div></div>
        <div class="list">{chr(10).join(char_links)}</div>
      </div>''',
        current="guides", canonical=f"{SITE}/guides/",
    ))
    search_index.append({"title": "Guides", "url": "/guides/", "hay": "guides topics legends riftbound"})


SEARCH_JS = r'''
(function () {
  function param(name) {
    var m = new URLSearchParams(location.search).get(name);
    return m ? m.trim() : "";
  }
  function boot() {
    var q = param("q");
    var input = document.getElementById("q");
    if (input && q) input.value = q;
    var status = document.getElementById("search-status");
    var box = document.getElementById("search-results");
    fetch("/data/search.json").then(function (r) { return r.json(); }).then(function (rows) {
      if (!q) {
        if (status) status.textContent = rows.length + " pages indexed. Type a legend, player, or card.";
        return;
      }
      var needle = q.toLowerCase();
      var hits = rows.filter(function (row) {
        return (row.title + " " + (row.hay || "")).toLowerCase().indexOf(needle) >= 0;
      }).slice(0, 60);
      if (status) status.textContent = hits.length + " result" + (hits.length === 1 ? "" : "s") + " for “" + q + "”";
      if (!box) return;
      box.innerHTML = hits.map(function (row) {
        return '<a class="item" href="' + row.url + '"><div><div>' + row.title + '</div><div class="muted">' + row.url + '</div></div><span class="link">Open →</span></a>';
      }).join("") || "<p class='muted'>Nothing matched.</p>";
    }).catch(function () {
      if (status) status.textContent = "Search index failed to load.";
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
'''


if __name__ == "__main__":
    build()
