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

CX, CY = 460.0, 252.0
R_OUTER = 148.0
R_INNER = 78.0
R_MID = (R_INNER + R_OUTER) / 2
R_LINE = R_OUTER + 10
INNER_MIN_PCT = 6.0
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


def _spread_ys(ys: list[float], min_gap: float, lo: float, hi: float) -> list[float]:
    if not ys:
        return []
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    placed = [ys[i] for i in order]
    for i in range(1, len(placed)):
        if placed[i] < placed[i - 1] + min_gap:
            placed[i] = placed[i - 1] + min_gap
    overflow = placed[-1] - hi
    if overflow > 0:
        placed = [y - overflow for y in placed]
    if placed[0] < lo:
        shift = lo - placed[0]
        placed = [y + shift for y in placed]
        for i in range(1, len(placed)):
            if placed[i] < placed[i - 1] + min_gap:
                placed[i] = placed[i - 1] + min_gap
    out = [0.0] * len(ys)
    for idx, y in zip(order, placed):
        out[idx] = y
    return out


def _fmt_pct(pct: float) -> str:
    if pct >= 10:
        return f"{pct:.0f}%" if abs(pct - round(pct)) < 0.05 else f"{pct:.1f}%"
    return f"{pct:.1f}%"


def pie_svg(slices: list[dict], total: int) -> str:
    if not slices or total <= 0:
        return '<p class="muted">No Vendetta-card lists to chart yet.</p>'

    angle = -math.pi / 2
    laid = []
    for sl in slices:
        sweep = (sl["pct"] / 100.0) * 2 * math.pi
        start, end = angle, angle + sweep
        mid = start + sweep / 2
        laid.append({
            **sl,
            "start": start,
            "end": end,
            "mid": mid,
            "inner": sl["pct"] >= INNER_MIN_PCT and not sl["other"],
            "other_label": sl["other"] and sl["pct"] >= INNER_MIN_PCT,
        })
        angle = end

    left = [s for s in laid if not s["inner"] and not s["other_label"] and math.cos(s["mid"]) < 0]
    right = [s for s in laid if not s["inner"] and not s["other_label"] and math.cos(s["mid"]) >= 0]
    left_ys = _spread_ys([_polar(s["mid"], R_LINE)[1] for s in left], 34, 36, 470)
    right_ys = _spread_ys([_polar(s["mid"], R_LINE)[1] for s in right], 34, 36, 470)
    for s, y in zip(left, left_ys):
        s["label_y"] = y
        s["side"] = "left"
    for s, y in zip(right, right_ys):
        s["label_y"] = y
        s["side"] = "right"

    defs = []
    paths = []
    labels = []
    callouts = []

    for i, s in enumerate(laid):
        d = _donut_path(s["start"], s["end"])
        href = e(s["href"])
        label = e(s["short"])
        paths.append(
            f'<a class="share-slice" href="{href}" data-share-id="{e(s["id"])}" aria-label="{label} {e(_fmt_pct(s["pct"]))}">'
            f'<path fill="{e(s["color"])}" d="{d}"/>'
            f"</a>"
        )
        mx, my = _polar(s["mid"], R_MID)
        if s["inner"]:
            face_r = 22 if s["pct"] >= 12 else 18
            clip_id = f"share-on-{s['id']}"
            face_cy = my - 8
            defs.append(
                f'<clipPath id="{clip_id}"><circle cx="{mx:.2f}" cy="{face_cy:.2f}" r="{face_r}"/></clipPath>'
            )
            img_y = face_cy - face_r * 1.35
            img_h = face_r * 2.7
            labels.append(
                f'<a class="share-on-slice" href="{href}" data-share-id="{e(s["id"])}">'
                f'<image href="{e(s["img"])}" x="{mx - face_r:.2f}" y="{img_y:.2f}" '
                f'width="{face_r * 2:.2f}" height="{img_h:.2f}" clip-path="url(#{clip_id})" '
                f'preserveAspectRatio="xMidYMin slice"/>'
                f'<circle cx="{mx:.2f}" cy="{face_cy:.2f}" r="{face_r}" fill="none" stroke="#fff" stroke-width="2"/>'
                f'<text class="share-on-name" x="{mx:.2f}" y="{face_cy + face_r + 14:.2f}" text-anchor="middle">{label}</text>'
                f'<text class="share-on-pct" x="{mx:.2f}" y="{face_cy + face_r + 30:.2f}" text-anchor="middle">{e(_fmt_pct(s["pct"]))}</text>'
                f"</a>"
            )
        elif s.get("other_label"):
            ox, oy = _polar(s["mid"], R_MID)
            labels.append(
                f'<text class="share-on-name" x="{ox:.2f}" y="{oy:.2f}" text-anchor="middle">Other</text>'
                f'<text class="share-on-pct" x="{ox:.2f}" y="{oy + 16:.2f}" text-anchor="middle">{e(_fmt_pct(s["pct"]))}</text>'
            )
        elif "side" in s:
            sx, sy = _polar(s["mid"], R_OUTER)
            side = s["side"]
            ly = s["label_y"]
            if side == "left":
                lx = 188
                chip_x = 8
                text_anchor = "end"
                text_x = 148
                img_x = 156
                elbow = 214
            else:
                lx = 732
                chip_x = 732
                text_anchor = "start"
                text_x = 776
                img_x = 744
                elbow = 706
            line = (
                f'M {sx:.2f} {sy:.2f} L {elbow:.2f} {ly:.2f} L {lx:.2f} {ly:.2f}'
            )
            chip_w = 180
            face_clip = f"share-call-{s['id']}"
            fy = ly
            defs.append(
                f'<clipPath id="{face_clip}"><circle cx="{img_x + 12:.2f}" cy="{fy:.2f}" r="12"/></clipPath>'
            )
            callouts.append(
                f'<g class="share-callout share-callout-{side}" data-share-id="{e(s["id"])}">'
                f'<path class="share-leader" d="{line}" fill="none" stroke="{e(s["color"])}" stroke-width="1.6"/>'
                f'<a href="{href}">'
                f'<rect x="{chip_x:.2f}" y="{ly - 16:.2f}" width="{chip_w:.2f}" height="32" rx="16" '
                f'fill="var(--surface)" stroke="{e(s["color"])}" stroke-width="1.6"/>'
                f'<image href="{e(s["img"])}" x="{img_x:.2f}" y="{fy - 16:.2f}" width="24" height="34" '
                f'clip-path="url(#{face_clip})" preserveAspectRatio="xMidYMin slice"/>'
                f'<circle cx="{img_x + 12:.2f}" cy="{fy:.2f}" r="12" fill="none" stroke="{e(s["color"])}" stroke-width="1.5"/>'
                f'<text class="share-call-name" x="{text_x:.2f}" y="{ly - 2:.2f}" text-anchor="{text_anchor}">{label}</text>'
                f'<text class="share-call-pct" x="{text_x:.2f}" y="{ly + 11:.2f}" text-anchor="{text_anchor}">{e(_fmt_pct(s["pct"]))}</text>'
                f"</a></g>"
            )

    hole = (
        f'<text class="share-hole-num" x="{CX:.0f}" y="{CY - 4:.0f}" text-anchor="middle">{total}</text>'
        f'<text class="share-hole-cap" x="{CX:.0f}" y="{CY + 16:.0f}" text-anchor="middle">Vendetta lists</text>'
    )
    return f'''<svg class="share-pie-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 520" role="img" aria-hidden="true" focusable="false" data-desktop-viewbox="0 0 920 520" data-mobile-viewbox="300 40 320 430">
  <defs>
    {"".join(defs)}
  </defs>
  <g class="share-slices">{"".join(paths)}</g>
  <circle class="share-hole-ring" cx="{CX:.0f}" cy="{CY:.0f}" r="{R_INNER - 1:.0f}" fill="var(--surface)"/>
  {hole}
  <g class="share-on-labels">{"".join(labels)}</g>
  <g class="share-callouts">{"".join(callouts)}</g>
</svg>'''


def _tier_class(tier: str) -> str:
    letter = (tier or "").lower()
    if letter in "sabcd":
        return f"tier-{letter}"
    return "tier-d"


def share_key_html(slices: list[dict]) -> str:
    rows = []
    for s in slices:
        tier = s.get("tier") or ""
        tier_html = (
            f'<span class="share-tier {_tier_class(tier)}">{e(tier)}</span>'
            if tier else
            '<span class="share-tier share-tier-none">—</span>'
        )
        rows.append(
            f'''            <li>
              <a class="share-key-row" href="{e(s["href"])}" data-share-id="{e(s["id"])}">
                <span class="share-swatch" style="background:{e(s["color"])}"></span>
                <img class="share-face" src="{e(s["img"])}" alt="" width="40" height="40" />
                <span class="share-key-name">{e(s["short"])}</span>
                <span class="share-key-count">{s["count"]} lists</span>
                <span class="share-key-pct">{e(_fmt_pct(s["pct"]))}</span>
                {tier_html}
              </a>
            </li>'''
        )
    return "\n".join(rows)


def share_section_html(slices: list[dict], total: int, pool: int, archive: int, heading="h2",
                      cta_href="/tier-list.html", cta_label="Tier list →") -> str:
    svg = pie_svg(slices, total)
    key = share_key_html(slices)
    skipped = archive - pool
    note = (
        f"Among {pool} public lists that include at least one Vendetta card, grouped by Legend. "
        f"{skipped} Origins / Unleashed / Spiritforged piles with no Vendetta cards are left out. "
        f"Percentages are of this Vendetta-card pool, not the whole archive ({archive} lists)."
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
            <div class="share-pie-canvas">
              {svg}
            </div>
            <h3 class="share-key-title">Legend</h3>
            <ul class="share-key" aria-label="Vendetta meta share by Legend">
{key}
            </ul>
          </div>
        </section>
'''
