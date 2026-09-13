"""Unique long-form copy for topic guide pages (thin stubs hurt rankings)."""

RELATED = {
    "riftbound": [("/guides/riftbound-tcg.html", "Riftbound TCG"), ("/guides/standard.html", "Standard"), ("/format.html", "Format")],
    "riftbound-tcg": [("/guides/riftbound.html", "Riftbound"), ("/guides/legend.html", "Legend"), ("/decklists/", "Legend lists")],
    "league-of-legends-tcg": [("/guides/riftbound.html", "Riftbound"), ("/guides/riot-games.html", "Riot Games")],
    "standard": [("/format.html", "Format"), ("/guides/vendetta.html", "Vendetta"), ("/guides/radiance.html", "Radiance")],
    "vendetta": [("/guides/standard.html", "Standard"), ("/guides/radiance.html", "Radiance"), ("/tier-list.html", "Tier list")],
    "radiance": [("/events.html", "Events"), ("/guides/standard.html", "Standard")],
    "origins": [("/guides/standard.html", "Standard"), ("/guides/spiritforged.html", "Spiritforged")],
    "spiritforged": [("/guides/unleashed.html", "Unleashed"), ("/guides/standard.html", "Standard")],
    "unleashed": [("/guides/legend.html", "Legend"), ("/guides/master-yi-strategy.html", "Master Yi strategy")],
    "legend": [("/decklists/", "Legend hubs"), ("/guides/chosen-champion.html", "Chosen Champion"), ("/guides/legend-strategy.html", "Strategy")],
    "chosen-champion": [("/guides/legend.html", "Legend"), ("/format.html", "Format")],
    "runes": [("/guides/domains.html", "Domains"), ("/guides/channel.html", "Channel")],
    "battlefields": [("/guides/conquer.html", "Conquer"), ("/guides/hold.html", "Hold")],
    "domains": [("/guides/fury.html", "Fury"), ("/guides/calm.html", "Calm"), ("/guides/mind.html", "Mind")],
    "summoner-skirmish": [("/events.html", "Events"), ("/guides/nexus-nights.html", "Nexus Nights")],
    "regional-qualifier": [("/events.html", "Events"), ("/guides/showdown-series.html", "Showdown Series")],
    "showdown-series": [("/events.html", "Events"), ("/guides/regional-qualifier.html", "Regional Qualifier")],
    "nexus-nights": [("/guides/locals.html", "Locals"), ("/events.html", "Events")],
    "conquer": [("/guides/hold.html", "Hold"), ("/guides/fury.html", "Fury")],
    "hold": [("/guides/conquer.html", "Conquer"), ("/guides/calm.html", "Calm")],
    "channel": [("/guides/runes.html", "Runes"), ("/guides/conquer.html", "Conquer")],
    "sideboard": [("/format.html", "Format"), ("/guides/standard.html", "Standard")],
    "starter-decks": [("/guides/constructed.html", "Constructed"), ("/guides/legend.html", "Legend")],
    "riftbound-meta": [("/tier-list.html", "Tier list"), ("/guides/legend-strategy.html", "Legend strategy")],
    "riot-games": [("/guides/uvs-games.html", "UVS Games"), ("/guides/playriftbound.html", "PlayRiftbound")],
    "uvs-games": [("/guides/riot-games.html", "Riot Games"), ("/guides/playriftbound.html", "PlayRiftbound")],
    "piltover-archive": [("/guides/playriftbound.html", "PlayRiftbound"), ("/decklists/", "Lists")],
    "playriftbound": [("/events.html", "Events"), ("/guides/regional-qualifier.html", "Regional Qualifier")],
    "constructed": [("/format.html", "Format"), ("/guides/standard.html", "Standard")],
    "locals": [("/guides/nexus-nights.html", "Nexus Nights"), ("/guides/showdown-series.html", "Showdown Series")],
    "fury": [("/guides/domains.html", "Domains"), ("/guides/conquer.html", "Conquer"), ("/guides/rengar-strategy.html", "Rengar")],
    "calm": [("/guides/hold.html", "Hold"), ("/guides/ornn-strategy.html", "Ornn")],
    "mind": [("/guides/ornn-strategy.html", "Ornn"), ("/guides/domains.html", "Domains")],
    "body": [("/guides/master-yi-strategy.html", "Master Yi"), ("/guides/rengar-strategy.html", "Rengar")],
    "chaos": [("/guides/kennen-strategy.html", "Kennen"), ("/guides/domains.html", "Domains")],
    "order": [("/guides/kennen-strategy.html", "Kennen"), ("/guides/azir-strategy.html", "Azir")],
}

EXTRA = {
    "riftbound": """
<p>Riftbound is a paper trading card game set in League of Legends. English organized play is run with UVS Games. This fan site tracks <strong>Standard constructed</strong> lists from public tournaments: Regional Qualifiers, Showdown Series, City Challenges, and similar events.</p>
<p>A competitive 1v1 deck is one Legend, one Chosen Champion, a 40-card main, three unique Battlefields, and twelve Runes. Scoring comes from conquering and holding battlefields. Lists on this site are copied from public results so you can copy a list, buy the singles, and read current-meta strategy per Legend.</p>
<p>Riftbound is not Legends of Runeterra. If you landed here looking for the digital card game, this archive will not help you. If you are registering for a 2026 Regional Qualifier or a Showdown, start with the <a href="/tier-list.html">Vendetta Standard tier list</a> and the <a href="/guides/legend-strategy.html">legend strategy index</a>.</p>
""",
    "riftbound-tcg": """
<p>Search engines and shops often label the game <strong>Riftbound TCG</strong>. Same product: Riot's League of Legends trading card game. Constructed decks on this site follow Standard legality for 2026 organized play.</p>
<p>The identity card is a Legend, not a leader. Your Legend locks which two domains you may play. Typical regional pairs in August–September 2026 are Chaos-Order Kennen and Body-Calm Master Yi, Wuju Bladesman, with Ornn and Akali as the legends that actually won Regional Qualifiers in this window.</p>
<p>Browse <a href="/decklists/">legend hubs</a> for public lists, or open <a href="/shop/">table gear</a> if you need sleeves and a box before an event.</p>
""",
    "league-of-legends-tcg": """
<p>Riftbound is the League of Legends trading card game. It shares champions, regions, and names with the video game, but the paper rules are its own. It is not Legends of Runeterra, and it is not a video-game client.</p>
<p>This archive republishes public Standard constructed lists for commentary. Official rules, banlist notes, and organized play live on <a href="https://playriftbound.com/en-us/news/" target="_blank" rel="noopener">playriftbound.com</a>. Official card tools live on <a href="https://piltoverarchive.com/" target="_blank" rel="noopener">Piltover Archive</a>.</p>
""",
    "standard": """
<p>Standard is the only constructed format used in 2026 Riftbound organized play. There is no Eternal split yet. If a Regional Qualifier, Showdown, or City Challenge posts lists, they are Standard unless the event packet says otherwise.</p>
<p>As of September 2026, Standard includes Origins, Origins: Proving Grounds, Spiritforged, Unleashed, and Vendetta. Radiance (23 October 2026) enters Standard in time for the European Regional Championship in Stuttgart and the North American Regional Championship in Las Vegas.</p>
<p>Deck construction: 40 in the main, up to three copies, one Legend outside the 40, one Chosen Champion, three unique Battlefields, twelve Runes, and a best-of-three sideboard of 0 or 8 in the core rules (some 2026 packets use 10). Full notes: <a href="/format.html">format page</a>.</p>
""",
    "vendetta": """
<p>Vendetta (VEN) released 31 July 2026. It is the newest set in Standard until Radiance. Regional Qualifiers in Barcelona, Wuhan, and Singapore were Vendetta Standard events. Kennen, Akali, Ornn, Jayce, Rek'Sai, and several other current staples are Vendetta legends or gained Vendetta tools.</p>
<p>When you copy a list from this site dated August or September 2026, assume Vendetta is legal. Check the event packet if you are registering after Radiance lands.</p>
""",
    "radiance": """
<p>Radiance (RAD) is set 5, dated 23 October 2026. It will be Standard legal for the European Regional Championship (Stuttgart, 6–8 November) and the North American Regional Championship (Las Vegas, 11–13 December).</p>
<p>These pages do not yet have Radiance lists. Until 23 October, copy Vendetta Standard lists and watch official legality notes. Schedule digest: <a href="/events.html">events</a>.</p>
""",
    "legend": """
<p>The Legend is the identity card. It sits outside your 40-card main. It tells you which two domains you may play and what your deck is trying to do. This site organizes every public list by Legend, not by player color or by "leader."</p>
<p>Do not confuse the Legend with the Chosen Champion. The champion is a unit that starts available and counts toward the three-copy limit. The Legend does not.</p>
<p>Open a picture on the <a href="/decklists/">legends index</a>, then read that legend's current-meta plan on its hub and on the matching <a href="/guides/legend-strategy.html">strategy page</a>.</p>
""",
    "runes": """
<p>Every constructed deck has a twelve-card rune deck. The six domains are Fury, Calm, Mind, Body, Chaos, and Order. Your Legend allows two of them. Competitive lists often split unevenly — Kennen's 9 Chaos / 3 Order is the example everyone copies, then punishes.</p>
<p>Channeling runes is how you pay. Banner shorthand on this site is Channel · Conquer · Score. If a public list is missing rune counts, do not register it; incomplete submissions show up in some City Challenge pastes.</p>
""",
    "battlefields": """
<p>You register three unique Battlefields. In competitive 1v1 Duel you choose one each game. Scoring requires conquering a battlefield and then holding it. Fury decks want the conquer; Calm decks want the hold.</p>
<p>Copy the three battlefields with the rest of the list. Tournament packets care. Popular names in this scrape include Seat of Power, Emperor's Dais, Star Spring, Zaun Warrens, and Minefield.</p>
""",
    "domains": """
<p>Your Legend locks two domains. Fury is red aggression. Calm is green holds and tricks. Mind is blue draw and gear. Body is orange combat and ramp. Chaos is purple tricks. Order is yellow go-wide and spot removal.</p>
<p>August–September 2026 regional tables were dominated by Chaos-Order (Kennen) and Body-Calm (Master Yi, Wuju Bladesman), with Calm-Mind Ornn winning Barcelona and Fury-Calm Akali winning Singapore.</p>
""",
    "riftbound-meta": """
<p>Vendetta Standard after Barcelona (23 Aug), Wuhan (30 Aug), and Singapore (5–6 Sep): Kennen and Master Yi, Wuju Bladesman are the regional pair. Ornn won the first Vendetta Regional Qualifier. Akali won Singapore. Irelia, Rengar, and Azir still convert Top 8s.</p>
<p>This is a fan read of public lists, not an official ranking. The picture board lives on the <a href="/tier-list.html">tier list</a>. Game plans live on each legend hub and in <a href="/guides/legend-strategy.html">legend strategy</a>.</p>
""",
    "regional-qualifier": """
<p>Regional Qualifiers are the premier 2026 events. This window includes Barcelona (2,130+), S4 Wuhan Regional Open (~1,280), and Singapore EXPO. In 2027 Riot is renaming them Riftbound Regionals.</p>
<p>Public Top cut lists from those events are on this site. Official recaps: <a href="https://playriftbound.com/en-us/news/organizedplay/" target="_blank" rel="noopener">PlayRiftbound organized play</a>.</p>
""",
    "fury": """
<p>Fury is the red domain: accelerate, punch, and score by conquering. Rengar, Akali, Rek'Sai, Lucian, and several Chaos-Fury or Fury-Mind legends splash it.</p>
<p>If the room is sitting back on Ornn and Nasus, Fury is the punish. If the room is Irelia and Akali that never give you the second battlefield, pick a hold deck instead.</p>
""",
    "calm": """
<p>Calm is the green domain: holds, combat tricks, Defy / Discipline, and the long score. Ornn, Master Yi, Irelia, Nasus, and Akali all use it in this meta.</p>
<p>Calm wins games that go long enough to park a unit. It loses to Rengar on the play if you flood.</p>
""",
    "chaos": """
<p>Chaos is the purple domain: stacked-deck sequences, discard, hidden, and storm tools. Kennen is the default Chaos legend in Vendetta Standard.</p>
<p>The live question is not Swiss — Kennen converts. The live question is the finals, where Ornn, Irelia, and Akali have all beaten the default 9/3 draw.</p>
""",
    "order": """
<p>Order is the yellow domain: go-wide, recycle, death triggers, and spot interaction. Kennen splashes it. Azir lives in it. LeBlanc and several Mind-Order legends sit here too.</p>
""",
    "constructed": """
<p>Constructed means you build the 40 in advance. This site does not track sealed. Limited exists (six packs, 25-card decks) and uses the same Standard card pool, but those lists are not ingested here.</p>
""",
    "sideboard": """
<p>Best-of-three only. Core rules: a sideboard of exactly 0 or 8 cards. Some 2026 event packets use 10. Copy the tournament document, not a forum guess. Lists on this site include the sideboard when the public paste had one.</p>
""",
}


def html_for(title: str, slug: str, blurb: str) -> str:
    extra = EXTRA.get(slug, f"<p>{blurb}</p>")
    if slug not in EXTRA:
        extra = (
            f"<p>{blurb}</p>"
            f"<p>This page is a Riftbound TCG glossary entry for Vendetta Standard. "
            f"Use it to land on the right constructed lists and legend strategy. "
            f"Official rules stay on PlayRiftbound; this fan site republishes public lists for commentary.</p>"
        )
    links = RELATED.get(slug, [("/decklists/", "Legend lists"), ("/format.html", "Format"), ("/guides/", "Guides")])
    items = "".join(f'<li><a href="{href}">{label}</a></li>' for href, label in links)
    return f"""
        {extra}
        <h2>Related</h2>
        <ul>{items}
          <li><a href="/guides/">All guides</a></li>
          <li><a href="/search.html">Search the archive</a></li>
        </ul>
        <h2>FAQ</h2>
        <h3>Is this official?</h3>
        <p>No. Riftbound Decklists is a fan archive. Official organized play is <a href="https://playriftbound.com/en-us/news/organizedplay/" target="_blank" rel="noopener">playriftbound.com</a>.</p>
        <h3>Where are the lists?</h3>
        <p>Every public Standard list on this site is grouped by Legend on <a href="/decklists/">legend hubs</a>.</p>
"""
