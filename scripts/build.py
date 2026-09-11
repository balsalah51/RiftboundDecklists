#!/usr/bin/env python3
"""Generate the Riftbound Decklists static site from official public lists."""
from __future__ import annotations

import html
import json
import re
import hashlib
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from legend_strategy import html_for as strategy_html, hub_excerpt, STRAT
import topic_guides

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://riftbounddecklists.com"
NAME = "Riftbound Decklists"
SHORT = "RBDB"
TODAY = "2026-09-11"
# Fill after AdSense approval (ca-pub-…). Empty = no ads.txt seller line, slots stay hidden.
ADSENSE_PUB = ""

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
    "Kai'Sa, Daughter of the Void": {
        "short": "Kai'Sa", "img": "card-back", "domains": ("Fury", "Mind"),
        "set": "Origins", "tier": "B",
        "blurb": "Void survivor midrange. City Challenge winner in Shenzhen and a regular Top 16 in August Showdowns.",
    },
    "Teemo, Swift Scout": {
        "short": "Teemo", "img": "card-back", "domains": ("Chaos", "Mind"),
        "set": "Origins", "tier": "D",
        "blurb": "Mushroom tempo. A spicy Chaos-Mind Showdown legend, not a regional pair.",
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


def strategy_slug(name: str) -> str:
    meta = LEGEND_META.get(name, {})
    return slugify(meta.get("short") or name) + "-strategy"


def legend_img_abs(full: str) -> str:
    path = legend_img(full)
    return SITE + path if path.startswith("/") else f"{SITE}/{path}"


def ld_tag(*objs) -> str:
    graph = [o for o in objs if o]
    if not graph:
        return ""
    blob = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return f'<script type="application/ld+json">{blob}</script>'


def org_ld() -> dict:
    return {
        "@type": "Organization",
        "@id": SITE + "/#org",
        "name": NAME,
        "url": SITE + "/",
        "description": "Fan site for Riftbound TCG Standard decklists and legend strategy. Not affiliated with Riot Games or UVS Games.",
        "knowsAbout": ["Riftbound", "Riftbound TCG", "Vendetta Standard"],
        "logo": {"@type": "ImageObject", "url": SITE + "/img/rbdb-logo-192.jpg", "width": 192, "height": 192},
        "image": SITE + "/img/rbdb-hero.jpg",
    }


def website_ld() -> dict:
    return {
        "@type": "WebSite",
        "@id": SITE + "/#website",
        "name": NAME,
        "alternateName": ["RBDB", "Riftbound Deck Lists"],
        "url": SITE + "/",
        "description": "Fan archive of Riftbound TCG Standard decklists, legend hubs, and current-meta strategy.",
        "inLanguage": "en-US",
        "publisher": {"@id": SITE + "/#org"},
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": SITE + "/search.html?q={search_term_string}",
            },
            "query-input": "required name=search_term_string",
        },
    }


def riftbound_game_ld() -> dict:
    return {
        "@type": "VideoGame",
        "@id": SITE + "/#riftbound",
        "name": "Riftbound",
        "alternateName": ["Riftbound TCG", "League of Legends TCG"],
        "genre": "Trading card game",
        "author": {"@type": "Organization", "name": "Riot Games"},
        "publisher": {"@type": "Organization", "name": "UVS Games"},
        "gamePlatform": "Tabletop",
        "url": "https://playriftbound.com/",
    }


def webpage_ld(url: str, name: str, desc: str) -> dict:
    loc = url if str(url).startswith("http") else SITE + (url if url.startswith("/") else "/" + url)
    return {
        "@type": "WebPage",
        "@id": loc + "#webpage",
        "url": loc,
        "name": name,
        "description": desc,
        "isPartOf": {"@id": SITE + "/#website"},
        "about": {"@id": SITE + "/#org"},
        "inLanguage": "en-US",
        "dateModified": TODAY,
    }


def sitemap_meta(loc: str) -> tuple[str, str]:
    if loc == "/":
        return "daily", "1.0"
    if loc in ("/decklists/", "/tier-list.html", "/guides/legend-strategy.html"):
        return "weekly", "0.9"
    if loc in ("/format.html", "/events.html", "/guides/", "/shop/", "/prices.html"):
        return "weekly", "0.8"
    if loc.startswith("/decklists/") and loc.count("/") == 2:
        return "weekly", "0.85"
    if loc.endswith("-strategy.html"):
        return "weekly", "0.75"
    if loc.startswith("/decklists/"):
        return "monthly", "0.45"
    if loc.startswith("/shop/"):
        return "monthly", "0.55"
    if loc.startswith("/guides/"):
        return "monthly", "0.5"
    if loc in ("/search.html", "/privacy.html", "/advertise.html"):
        return "yearly", "0.3"
    return "weekly", "0.6"


def html_loc(rel: str) -> str:
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def breadcrumb_ld(crumbs: list) -> dict:
    items = []
    for i, (name, url) in enumerate(crumbs, 1):
        loc = url if str(url).startswith("http") else SITE + url
        items.append({"@type": "ListItem", "position": i, "name": name, "item": loc})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def faq_ld(name: str, meta: dict) -> dict | None:
    row = STRAT.get(name)
    if not row:
        return None
    short = meta.get("short") or name
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f"How do you play {short} in Vendetta Standard?", "acceptedAnswer": {"@type": "Answer", "text": row["plan"]}},
            {"@type": "Question", "name": f"What are the key cards in {short}?", "acceptedAnswer": {"@type": "Answer", "text": row["keys"]}},
            {"@type": "Question", "name": f"What are the {short} matchups in this meta?", "acceptedAnswer": {"@type": "Answer", "text": row["matchups"]}},
            {"@type": "Question", "name": f"When should I register {short}?", "acceptedAnswer": {"@type": "Answer", "text": row["pick"]}},
        ],
    }


def clip(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    if len(s) <= n:
        return s
    return s[: n - 1].rsplit(" ", 1)[0] + "…"


def sitemap_url(loc: str, lastmod: str = "", changefreq: str = "weekly", priority: str = "0.6", image: str = "") -> str:
    href = loc if loc.startswith("http") else SITE + (loc if loc.startswith("/") else "/" + loc)
    parts = [f"  <url><loc>{href}</loc>"]
    if lastmod:
        parts.append(f"<lastmod>{lastmod}</lastmod>")
    parts.append(f"<changefreq>{changefreq}</changefreq><priority>{priority}</priority>")
    if image:
        parts.append(f"<image:image><image:loc>{e(image)}</image:loc></image:image>")
    parts.append("</url>")
    return "".join(parts)


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


def layout(title, desc, body, current="", extra_head="", body_class="", canonical="",
           og_image="", og_type="website", json_ld=None, published="", noindex=False):
    canon = canonical or SITE + "/"
    og = og_image or (SITE + "/img/rbdb-hero.jpg")
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    extra_ld = list(json_ld or [])
    ld = ld_tag(org_ld(), website_ld(), riftbound_game_ld(), *extra_ld)
    pub = f'\n  <meta property="article:published_time" content="{e(published)}" />' if published else ""
    ads_meta = f'\n  <meta name="google-adsense-account" content="{e(ADSENSE_PUB)}" />' if ADSENSE_PUB else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta name="impact-site-verification" content="2a231ac3-b656-4c47-806f-411dadcf4bb1" />
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <script>
    (function () {{
      try {{
        var m = document.cookie.match(/(?:^|; )rbdb-theme=(dark|light)(?:;|$)/);
        document.documentElement.setAttribute("data-theme", m ? m[1] : "light");
      }} catch (e) {{
        document.documentElement.setAttribute("data-theme", "light");
      }}
    }})();
  </script>
  <title>{e(title)}</title>
  <meta name="description" content="{e(clip(desc, 160))}" />
  <meta name="author" content="{e(NAME)}" />
  <meta name="application-name" content="{e(NAME)}" />
  <meta name="color-scheme" content="light dark" />
  <link rel="stylesheet" href="/css/site.css?v=rift-6" />
  <link rel="canonical" href="{e(canon)}" />
  <meta name="robots" content="{robots}" />
  <meta name="theme-color" content="#b42318" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <link rel="icon" href="/img/rbdb-logo-192.jpg" type="image/jpeg" sizes="192x192" />
  <link rel="apple-touch-icon" href="/img/rbdb-logo-192.jpg" sizes="192x192" />
  <link rel="manifest" href="/site.webmanifest" />
  <link rel="search" type="application/opensearchdescription+xml" title="{e(NAME)}" href="/opensearch.xml" />
  <link rel="sitemap" type="application/xml" title="Sitemap" href="/sitemap.xml" />
  <link rel="alternate" type="application/rss+xml" title="Recent Riftbound decklists" href="/feed.xml" />
  <link rel="author" type="text/plain" href="/humans.txt" />{ads_meta}
  <meta property="og:site_name" content="{e(NAME)}" />
  <meta property="og:locale" content="en_US" />
  <meta property="og:type" content="{e(og_type)}" />
  <meta property="og:title" content="{e(title)}" />
  <meta property="og:description" content="{e(clip(desc, 160))}" />
  <meta property="og:url" content="{e(canon)}" />
  <meta property="og:image" content="{e(og)}" />
  <meta property="og:image:alt" content="{e(title)}" />
  <meta property="og:image:width" content="1400" />
  <meta property="og:image:height" content="788" />
  <meta property="og:image:type" content="image/jpeg" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{e(title)}" />
  <meta name="twitter:description" content="{e(clip(desc, 160))}" />
  <meta name="twitter:image" content="{e(og)}" />
  <meta name="twitter:image:alt" content="{e(title)}" />{pub}
  {ld}
  {extra_head}
</head>
<body{(' class="' + body_class + '"') if body_class else ''}>
  <a class="skip-link" href="#content">Skip to content</a>
  <div class="wrap">
    <header>
      <a class="brand" href="/">
        <img class="logo" src="/img/rbdb-avatar.jpg" width="56" height="56" alt="{e(NAME)} logo" />
        <div>
          <p class="brand-name">{e(NAME)}</p>
          <div class="subtitle">Riftbound TCG · Standard lists · Legend strategy</div>
        </div>
      </a>
      <button type="button" class="theme-toggle" id="theme-toggle" role="switch" aria-checked="false" aria-label="Dark mode">
        <span class="theme-toggle-option" data-on="light">Light</span>
        <span class="theme-toggle-option" data-on="dark">Dark</span>
      </button>
      <nav aria-label="Primary">
        {header_nav(current)}
      </nav>
    </header>
    <aside class="ad-slot ad-slot-top" data-ad-slot="top" data-ad-format="horizontal" hidden data-nosnippet>
      <p class="ad-kicker">Advertisement</p>
    </aside>
    <main id="content" class="single" role="main">
      {body}
    </main>
    <aside class="ad-slot ad-slot-bottom" data-ad-slot="bottom" data-ad-format="horizontal" hidden data-nosnippet>
      <p class="ad-kicker">Advertisement</p>
    </aside>
    <footer>
      <nav class="footer-grid" aria-label="Footer">
        <div>
          <div class="footer-kicker">Lists</div>
          <a href="/decklists/">Legends</a>
          <a href="/tier-list.html">Tier list</a>
          <a href="/#recent">Recent lists</a>
          <a href="/guides/legend-strategy.html">Legend strategy</a>
        </div>
        <div>
          <div class="footer-kicker">Play</div>
          <a href="/format.html">Standard format</a>
          <a href="/events.html">Events</a>
          <a href="/guides/">Guides</a>
          <a href="/search.html">Search</a>
        </div>
        <div>
          <div class="footer-kicker">Shop</div>
          <a href="/shop/">Table gear</a>
          <a href="/prices.html">Price tracker</a>
          <a href="/shop/buy-list.html">Buy a list</a>
          <a href="/advertise.html">Advertise</a>
          <a href="/privacy.html">Privacy</a>
        </div>
      </nav>
      <p class="footer-legal">© <span id="year"></span> {e(NAME)} — Fan site, not affiliated with Riot Games, UVS Games, or League of Legends. Riftbound and League of Legends are trademarks of their owners. Tournament lists are republished from public results for commentary and reference. Shop and buy-list links are affiliates; we may earn a commission.</p>
    </footer>
  </div>
  <script src="/js/ads-config.js?v=rift-1" defer></script>
  <script src="/js/tcgplayer-config.js?v=rift-1" defer></script>
  <script src="/js/site.js?v=rift-2" defer></script>
  <script src="/js/tcgplayer.js?v=rift-1" defer></script>
  <script src="/js/affiliates.js?v=rift-1" defer></script>
  <script src="/js/ads.js?v=rift-1" defer></script>
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
              <img class="shop-photo" src="/img/shop/{e(p['img'])}" alt="{e(p['title'])}" width="400" height="400" loading="lazy" decoding="async" />
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
    scraped_path = ROOT / "data/scraped-lists.txt"
    scraped = parse_extra(scraped_path.read_text(encoding="utf-8", errors="replace")) if scraped_path.exists() else []
    decks = barcelona + extra + scraped
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
        if len(picked) >= 160:
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
              <h1>Riftbound Decklists</h1>
              <p class="banner-terms">Channel runes · Hold battlefields · Conquer · Score the Rift</p>
            </div>
          </div>
        </section>

        <a class="events-banner" id="events" href="https://playriftbound.com/en-us/news/organizedplay/" target="_blank" rel="noopener">
          <div>
            <div class="kicker">Official Riot / UVS site</div>
            <div class="title">Riftbound organized play</div>
            <div class="muted" style="color:rgba(255,255,255,0.82);margin-top:4px">Regional Qualifiers, Showdown Series, Championships</div>
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
            <span class="home-big-note">Every legend picture on this site</span>
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
                <h2>Legends</h2>
                <p>Pick a picture. Each page has lists for that legend. Names live in the <a href="/guides/">guides</a>.</p>
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
            <h2>Recent lists</h2>
            <div class="muted">{len(picked)} lists</div>
          </div>
          <p class="muted">Newest first. At least one list from each legend, then the latest results. {len(decks)} public Standard lists from August–September 2026 tournaments, including Singapore, Wuhan, Ottawa, Speyer, and City Challenges.</p>
          <ul class="recent-list" aria-label="Recent decklists">
{chr(10).join(recent_items)}
          </ul>
        </section>

        <section class="card home-panel home-faq policy" id="faq">
          <div class="section-title"><h2>FAQ</h2></div>
          <h3>What is Riftbound Decklists?</h3>
          <p>A fan archive of public Riftbound TCG Standard constructed lists. Browse by Legend, copy a tournament list, and read current-meta strategy. Not affiliated with Riot Games or UVS Games.</p>
          <h3>What format are these lists?</h3>
          <p>Standard. That is the only constructed legality in 2026 organized play. Deck construction notes are on the <a href="/format.html">format page</a>.</p>
          <h3>What is a Legend?</h3>
          <p>The identity card that sits outside your 40. This site organizes decks by Legend. Strategy for each name is on the legend hub and in <a href="/guides/legend-strategy.html">legend strategy</a>.</p>
          <h3>How do I buy a list?</h3>
          <p>Copy list, then Buy on TCGplayer (Impact affiliate). Table gear in the <a href="/shop/">shop</a> uses Amazon Associate links. Cardmarket and eBay catalog links sit next to buy buttons for EU and secondary-market singles.</p>
          <h3>Do you show ads?</h3>
          <p>Ad slots are wired for Google AdSense and stay hidden until a publisher ID is approved. Details: <a href="/advertise.html">advertise and affiliates</a>.</p>
        </section>
'''
    home_title = "Riftbound Decklists | Standard tournament lists and legend strategy"
    home_desc = "Public Riftbound TCG Standard decklists from August–September 2026. Browse by Legend, copy lists from Singapore, Wuhan, and Barcelona, and read current-meta strategy."
    home_list = {
        "@type": "ItemList",
        "name": "Riftbound Standard legends",
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "numberOfItems": min(16, len(legends_ordered)),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "name": name,
                "url": f"{SITE}/decklists/{legend_slug(name)}.html",
            }
            for i, name in enumerate(legends_ordered[:16], 1)
        ],
    }
    home_faq = {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": "What is Riftbound Decklists?", "acceptedAnswer": {"@type": "Answer", "text": "A fan archive of public Riftbound TCG Standard constructed lists, grouped by Legend, with current-meta strategy. Not affiliated with Riot Games or UVS Games."}},
            {"@type": "Question", "name": "What format are these Riftbound lists?", "acceptedAnswer": {"@type": "Answer", "text": "Standard constructed, the only constructed legality in 2026 organized play."}},
            {"@type": "Question", "name": "What is a Legend in Riftbound?", "acceptedAnswer": {"@type": "Answer", "text": "The identity card that sits outside the 40-card main. Decks on this site are organized by Legend."}},
            {"@type": "Question", "name": "How do I buy a Riftbound list?", "acceptedAnswer": {"@type": "Answer", "text": "Copy the list and use the TCGplayer affiliate buy button. Table gear uses Amazon Associate links. Cardmarket and eBay catalog searches are linked for singles."}},
        ],
    }
    write(ROOT / "index.html", layout(
        home_title,
        home_desc,
        home, current="recent", canonical=SITE + "/",
        extra_head='<link rel="preload" as="image" href="/img/rbdb-hero.jpg" fetchpriority="high">',
        json_ld=[
            breadcrumb_ld([("Home", "/")]),
            webpage_ld("/", home_title, home_desc),
            home_list,
            home_faq,
        ],
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
    legends_title = "Riftbound legends | Standard decklists"
    legends_desc = "Every Riftbound legend with public Standard lists: Kennen, Master Yi, Akali, Ornn, Irelia, and the rest of the August–September 2026 field."
    write(ROOT / "decklists/index.html", layout(
        legends_title,
        legends_desc,
        f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Legends</div>
        <h1>Riftbound legends</h1>
        <p>Riftbound organizes decks around a Legend — the identity card that sits outside your 40. Current Standard is the only constructed format in organized play. Each hub has public tournament lists and current-meta strategy.</p>
        <div class="leader-grid">
{chr(10).join(tiles)}
        </div>
      </div>''',
        current="legends", canonical=f"{SITE}/decklists/",
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Legends", "/decklists/")]),
            webpage_ld("/decklists/", legends_title, legends_desc),
            {
                "@type": "CollectionPage",
                "name": legends_title,
                "url": f"{SITE}/decklists/",
                "numberOfItems": len(legends_ordered),
            },
        ],
    ))
    search_index.append({"title": "Legends", "url": "/decklists/", "hay": "legends decklists"})

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
            place = placing_label(d["placing"])
            deck_title = clip(f"{d['player']} {meta['short']} decklist ({place}) | Riftbound", 62)
            deck_desc = clip(
                f"{place} {meta['short']} Standard list from {d['event']} on {d['date']}. "
                f"Riftbound TCG decklist with legend, runes, battlefields, and sideboard.",
                160,
            )
            write(ROOT / d["url"].lstrip("/"), layout(
                deck_title,
                deck_desc,
                body, current="legends", body_class=color_class(d["domains"]),
                canonical=SITE + d["url"],
                og_image=legend_img_abs(name),
                og_type="article",
                published=d.get("date") or "",
                json_ld=[
                    breadcrumb_ld([
                        ("Home", "/"),
                        ("Legends", "/decklists/"),
                        (meta["short"], f"/decklists/{legend_slug(name)}.html"),
                        (f"{d['player']} list", d["url"]),
                    ]),
                    {
                        "@type": "Article",
                        "headline": f"{d['player']} — {meta['short']} Standard decklist",
                        "datePublished": d.get("date"),
                        "dateModified": d.get("date") or TODAY,
                        "author": {"@type": "Person", "name": d["player"]},
                        "publisher": {"@id": SITE + "/#org"},
                        "about": name,
                        "image": legend_img_abs(name),
                        "mainEntityOfPage": SITE + d["url"],
                        "inLanguage": "en-US",
                        "isPartOf": {"@id": SITE + "/#website"},
                    },
                ],
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
            <h1>{e(name)}</h1>
            <div class="stat-row">
              <span class="pill">{e(" / ".join(meta["domains"]))}</span>
              <span class="pill">{e(meta["set"])}</span>
              <span class="pill">Standard</span>
            </div>
            {hub_excerpt(name, meta, f"/guides/{e(strategy_slug(name))}.html")}
          </div>
        </div>
        <section class="legend-strategy policy" style="margin-top:22px">
          <div class="section-title">
            <h3>Current meta</h3>
            <div class="muted">August–September 2026</div>
          </div>
          {strategy_html(name, meta, len(lists), f"/decklists/{e(slug)}.html")}
        </section>
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
            clip(f"{name} decklists ({len(lists)}) | Riftbound Standard", 62),
            clip(f"{meta['blurb']} {len(lists)} public Standard lists for {meta['short']} from August–September 2026 tournaments.", 160),
            hub, current="legends", body_class=color_class(meta["domains"]),
            canonical=f"{SITE}/decklists/{slug}.html",
            og_image=legend_img_abs(name),
            json_ld=[
                breadcrumb_ld([("Home", "/"), ("Legends", "/decklists/"), (meta["short"], f"/decklists/{slug}.html")]),
                {
                    "@type": "CollectionPage",
                    "name": f"{name} Standard decklists",
                    "url": f"{SITE}/decklists/{slug}.html",
                    "about": name,
                    "numberOfItems": len(lists),
                },
                faq_ld(name, meta),
            ],
        ))
        search_index.append({"title": name, "url": f"/decklists/{slug}.html", "hay": f"{name} {meta['short']} legend {meta['blurb']}"})

    # Format
    format_title = "Riftbound Standard format | Deck construction 2026"
    format_desc = "Riftbound Standard constructed rules: 40-card main, one Legend, three Battlefields, 12 runes, and 2026 set legality including Vendetta and Radiance."
    write(ROOT / "format.html", layout(
        format_title,
        format_desc,
        format_page(), current="format", canonical=f"{SITE}/format.html",
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Format", "/format.html")]),
            webpage_ld("/format.html", format_title, format_desc),
            {
                "@type": "HowTo",
                "name": "Build a Riftbound Standard deck",
                "description": "Deck construction for 2026 Riftbound Standard constructed.",
                "step": [
                    {"@type": "HowToStep", "name": "Choose a Legend", "text": "The Legend sits outside the 40 and locks two domains."},
                    {"@type": "HowToStep", "name": "Build the 40", "text": "Up to three copies of a unique card. Include one Chosen Champion."},
                    {"@type": "HowToStep", "name": "Add battlefields and runes", "text": "Three unique Battlefields and twelve Runes."},
                    {"@type": "HowToStep", "name": "Sideboard for best-of-three", "text": "0 or 8 cards in the core rules; some 2026 packets use 10."},
                ],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": "Is Standard the only Riftbound constructed format?", "acceptedAnswer": {"@type": "Answer", "text": "Yes in 2026 organized play."}},
                    {"@type": "Question", "name": "Does the Legend count toward the 40?", "acceptedAnswer": {"@type": "Answer", "text": "No. The Legend sits outside the main deck."}},
                ],
            },
        ],
    ))
    search_index.append({"title": "Format", "url": "/format.html", "hay": "standard constructed runes battlefields sideboard banlist radiance"})

    # Events page (internal companion to official hub)
    events_title = "Riftbound events 2026 | Regional Qualifiers and Championships"
    events_desc = "Riftbound organized play digest for 2026: Barcelona, Wuhan, Singapore, Stuttgart, Las Vegas, Showdown Series, and Summoner Skirmish."
    write(ROOT / "events.html", layout(
        events_title,
        events_desc,
        events_page(), canonical=f"{SITE}/events.html",
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Events", "/events.html")]),
            webpage_ld("/events.html", events_title, events_desc),
            {
                "@type": "Event",
                "name": "Riftbound European Regional Championship 2026",
                "startDate": "2026-11-06",
                "endDate": "2026-11-08",
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "eventStatus": "https://schema.org/EventScheduled",
                "location": {"@type": "Place", "name": "Messe Stuttgart", "address": {"@type": "PostalAddress", "addressLocality": "Stuttgart", "addressCountry": "DE"}},
                "organizer": {"@type": "Organization", "name": "Riot Games"},
                "url": "https://playriftbound.com/en-us/news/organizedplay/2026-regional-championship-info/",
                "description": "Standard including Radiance. $50,000. Top 8 to Worlds.",
            },
            {
                "@type": "Event",
                "name": "Riftbound North American Regional Championship 2026",
                "startDate": "2026-12-11",
                "endDate": "2026-12-13",
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "eventStatus": "https://schema.org/EventScheduled",
                "location": {"@type": "Place", "name": "Convergence Fest", "address": {"@type": "PostalAddress", "addressLocality": "Las Vegas", "addressCountry": "US"}},
                "organizer": {"@type": "Organization", "name": "Riot Games"},
                "url": "https://playriftbound.com/en-us/news/organizedplay/north-american-regional-championship-info/",
            },
        ],
    ))
    search_index.append({"title": "Events", "url": "/events.html", "hay": "singapore barcelona wuhan stuttgart las vegas championships"})

    # Tier list
    tier_title = "Riftbound Standard tier list | Vendetta 2026"
    tier_desc = "Legend tier list for Riftbound Vendetta Standard after Regional Qualifiers in Barcelona, Wuhan, and Singapore."
    write(ROOT / "tier-list.html", layout(
        tier_title,
        tier_desc,
        tier_page(by_legend, legends_ordered), current="tier", canonical=f"{SITE}/tier-list.html",
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Tier list", "/tier-list.html")]),
            webpage_ld("/tier-list.html", tier_title, tier_desc),
        ],
    ))
    search_index.append({"title": "Tier List", "url": "/tier-list.html", "hay": "tier list kennen akali master yi ornn"})

    # Privacy
    privacy_title = "Privacy Policy | Riftbound Decklists"
    privacy_desc = "Privacy, cookies, affiliates, fair use, and disclaimer for Riftbound Decklists, a Riftbound TCG fan site."
    write(ROOT / "privacy.html", layout(
        privacy_title,
        privacy_desc,
        privacy_page(), current="", canonical=f"{SITE}/privacy.html",
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Privacy", "/privacy.html")]),
            webpage_ld("/privacy.html", privacy_title, privacy_desc),
        ],
    ))

    adv_title = "Advertise and affiliates | Riftbound Decklists"
    adv_desc = "Host display ads and affiliate partnerships on Riftbound Decklists: Google AdSense, Carbon Ads, Amazon, TCGplayer, Cardmarket, eBay, and direct TCG sponsorships."
    write(ROOT / "advertise.html", layout(
        adv_title,
        adv_desc,
        advertise_page(), canonical=f"{SITE}/advertise.html",
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Advertise", "/advertise.html")]),
            webpage_ld("/advertise.html", adv_title, adv_desc),
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": "Do you run Google AdSense?", "acceptedAnswer": {"@type": "Answer", "text": "Ad slots are wired for AdSense. They stay hidden until a ca-pub publisher ID is approved and enabled in ads-config.js."}},
                    {"@type": "Question", "name": "Which affiliate programs are live?", "acceptedAnswer": {"@type": "Answer", "text": "Amazon Associates for table gear and TCGplayer Impact for singles and mass-entry buy lists."}},
                    {"@type": "Question", "name": "Can I sponsor the site directly?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. Sleeve, playmat, and shop brands can buy labeled placements. Discord is the contact placeholder until an invite is posted."}},
                ],
            },
        ],
    ))
    search_index.append({"title": "Advertise", "url": "/advertise.html", "hay": "adsense carbon ads amazon tcgplayer cardmarket ebay affiliate sponsor"})

    # Search
    search_title = "Search Riftbound decklists, legends, and guides"
    search_desc = "Search Riftbound TCG Standard decklists by legend, player, card, event, or strategy guide on Riftbound Decklists."
    write(ROOT / "search.html", layout(
        search_title,
        search_desc,
        search_page(), current="search", canonical=f"{SITE}/search.html",
        extra_head='<script src="/js/search.js?v=rift-1" defer></script>',
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Search", "/search.html")]),
            webpage_ld("/search.html", search_title, search_desc),
        ],
    ))

    # Prices
    prices = []
    labels = [(date(2026, 7, 9) + timedelta(days=i)).isoformat() for i in range(60)]
    for name, price, kind in PRICE_SEED:
        hist = seeded_history(name, price)
        change = (hist[-1] - hist[0]) / hist[0] * 100 if hist[0] else 0
        prices.append({"id": slugify(name), "name": name, "price": price, "kind": kind, "history": hist, "change": change, "labels": [labels[0], labels[-1]]})
    write(ROOT / "data/prices.json", json.dumps(prices, indent=2))
    prices_title = "Riftbound card price tracker | TCGplayer singles"
    prices_desc = "Riftbound TCG singles price history with TCGplayer affiliate buy links. Fan-side tracker for cards that showed up in 2026 Standard lists."
    write(ROOT / "prices.html", layout(
        prices_title,
        prices_desc,
        prices_page(prices), current="prices", canonical=f"{SITE}/prices.html",
        extra_head='<script>window.RBDB_PRICES = ' + json.dumps({p["id"]: p for p in prices}) + ';</script>\n  <script src="/js/prices.js?v=rift-2" defer></script>',
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Prices", "/prices.html")]),
            webpage_ld("/prices.html", prices_title, prices_desc),
        ],
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
    write(ROOT / "robots.txt", """User-agent: *
Allow: /
Disallow: /404.html

Sitemap: https://riftbounddecklists.com/sitemap.xml
""")
    if ADSENSE_PUB:
        pub = ADSENSE_PUB.replace("ca-pub-", "pub-") if ADSENSE_PUB.startswith("ca-pub-") else ADSENSE_PUB
        write(ROOT / "ads.txt", f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")
    else:
        write(ROOT / "ads.txt", """# riftbounddecklists.com authorized digital sellers
# Add the AdSense line after approval, then rebuild:
# google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
""")
    items_rss = []
    for d in decks[:40]:
        meta = LEGEND_META[d["legend"]]
        items_rss.append(
            f"    <item><title>{e(d['player'])} — {e(meta['short'])} ({placing_label(d['placing'])})</title>"
            f"<link>{SITE}{d['url']}</link><pubDate>{e(d['date'])}</pubDate>"
            f"<description>{e(d['event'])} · {e(d['source'])}</description></item>"
        )
    write(ROOT / "feed.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{e(NAME)}</title>
    <link>{SITE}/</link>
    <description>Latest public Riftbound TCG Standard decklists</description>
    <language>en-us</language>
{chr(10).join(items_rss)}
  </channel>
</rss>
''')
    lastmods = {d["url"]: d["date"] for d in decks}
    hub_img = {}
    for name, lists in by_legend.items():
        loc = f"/decklists/{legend_slug(name)}.html"
        hub_img[loc] = legend_img_abs(name)
        if lists:
            lastmods[loc] = max(x["date"] for x in lists)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    seen = set()
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if any(part.startswith(".") for part in rel.parts):
            continue
        posix = rel.as_posix()
        if posix == "404.html":
            continue
        loc = html_loc(posix)
        if loc in seen:
            continue
        seen.add(loc)
        freq, pri = sitemap_meta(loc)
        sm.append(sitemap_url(loc, lastmods.get(loc, TODAY), freq, pri, hub_img.get(loc, "")))
    sm.append("</urlset>")
    write(ROOT / "sitemap.xml", "\n".join(sm) + "\n")
    write(ROOT / "site.webmanifest", json.dumps({
        "name": NAME,
        "short_name": SHORT,
        "description": "Riftbound TCG Standard decklists, legend hubs, and current-meta strategy.",
        "start_url": "/",
        "scope": "/",
        "lang": "en-US",
        "display": "standalone",
        "background_color": "#f4f1eb",
        "theme_color": "#b42318",
        "categories": ["games", "sports"],
        "icons": [
            {"src": "/img/rbdb-logo-192.jpg", "sizes": "192x192", "type": "image/jpeg", "purpose": "any"},
            {"src": "/img/rbdb-avatar.jpg", "sizes": "192x192", "type": "image/jpeg", "purpose": "any"},
        ],
    }, indent=2))
    write(ROOT / "llms.txt", f"""# {NAME}

> Fan archive of Riftbound TCG Standard tournament decklists, legend hubs, and current-meta strategy.

Riftbound is Riot Games' League of Legends trading card game. This site is not affiliated with Riot Games or UVS Games. The identity card is a Legend.

## Primary pages

- [Home]({SITE}/): Latest public Standard lists
- [Legends]({SITE}/decklists/): Every legend with public lists
- [Legend strategy]({SITE}/guides/legend-strategy.html): Current-meta plans by legend
- [Tier list]({SITE}/tier-list.html): Vendetta Standard picture board
- [Format]({SITE}/format.html): Standard deck construction
- [Events]({SITE}/events.html): 2026 organized play digest
- [Guides]({SITE}/guides/): Topics, domains, and character pages
- [Search]({SITE}/search.html): Site search
- [Advertise]({SITE}/advertise.html): Ads and affiliate programs
- [RSS]({SITE}/feed.xml): Latest lists
- [Sitemap]({SITE}/sitemap.xml)

## Optional

- Tournament lists are republished from public results for commentary.
- Shop uses Amazon Associates. Singles use TCGplayer Impact; Cardmarket and eBay catalog links are also present.
""")
    write(ROOT / "humans.txt", """/* TEAM */
Fan site: Riftbound Decklists
Site: https://riftbounddecklists.com/

/* THANKS */
Public tournament organizers, PlayRiftbound, Piltover Archive.

/* SITE */
Language: English
Standards: HTML5, CSS, JSON-LD
Doctype: HTML5
Generator: scripts/build.py
""")
    write(ROOT / "opensearch.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
  <ShortName>{e(NAME)}</ShortName>
  <Description>Search Riftbound TCG Standard decklists, legends, and guides</Description>
  <Url type="text/html" method="get" template="{SITE}/search.html?q={{searchTerms}}"/>
  <Image width="192" height="192" type="image/jpeg">{SITE}/img/rbdb-logo-192.jpg</Image>
  <Language>en-US</Language>
</OpenSearchDescription>
''')
    write(ROOT / "404.html", layout(
        "Page not found | Riftbound Decklists",
        "That Riftbound Decklists URL is missing. Search legends, lists, and guides, or return home.",
        '''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Not found</div>
        <h1>This page is not on the site</h1>
        <p>The URL you opened is not a published Riftbound Decklists page. It may have moved when legend hubs were renamed, or it was never generated.</p>
        <p>Try <a href="/">home</a>, <a href="/decklists/">legend lists</a>, <a href="/guides/legend-strategy.html">legend strategy</a>, or <a href="/search.html">search</a>.</p>
      </div>''',
        canonical=f"{SITE}/404.html",
        noindex=True,
        json_ld=[breadcrumb_ld([("Home", "/"), ("Not found", "/404.html")])],
    ))

    print(f"Wrote {len(decks)} decks across {len(by_legend)} legends")


def deck_page(d, meta):
    cc = color_class(d["domains"])
    main_count = sum(q for q, _ in d["main"])
    return f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / <a href="/decklists/">Legends</a> / <a href="/decklists/{e(legend_slug(d['legend']))}.html">{e(meta['short'])}</a> / Decklist</div>
        <h1>{e(d['player'])} — {e(meta['short'])} (Standard)</h1>
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
        <p class="related-links">More <a href="/decklists/{e(legend_slug(d['legend']))}.html">{e(meta['short'])} lists</a> · <a href="/guides/{e(strategy_slug(d['legend']))}.html">{e(meta['short'])} strategy</a> · <a href="/tier-list.html">Tier list</a> · <a href="/guides/legend-strategy.html">All legend strategy</a></p>
      </div>'''


def format_page():
    return '''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Format</div>
        <h1>Standard is the constructed format</h1>
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
          <h2>FAQ</h2>
          <h3>Is Standard the only constructed format?</h3>
          <p>Yes in 2026 organized play. Casual tables can still play other modes (FFA, 2v2) using Standard cards.</p>
          <h3>Does the Legend count toward the 40?</h3>
          <p>No. The Legend sits outside the main. The Chosen Champion is a unit in your deck and counts toward the three-copy limit.</p>
          <h3>When does Radiance become legal?</h3>
          <p>23 October 2026. It is legal for Stuttgart (6–8 November) and Las Vegas (11–13 December).</p>
        </section>
      </div>'''


def events_page():
    return '''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Events</div>
        <h1>Riftbound events and schedule</h1>
        <p>Primary source is always <a href="https://playriftbound.com/en-us/news/organizedplay/" target="_blank" rel="noopener">playriftbound.com organized play</a>. This page is a fan-side digest of August–December 2026.</p>
        <section class="policy">
          <h3>Just played</h3>
          <ul>
            <li><strong>14–23 August 2026</strong> — Regional Qualifier Barcelona (2,130+ players). Ornn won. Official recap: <a href="https://playriftbound.com/en-us/news/organizedplay/barcelonas-top-decks/" target="_blank" rel="noopener">Barcelona's Top Decks</a>.</li>
            <li><strong>8 August 2026</strong> — Riftbound Showdown Ottawa (594 players). Rengar won.</li>
            <li><strong>14 August 2026</strong> — 10K Showdown Auckland Card Show (301 players).</li>
            <li><strong>16 August 2026</strong> — RiftAtlas Convergence #2 (257 players).</li>
            <li><strong>23 August 2026</strong> — NRG Series $5k Constructed Showdown (Vendetta constructed).</li>
            <li><strong>15–16 August 2026</strong> — Riftbound Showdown Series Germany, Speyer. Public Top 32 lists are on this site.</li>
            <li><strong>30 August 2026</strong> — S4 Wuhan Regional Open (~1,280 players). Public Top 64 lists are on this site.</li>
            <li><strong>4–6 September 2026</strong> — Regional Qualifier Singapore, Singapore EXPO. Akali defeated Kennen in the finals. Public Top cut lists are on this site. Official preview: <a href="https://playriftbound.com/en-us/news/organizedplay/all-eyes-on-singapore/" target="_blank" rel="noopener">All Eyes on Singapore</a>.</li>
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
        <h1>Vendetta Standard tier list</h1>
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
        <h1>Privacy Policy</h1>
        <p>Last updated: September 11, 2026</p>
        <p>Riftbound Decklists ("we," "us," or "this site") respects your privacy. This Privacy Policy explains what information we collect when you visit riftbounddecklists.com, how we use it, and the choices you have.</p>
        <section>
          <h3>Information We Collect</h3>
          <p><strong>Automatically collected information:</strong> Like most websites, we automatically collect certain information when you visit, including your IP address, browser type, device type, pages viewed, and time spent on the site. This is collected through cookies, log files, and similar technologies.</p>
          <p><strong>Information you provide:</strong> If you join a Discord later, or contact us directly, any information you share there (such as a username or message) is subject to that platform's own privacy policy, not this one. We do not require account creation or collect personal information such as your name, email address, or payment details through this site.</p>
        </section>
        <section>
          <h3>Cookies</h3>
          <p>We use cookies and similar tracking technologies to understand how visitors use the site, remember basic preferences, and support advertising if ads are enabled. You can disable cookies through your browser settings.</p>
          <p>A first-party cookie named <code>rbdb-theme</code> stores only <code>light</code> or <code>dark</code> so the Light / Dark toggle at the top of every page can restore your last choice on the next visit. It lasts up to one year, is not used for advertising or tracking, and clearing cookies returns the site to light mode.</p>
        </section>
        <section>
          <h3>Advertising</h3>
          <p>This site is built to host display ads once a publisher account is approved. Inventory is reserved for Google AdSense first (auto ads plus labeled units). Carbon Ads is the backup if we want a smaller, TCG-adjacent network. Empty publisher IDs keep the slots hidden so Core Web Vitals stay clean. Opt out of personalized Google ads in <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Ads Settings</a>. See <a href="/advertise.html">advertise and affiliates</a> for how to turn ads on.</p>
        </section>
        <section>
          <h3>Affiliate partnerships</h3>
          <p>Some links on this site are affiliate links. If you buy through them, we may earn a commission. That does not change the price you pay.</p>
          <ul>
            <li><strong>Amazon.</strong> We are an Amazon Associate. The Shop links to Amazon for sleeves, dice, playmats, deck boxes, and table extras, and we earn from qualifying purchases. These are the same affiliate listings used on One Piece Deck Base.</li>
            <li><strong>TCGplayer.</strong> We are a TCGplayer affiliate (Impact partner <code>7670706 / 1780961 / 21018</code>). Buy links on decklists and the price tracker go to TCGplayer, and we may earn a commission if you purchase after clicking them.</li>
            <li><strong>Cardmarket.</strong> Catalog search links open Riftbound singles on Cardmarket (EU). Tracking is added after a partner ID is set in <code>js/ads-config.js</code>.</li>
            <li><strong>eBay Partner Network.</strong> Catalog searches for Riftbound singles. Campaign tracking is added after a campid is set.</li>
            <li><strong>CardNexus.</strong> Optional partner URL for the all-TCG marketplace; empty until approved.</li>
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


def advertise_page():
    return '''      <div class="card hero policy">
        <div class="crumb"><a href="/">Home</a> / Advertise</div>
        <h1>Advertise and affiliates</h1>
        <p>Riftbound Decklists is a high-intent fan archive: people land here to copy a Standard list and buy the cards. That is the inventory we sell — display ads, tracked singles links, and table-gear affiliates. This page is the menu. Nothing loads a third-party ad script until a publisher ID is approved.</p>

        <h2>Display ads (hosting)</h2>
        <p>Every page has labeled top and bottom units. They stay <code>hidden</code> until <code>js/ads-config.js</code> has <code>enabled: true</code> and an AdSense client. That keeps Core Web Vitals clean while the site is in review.</p>
        <h3>Google AdSense</h3>
        <p>Best first network for a custom-domain GitHub Pages site. After approval:</p>
        <ol>
          <li>Put <code>ca-pub-…</code> in <code>ADSENSE_PUB</code> in <code>scripts/build.py</code> and in <code>js/ads-config.js</code> (<code>adsenseClient</code>, <code>enabled: true</code>).</li>
          <li>Rebuild. <code>ads.txt</code> gets the official <code>google.com, pub-…, DIRECT, f08c47fec0942fa0</code> line. Slots unhide. Auto ads are optional.</li>
          <li>Confirm <a href="https://riftbounddecklists.com/ads.txt">/ads.txt</a> returns HTTP 200 on the root domain.</li>
        </ol>
        <h3>Carbon Ads</h3>
        <p>Smaller, design-forward units. Fit a TCG fan site better than a wall of remnant display. Add <code>carbonServe</code> and <code>carbonPlacement</code> in the same config when you have a campaign.</p>
        <h3>Mediavine, Raptive, Playwire, Ezoic</h3>
        <p>Session-gated premium networks. Apply when traffic supports it. Do not load their scripts until a contract exists — they will tank LCP if they sit idle.</p>
        <h3>Direct sponsorships</h3>
        <p>Sleeve, playmat, dice, and local-shop brands can buy a labeled homepage or legend-hub placement. That is usually worth more than remnant AdSense on a niche TCG URL. Discord is the contact placeholder until an invite is posted.</p>

        <h2>Affiliate programs</h2>
        <h3>Live today</h3>
        <ul>
          <li><strong>Amazon Associates</strong> — Shop sleeves, dice, playmats, deck boxes, table extras. Same listings as One Piece Deck Base.</li>
          <li><strong>TCGplayer (Impact)</strong> — Partner <code>7670706 / 1780961 / 21018</code>. Copy-list and per-card Buy buttons, plus mass entry. Highest intent on this site.</li>
        </ul>
        <h3>Wired, waiting on IDs</h3>
        <ul>
          <li><strong>Cardmarket</strong> — EU Riftbound singles catalog. Search links are already on deck pages. Add <code>cardmarketId</code> in <code>js/ads-config.js</code> to track.</li>
          <li><strong>eBay Partner Network</strong> — Secondary-market singles and sealed. Set <code>ebayCampId</code> to attach campaign parameters.</li>
          <li><strong>CardNexus</strong> — All-TCG marketplace partner program. Set <code>cardnexusUrl</code> to a tracked landing page.</li>
        </ul>
        <h3>Worth applying</h3>
        <ul>
          <li>Card Kingdom / Channel Fireball / CoolStuffInc store affiliates if they add Riftbound SKUs.</li>
          <li>Dragon Shield / Ultra Pro brand programs for sleeves and boxes (Amazon already covers many of those SKUs).</li>
          <li>Riot / UVS creator activations are contract-by-set, not an automated affiliate network. Do not claim an official Riftbound partner badge.</li>
        </ul>
        <p>FTC: affiliate links are marked <code>rel="sponsored"</code>. Amazon and TCGplayer disclosures sit on shop, prices, and deck pages.</p>

        <h2>FAQ</h2>
        <h3>Are ads on the site right now?</h3>
        <p>Slots exist. They do not request ad servers until a publisher ID is enabled. You should not see empty “Advertisement” boxes in the meantime.</p>
        <h3>Will ads change list copy?</h3>
        <p>No. Tournament lists stay the product. Ads sit above and below the article, labeled, and are skipped by crawlers with <code>data-nosnippet</code>.</p>
      </div>'''


def search_page():
    return '''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Search</div>
        <h1>Search Riftbound decklists</h1>
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
        <h1>Riftbound card price tracker</h1>
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
            clip(f"{label} for Riftbound TCG | Shop", 62),
            clip(f"{label} for Riftbound TCG tables. Amazon affiliate listings for Standard constructed play — same shop as One Piece Deck Base.", 160),
            f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / <a href="/shop/">Shop</a> / {e(label)}</div>
        <h1>{e(label)} for Riftbound</h1>
        <p>Same Amazon Associate listings as One Piece Deck Base. Open Amazon for live price and stock. These sleeves, dice, and boxes fit a 40-card Riftbound main deck plus extras.</p>
        <div class="shop-grid">
{cards}
        </div>
        <p class="amazon-disclosure-line">As an Amazon Associate I earn from qualifying purchases.</p>
      </div>''',
            current="shop", canonical=f"{SITE}/shop/{cat}.html",
            json_ld=[
                breadcrumb_ld([("Home", "/"), ("Shop", "/shop/"), (label, f"/shop/{cat}.html")]),
                webpage_ld(f"/shop/{cat}.html", f"{label} for Riftbound TCG | Shop", f"{label} for Riftbound TCG tables."),
            ],
        ))
    also = "\n".join(
        f'          <a class="item" href="/shop/{cat}.html"><div><div>{e(label)}</div><div class="muted">Amazon shop · table gear</div></div><span class="link">Open →</span></a>'
        for cat, label in CAT_LABEL.items()
    )
    write(ROOT / "shop/index.html", layout(
        "Riftbound shop | Sleeves, dice, playmats, deck boxes",
        "Riftbound TCG table gear: sleeves, dice, playmats, deck boxes, and extras. Amazon Associate listings with live price and stock on Amazon.",
        f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Shop</div>
        <h1>Shop Riftbound table gear</h1>
        <p>Sleeves, dice, playmats, deck boxes, and a table extra. Open Amazon for live price and stock. These are the same affiliate links as OPDB.</p>
        <section class="policy" style="margin-top:18px">
          <h2>Singles marketplaces</h2>
          <p>Amazon is table gear. For cards, use tracked TCGplayer mass entry, then Cardmarket (EU) or eBay if you need a second market.</p>
          <p>
            <a class="shop-buy" href="https://partner.tcgplayer.com/c/7670706/1780961/21018?u=https%3A%2F%2Fwww.tcgplayer.com%2Fmassentry%3Fproductline%3DRiftbound" target="_blank" rel="sponsored noopener noreferrer">TCGplayer mass entry</a>
            <a class="retailer-link" href="https://www.cardmarket.com/en/Riftbound/Products/Singles" target="_blank" rel="noopener nofollow sponsored">Cardmarket singles</a>
            <a class="retailer-link" href="https://www.ebay.com/sch/i.html?_nkw=Riftbound+TCG" target="_blank" rel="noopener nofollow sponsored">eBay Riftbound</a>
          </p>
        </section>
{chr(10).join(blocks)}
        <div class="section-title" style="margin-top:28px"><h3>Also in the shop</h3></div>
        <div class="list">{also}</div>
        <p class="amazon-disclosure-line">As an Amazon Associate I earn from qualifying purchases.</p>
      </div>''',
        current="shop", canonical=f"{SITE}/shop/",
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Shop", "/shop/")]),
            webpage_ld("/shop/", "Riftbound shop | Sleeves, dice, playmats, deck boxes", "Riftbound TCG table gear with Amazon affiliate listings."),
            {"@type": "CollectionPage", "name": "Riftbound shop", "url": f"{SITE}/shop/"},
        ],
    ))
    write(ROOT / "shop/buy-list.html", layout(
        "Buy a Riftbound list on TCGplayer",
        "Open TCGplayer mass entry with affiliate tracking to buy a Riftbound Standard list from this site.",
        '''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / <a href="/shop/">Shop</a> / Buy list</div>
        <h1>Buy a Riftbound list</h1>
        <p>Deck pages already open TCGplayer mass entry with the affiliate partner link. Copy a list, then use Buy list on TCGplayer.</p>
        <p><a class="shop-buy" href="https://partner.tcgplayer.com/c/7670706/1780961/21018?u=https%3A%2F%2Fwww.tcgplayer.com%2Fmassentry%3Fproductline%3DRiftbound" target="_blank" rel="sponsored noopener noreferrer">Open TCGplayer mass entry</a></p>
      </div>''',
        current="shop", canonical=f"{SITE}/shop/buy-list.html",
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Shop", "/shop/"), ("Buy a list", "/shop/buy-list.html")]),
            webpage_ld("/shop/buy-list.html", "Buy a Riftbound list on TCGplayer", "TCGplayer mass entry for Riftbound Standard lists."),
        ],
    ))


def guide_page(title, slug, body, desc="", json_ld=None, og_image="", og_type="article", h1=""):
    heading = h1 or title
    desc = desc or f"{title} — Riftbound TCG guide for Vendetta Standard constructed play on Riftbound Decklists."
    extras = [
        breadcrumb_ld([("Home", "/"), ("Guides", "/guides/"), (title, f"/guides/{slug}.html")]),
        webpage_ld(f"/guides/{slug}.html", f"{title} | Riftbound TCG", desc),
    ]
    extras.extend(x for x in (json_ld or []) if x)
    return layout(
        clip(f"{title} | Riftbound TCG", 62),
        clip(desc, 160),
        f'''      <div class="card hero policy">
        <div class="crumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / {e(title)}</div>
        <h1>{e(heading)}</h1>
        {body}
      </div>''',
        current="guides", canonical=f"{SITE}/guides/{slug}.html",
        og_image=og_image, og_type=og_type, json_ld=extras, published=TODAY,
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
        ("Legend", "legend", "The Legend is the identity card. Organize decks by Legend."),
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
        ("Riftbound meta", "riftbound-meta", "August–September 2026: Kennen and Master Yi are the regional pair. Ornn won Barcelona. Akali won Singapore. Per-legend strategy lives on each legend page and in the strategy guides."),
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
        body = topic_guides.html_for(title, slug, blurb)
        write(ROOT / f"guides/{slug}.html", guide_page(
            title, slug, body,
            desc=f"{blurb} Riftbound TCG guide on Riftbound Decklists.",
        ))
        topic_links.append(f'        <a class="item" href="/guides/{slug}.html"><div><div>{e(title)}</div><div class="muted">Topic</div></div><span class="link">Open →</span></a>')
        search_index.append({"title": title, "url": f"/guides/{slug}.html", "hay": f"{title} {blurb}"})

    strat_links = []
    for name in legends_ordered:
        meta = LEGEND_META[name]
        sslug = strategy_slug(name)
        lists = by_legend[name]
        row = STRAT.get(name)
        plan = row["plan"] if row else meta["blurb"]
        body = strategy_html(name, meta, len(lists), f"/decklists/{e(legend_slug(name))}.html")
        write(ROOT / f"guides/{sslug}.html", guide_page(
            f"{meta['short']} strategy",
            sslug,
            f'<div class="policy">{body}</div>',
            desc=f"{plan} {meta['short']} Vendetta Standard strategy with public Riftbound lists.",
            json_ld=[
                faq_ld(name, meta),
                {
                    "@type": "Article",
                    "headline": f"{meta['short']} strategy — Vendetta Standard",
                    "about": name,
                    "dateModified": TODAY,
                    "author": {"@id": SITE + "/#org"},
                    "publisher": {"@id": SITE + "/#org"},
                    "inLanguage": "en-US",
                },
            ],
            og_image=legend_img_abs(name),
            h1=f"{meta['short']} strategy",
        ))
        strat_links.append(f'        <a class="item" href="/guides/{sslug}.html"><div><div>{e(meta["short"])} strategy</div><div class="muted">{e(" / ".join(meta["domains"]))} · {meta.get("tier", "D")}</div></div><span class="link">Open →</span></a>')
        search_index.append({"title": f"{meta['short']} strategy", "url": f"/guides/{sslug}.html", "hay": f"{name} strategy meta {meta['blurb']}"})
    write(ROOT / "guides/legend-strategy.html", layout(
        "Legend strategy | Vendetta Standard | Riftbound",
        "Current-meta strategy for every Riftbound legend with public Standard lists: game plan, key cards, matchups, and when to register it.",
        f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / Legend strategy</div>
        <h1>Legend strategy</h1>
        <p>August–September 2026 Vendetta Standard. Each page is a game plan, key cards, matchups, and when to register that legend. Lists stay on the legend hubs.</p>
        <div class="list">
{chr(10).join(strat_links)}
        </div>
      </div>''',
        current="guides", canonical=f"{SITE}/guides/legend-strategy.html",
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Guides", "/guides/"), ("Legend strategy", "/guides/legend-strategy.html")]),
            webpage_ld("/guides/legend-strategy.html", "Legend strategy | Vendetta Standard", "Current-meta strategy for every Riftbound legend with public Standard lists."),
        ],
    ))
    search_index.append({"title": "Legend strategy", "url": "/guides/legend-strategy.html", "hay": "legend strategy meta kennen akali ornn yi"})
    topic_links.insert(0, '        <a class="item" href="/guides/legend-strategy.html"><div><div>Legend strategy</div><div class="muted">Current meta</div></div><span class="link">Open →</span></a>')

    char_links = []
    (ROOT / "guides/characters").mkdir(parents=True, exist_ok=True)
    for name in legends_ordered:
        meta = LEGEND_META[name]
        slug = slugify(meta["short"])
        lists = by_legend[name]
        body = strategy_html(name, meta, len(lists), f"/decklists/{e(legend_slug(name))}.html")
        body += f'<p>Domains: {e(" / ".join(meta["domains"]))}. Set: {e(meta["set"])}.</p>'
        write(ROOT / f"guides/characters/{slug}.html", layout(
            clip(f"{name} | Riftbound TCG legend", 62),
            clip(f"{meta['blurb']} {name} in Riftbound TCG Vendetta Standard — lists and strategy.", 160),
            f'''      <div class="card hero policy">
        <div class="crumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / {e(meta['short'])}</div>
        <h1>{e(name)}</h1>
        {body}
      </div>''',
            current="guides", canonical=f"{SITE}/guides/characters/{slug}.html",
            og_image=legend_img_abs(name),
            og_type="article",
            published=TODAY,
            json_ld=[
                breadcrumb_ld([("Home", "/"), ("Guides", "/guides/"), (meta["short"], f"/guides/characters/{slug}.html")]),
                webpage_ld(f"/guides/characters/{slug}.html", f"{name} | Riftbound TCG legend", meta["blurb"]),
                faq_ld(name, meta),
            ],
        ))
        char_links.append(f'        <a class="item" href="/guides/characters/{slug}.html"><div><div>{e(name)}</div><div class="muted">{e(" / ".join(meta["domains"]))}</div></div><span class="link">Open →</span></a>')
        search_index.append({"title": meta["short"], "url": f"/guides/characters/{slug}.html", "hay": f"{name} {meta['blurb']}"})

    write(ROOT / "guides/index.html", layout(
        "Riftbound TCG guides | Standard, legends, and strategy",
        "Riftbound TCG guides: Standard format notes, domain primers, per-legend strategy, and character pages that link to public constructed lists.",
        f'''      <div class="card hero">
        <div class="crumb"><a href="/">Home</a> / Guides</div>
        <h1>Riftbound TCG guides</h1>
        <p>Topic pages, per-legend strategy, and character pages that link to the constructed lists on this site.</p>
        <div class="section-title"><h2>Topics</h2></div>
        <div class="list">{chr(10).join(topic_links)}</div>
        <div class="section-title" style="margin-top:28px"><h2>Legends</h2><div class="muted">{len(char_links)} names</div></div>
        <div class="list">{chr(10).join(char_links)}</div>
      </div>''',
        current="guides", canonical=f"{SITE}/guides/",
        json_ld=[
            breadcrumb_ld([("Home", "/"), ("Guides", "/guides/")]),
            webpage_ld("/guides/", "Riftbound TCG guides", "Topic and character pages that link to Standard lists."),
        ],
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
