"""Vendetta meta-share pie: lists that include at least one current-set card."""
from __future__ import annotations

import html
import math
from collections import Counter

# Unique / signature Vendetta (VEN) cards seen in public lists plus exclusive
# VEN-legend staples. Used together with Vendetta legend identity and champion names.
VEN_UNIQUE_CARDS = {
    "Lightning Rush",
    "Seal of Discord",
    "Last Rites",
    "Shadows of the Past",
    "Atakhan",
    "Thrill of the Hunt",
    "Void Rush",
    "Void Assault",
    "Pakaa Cub",
    "Faithful Manufactor",
    "Noxian Emissary",
    "Undertitan",
    "Karthus, Eternal",
    "Ruined Rex",
    "Gutter Palace",
    "Glasc Mixologist",
    "Mirror Image",
    "Clairvoyance",
    "Rocket Barrage",
    "Rage Amplifier",
    "Shuriken Flip",
    "Mystic Vortex",
    "Seal of Focus",
    "Seal of Unity",
    "Hostile Takeover",
    "Curtain Call",
    "Public Execution",
    "Shock Blast",
    "Invert Timelines",
    "Nocturne, Horrifying",
    "Rhasa the Sunderer",
    "The Harrowing",
    "Shadow Order Disciple",
    "Downwell",
    "Pyke, Dockside Butcher",
    "Black Rose Dignitary",
    "Cloth Armor",
    "Vanguard Captain",
    "Forgefire Cape",
    "Illaoi, Prophet of the Great Kraken",
    "Shadow Temple",
    "Rebuttal",
    "Pit Crew",
    "Shurelya's Requiem",
    "Ornn, Forge God",
    "Shadow Fiend",
    "Mischievous Marai",
    "Mel, Defiant Soul",
    "Jayce, Brilliant Inventor",
    "Jayce, Man of Progress",
    "LeBlanc, Fragmented",
    "LeBlanc, Everywhere at Once",
    "Akali, Deadly Weapon",
    "Kennen, Storm of Shuriken",
    "Ornn, Blacksmith",
    "Rengar, Trophy Hunter",
}

# Distinct slice fills so neighboring domain pairs do not collide.
SLICE_COLORS = [
    "#b42318",
    "#e07a1b",
    "#c9a227",
    "#2e7d32",
    "#1565c0",
    "#6a1b9a",
    "#c2185b",
    "#00838f",
    "#5d4037",
    "#4527a0",
    "#00897b",
    "#d84315",
    "#546e7a",
    "#ad1457",
    "#33691e",
]
OTHER_COLOR = "#8d8680"

CX, CY = 200.0, 200.0
R_OUTER = 158.0
R_INNER = 88.0
R_LABEL = 178.0
NAMED_MIN_PCT = 2.0
NAMED_MIN_COUNT = 6


def e(s: str) -> str:
    return html.escape(s or "", quote=True)


def deck_card_names(deck: dict) -> set[str]:
    names = {deck.get("champion") or "", deck.get("legend") or ""}
    for section in ("main", "battlefields", "sideboard"):
        for row in deck.get(section) or []:
            if isinstance(row, (tuple, list)) and len(row) >= 2:
                names.add(row[1])
            elif isinstance(row, dict):
                names.add(row.get("name") or "")
    names.discard("")
    return names


def vendetta_prefixes(legend_meta: dict) -> tuple[str, ...]:
    out = []
    for name, meta in legend_meta.items():
        if meta.get("set") != "Vendetta":
            continue
        out.append(name)
        short = (meta.get("short") or name.split(",")[0]).strip()
        out.append(short)
        first = short.split(",")[0].strip()
        if first:
            out.append(first)
    # Longest first so "Renata Glasc" wins over "Renata"
    return tuple(sorted(set(out), key=len, reverse=True))


def card_matches_vendetta(name: str, prefixes: tuple[str, ...]) -> bool:
    if name in VEN_UNIQUE_CARDS:
        return True
    for prefix in prefixes:
        if name == prefix or name.startswith(prefix + ",") or name.startswith(prefix + " "):
            return True
    return False


def has_vendetta_cards(deck: dict, legend_meta: dict, prefixes: tuple[str, ...] | None = None) -> bool:
    meta = legend_meta.get(deck.get("legend") or "", {})
    if meta.get("set") == "Vendetta":
        return True
    prefixes = prefixes if prefixes is not None else vendetta_prefixes(legend_meta)
    for name in deck_card_names(deck):
        if card_matches_vendetta(name, prefixes):
            return True
    return False


def _round_pcts(counts: list[int], total: int) -> list[float]:
    if total <= 0:
        return [0.0] * len(counts)
    raw = [c * 100.0 / total for c in counts]
    rounded = [round(x, 1) for x in raw]
    delta = round(100.0 - sum(rounded), 1)
    if rounded:
        idx = max(range(len(rounded)), key=lambda i: raw[i])
        rounded[idx] = round(rounded[idx] + delta, 1)
    return rounded


def share_slices(decks: list[dict], legend_meta: dict, legend_img, legend_slug) -> tuple[list[dict], int]:
    prefixes = vendetta_prefixes(legend_meta)
    pool = [d for d in decks if has_vendetta_cards(d, legend_meta, prefixes)]
    total = len(pool)
    counts = Counter(d["legend"] for d in pool)
    ranked = counts.most_common()

    named: list[tuple[str, int]] = []
    other = 0
    for name, n in ranked:
        pct = 100.0 * n / total if total else 0
        if n >= NAMED_MIN_COUNT or pct >= NAMED_MIN_PCT:
            named.append((name, n))
        else:
            other += n

    counts_list = [n for _, n in named]
    if other:
        counts_list.append(other)
    pcts = _round_pcts(counts_list, total)

    slices = []
    for i, (name, n) in enumerate(named):
        meta = legend_meta.get(name, {})
        short = meta.get("short") or name.split(",")[0]
        img = legend_img(name)
        slices.append({
            "id": f"leg-{i}",
            "legend": name,
            "short": short,
            "count": n,
            "pct": pcts[i],
            "img": img,
            "slug": legend_slug(name),
            "tier": meta.get("tier") or "D",
            "color": SLICE_COLORS[i % len(SLICE_COLORS)],
            "href": f"/decklists/{legend_slug(name)}.html",
            "other": False,
        })
    if other:
        slices.append({
            "id": "other",
            "legend": "Other legends",
            "short": "Other",
            "count": other,
            "pct": pcts[-1],
            "img": "/img/card-back.jpg",
            "slug": "",
            "tier": "",
            "color": OTHER_COLOR,
            "href": "/decklists/",
            "other": True,
        })
    return slices, total


def _polar(ang: float, r: float) -> tuple[float, float]:
    return CX + r * math.cos(ang), CY + r * math.sin(ang)


def _donut_path(start: float, end: float) -> str:
    sweep = end - start
    if sweep <= 0:
        return ""
    # Full circle — SVG arcs cannot be a complete 360°.
    if sweep >= 2 * math.pi - 1e-6:
        outer_a = _polar(start, R_OUTER)
        outer_b = _polar(start + math.pi, R_OUTER)
        inner_a = _polar(start, R_INNER)
        inner_b = _polar(start + math.pi, R_INNER)
        return (
            f"M {outer_a[0]:.2f} {outer_a[1]:.2f} "
            f"A {R_OUTER:.2f} {R_OUTER:.2f} 0 1 1 {outer_b[0]:.2f} {outer_b[1]:.2f} "
            f"A {R_OUTER:.2f} {R_OUTER:.2f} 0 1 1 {outer_a[0]:.2f} {outer_a[1]:.2f} "
            f"M {inner_a[0]:.2f} {inner_a[1]:.2f} "
            f"A {R_INNER:.2f} {R_INNER:.2f} 0 1 0 {inner_b[0]:.2f} {inner_b[1]:.2f} "
            f"A {R_INNER:.2f} {R_INNER:.2f} 0 1 0 {inner_a[0]:.2f} {inner_a[1]:.2f} Z"
        )
    large = 1 if sweep > math.pi else 0
    x0, y0 = _polar(start, R_OUTER)
    x1, y1 = _polar(end, R_OUTER)
    x2, y2 = _polar(end, R_INNER)
    x3, y3 = _polar(start, R_INNER)
    return (
        f"M {x0:.2f} {y0:.2f} "
        f"A {R_OUTER:.2f} {R_OUTER:.2f} 0 {large} 1 {x1:.2f} {y1:.2f} "
        f"L {x2:.2f} {y2:.2f} "
        f"A {R_INNER:.2f} {R_INNER:.2f} 0 {large} 0 {x3:.2f} {y3:.2f} Z"
    )


def _fmt_pct(pct: float) -> str:
    if pct >= 10:
        return f"{pct:.0f}%" if abs(pct - round(pct)) < 0.05 else f"{pct:.1f}%"
    return f"{pct:.1f}%"


def pie_svg(slices: list[dict], total: int) -> str:
    if not slices or total <= 0:
        return '<p class="muted">No Vendetta-card lists to chart yet.</p>'

    angle = -math.pi / 2
    paths = []
    labels = []
    for sl in slices:
        sweep = (sl["pct"] / 100.0) * 2 * math.pi
        start, end = angle, angle + sweep
        mid = start + sweep / 2
        d = _donut_path(start, end)
        href = e(sl["href"])
        label = e(sl["short"])
        paths.append(
            f'<a class="share-slice" href="{href}" data-share-id="{e(sl["id"])}" '
            f'aria-label="{label} {e(_fmt_pct(sl["pct"]))}">'
            f'<path fill="{e(sl["color"])}" d="{d}"/>'
            f"</a>"
        )
        if sl["pct"] >= 8:
            lx, ly = _polar(mid, R_LABEL)
            labels.append(
                f'<text class="share-slice-pct" x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                f'dominant-baseline="middle">{e(_fmt_pct(sl["pct"]))}</text>'
            )
        angle = end

    return f'''<svg class="share-pie-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" role="img" aria-hidden="true" focusable="false">
  <g class="share-slices">{"".join(paths)}</g>
  <circle class="share-hole-ring" cx="{CX:.0f}" cy="{CY:.0f}" r="{R_INNER - 1:.0f}" fill="var(--surface)"/>
  <text class="share-hole-num" x="{CX:.0f}" y="{CY - 6:.0f}" text-anchor="middle">{total}</text>
  <text class="share-hole-cap" x="{CX:.0f}" y="{CY + 16:.0f}" text-anchor="middle">lists</text>
  <g class="share-pct-labels">{"".join(labels)}</g>
</svg>'''


def _tier_class(tier: str) -> str:
    letter = (tier or "").lower()
    if letter in "sabcd":
        return f"tier-{letter}"
    return "tier-d"


def share_featured_html(slices: list[dict]) -> str:
    featured = [s for s in slices if not s.get("other")][:5]
    cards = []
    for i, s in enumerate(featured):
        cards.append(
            f'''            <li class="share-featured-item" style="--i:{i}">
              <a href="{e(s["href"])}" data-share-id="{e(s["id"])}">
                <img class="share-card-img" src="{e(s["img"])}" alt="{e(s["short"])} legend card" width="186" height="260" />
                <span class="share-featured-pct">{e(_fmt_pct(s["pct"]))}</span>
                <span class="share-featured-name">{e(s["short"])}</span>
              </a>
            </li>'''
        )
    return "\n".join(cards)


def share_key_html(slices: list[dict]) -> str:
    rows = []
    for s in slices:
        tier = s.get("tier") or ""
        tier_html = (
            f'<span class="share-tier {_tier_class(tier)}">{e(tier)}</span>'
            if tier else
            '<span class="share-tier share-tier-none">—</span>'
        )
        img = (
            f'<img class="share-card-thumb" src="{e(s["img"])}" alt="" width="52" height="72" />'
            if not s.get("other") else
            '<span class="share-card-thumb share-card-thumb-empty" aria-hidden="true"></span>'
        )
        rows.append(
            f'''            <li>
              <a class="share-key-row" href="{e(s["href"])}" data-share-id="{e(s["id"])}">
                <span class="share-swatch" style="background:{e(s["color"])}"></span>
                {img}
                <span class="share-key-copy">
                  <span class="share-key-name">{e(s["short"])}</span>
                  <span class="share-key-count">{s["count"]} lists</span>
                </span>
                <span class="share-key-pct">{e(_fmt_pct(s["pct"]))}</span>
                {tier_html}
              </a>
            </li>'''
        )
    return "\n".join(rows)


def share_section_html(slices: list[dict], total: int, pool: int, archive: int, heading="h2",
                      cta_href="/tier-list.html", cta_label="Tier list →") -> str:
    svg = pie_svg(slices, total)
    featured = share_featured_html(slices)
    key = share_key_html(slices)
    skipped = archive - pool
    note = (
        f"Among {pool} public lists that include at least one Vendetta card, grouped by Legend. "
        f"{skipped} lists with no Vendetta cards are left out. "
        f"Share is of this pool, not the whole archive ({archive} lists)."
    )
    return f'''        <section class="home-leaders-flow share-pie-flow" id="meta-share">
          <div class="home-leaders-intro">
            <p class="home-leaders-kicker">Current set</p>
            <div class="home-leaders-intro-row">
              <div>
                <{heading}>Vendetta meta share</{heading}>
                <p>Most-played legends among lists that actually run Vendetta cards.</p>
              </div>
              <a href="{e(cta_href)}">{e(cta_label)}</a>
            </div>
          </div>
          <div class="card home-panel share-pie-card">
            <p class="muted share-pie-note">{e(note)}</p>
            <div class="share-pro">
              <div class="share-pie-canvas">
                {svg}
              </div>
              <ol class="share-featured" aria-label="Top legends">
{featured}
              </ol>
            </div>
            <h3 class="share-key-title">By Legend</h3>
            <ul class="share-key" aria-label="Vendetta meta share by Legend">
{key}
            </ul>
          </div>
        </section>
'''
