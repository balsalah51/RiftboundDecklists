"""Current-meta strategy copy for every Standard legend on the site."""

STRAT = {
    "Kennen, Heart of the Tempest": {
        "plan": "Kennen is the default Vendetta Standard deck. You channel Chaos-Order, threaten stacked-deck plus Lightning Rush sequences, and close by holding a battlefield the opponent cannot contest through Seal of Discord and Rhasa. Swiss conversion is excellent; the live question is the finals. Ornn, Irelia, and Akali have all beaten it on the last regional table.",
        "keys": "Seal of Discord, Lightning Rush, Stacked Deck, Rhasa the Sunderer, Nocturne, Horrifying, Fizz, Trickster, Ride the Wind, Last Rites. Storm of Shuriken is the usual chosen champion; Keeper of Balance plus Baited Hook is the Order-heavy hook variant.",
        "matchups": "Good against fair midrange that cannot interact on the stack. Worse against Ornn value, greedy Irelia with a 7-drop hold, and the Singapore Akali lists that ignore your storm turn. Side Invert Timelines, Salvage, Divine Judgment, and Baron Nashor depending on the room.",
        "pick": "Play Kennen if you want the highest floor at a Regional Qualifier or a 300+ Showdown. Do not auto-pilot Game 2 — the field is built to punish the same 9 Chaos / 3 Order draw.",
    },
    "Master Yi, Wuju Bladesman": {
        "plan": "The other half of the regional pair. Body-Calm combat that scores by winning showdowns, not by storming. You ramp with Scuttle and Poro, grow with Rengar, Trophy Hunter, and punch first until the opponent cannot hold.",
        "keys": "Scuttle Crab, Lonely Poro, First Mate, Rengar, Trophy Hunter, Ruin Runner, Punch First, Defy, Discipline, Charm, Rampage, Zhonya's Hourglass. Chosen champion is Master Yi, Tempered.",
        "matchups": "Preferred into Kennen when you can keep Sabotage and Unyielding Spirit in the board. Splits with Rengar mirrors. Softer to Irelia and Akali tempo that never lets you sit on a battlefield. Ottawa and Speyer both kept Yi in Top 8 next to Kennen.",
        "pick": "Take Bladesman when you expect a Kennen-heavy Swiss and you want a deck that still functions if Discord gets taxed. Do not register Wuju Master instead — that printing is a Best-Of souvenir, not the regional shell.",
    },
    "Master Yi, Wuju Master": {
        "plan": "Origins Yi. Same domains, worse payoff in Vendetta. Barcelona still handed it a Best-Of, but Top 8s belong to Bladesman.",
        "keys": "Tempered or Honed depending on the list, Whiteflame Protector, Dazzling Aurora in older builds. Modern tables should just play Bladesman cards.",
        "matchups": "You are a step behind every Bladesman list in the room. Treat this as a collection constraint, not a meta call.",
        "pick": "Only if Bladesman is unavailable. Convert to the Unleashed legend as soon as you can.",
    },
    "Akali, Rogue Assassin": {
        "plan": "Singapore Regional Qualifier winner. Fury-Calm assassin that snowballs openings instead of racing Kennen on raw storm. The winning lists kept the SFD cheap units and added a Vendetta 7-drop plus Origins Blitzcrank, Impassive as the disruption package.",
        "keys": "Cheap empowered 2-drops, Silent / Deadly Weapon champions, VEN-028 and VEN-044 style hold units, OGN-067 Blitzcrank in the Singapore finalist shell. Punch First and combat tricks close the score.",
        "matchups": "Built to beat Kennen in a long final. Worse against go-wide Azir and against Yi that sticks Trophy Hunter first. Side extra removal for Discord and extra units for the Irelia grind.",
        "pick": "Register Akali if the room is 30%+ Kennen and you are comfortable playing from behind for a turn. This is the best 'I am not playing the bogeyman' legend in September 2026.",
    },
    "Ornn, Fire Below the Mountain": {
        "plan": "Barcelona champion. Calm-Mind forge value: gear, recycle, and a hold that Kennen cannot burn through in one storm. Two live shells — Blacksmith midrange with Sona/Hwei, and Forge God with Porobot, Time Warp, and a 7/5 Mind split.",
        "keys": "Sprite Fountain, Guardian Angel, Zhonya's Hourglass, Defy, Discipline, Emperor's Divide, Hwei, Brooding Painter, Scuttle Crab. Forge God lists add Apprentice Smith, Poro Snax, Brutalizer, Time Warp.",
        "matchups": "Favored into default Kennen if you respect the stacked-deck turn. Even with Irelia value. Worse against Rengar and Lucian that score before your gear comes online. Beijing City Challenge posted both Ornn shells in the same 123-player field.",
        "pick": "Play Ornn when you want a legend that has already beaten Kennen in a Regional Qualifier final and you can sequence gear without flooding.",
    },
    "Irelia, Blade Dancer": {
        "plan": "Calm-Chaos tempo that wins by dancing through removal and parking a unit on a battlefield. Wuhan's winner copied Akali's 7-cost hold; Beijing's City Challenge winner (旋木时光绿拐) was a cleaner Defiant Dance / Tideturner / Pyke, Returned list.",
        "keys": "Defiant Dance, Tideturner, Stellacorn Herder, Scuttle Crab, Vex, Apathetic, Pyke, Returned, Boots of Swiftness, Defy, Discipline, Stacked Deck, Irelia, Fervent.",
        "matchups": "Excellent if Kennen is taxed. The greedy VEN-044 main-deck version is for value rooms (Wuhan). The Beijing list is the one to copy for mixed Showdowns. Weak to discard-heavy Chaos and to Rengar racing the score.",
        "pick": "The right 'second legend' if you hate playing Kennen but still want Top 8 conversion. High Day 1 share at Barcelona was not a fluke.",
    },
    "Rengar, Pridestalker": {
        "plan": "Body-Fury conquer deck. Ottawa's 594-player Showdown went to a 12-0-2 Rengar stuffed with Irresistible Faefolk, Kai'Sa, Survivor, and Thrill of the Hunt. You score early and dare the opponent to hold.",
        "keys": "Rengar, Trophy Hunter, Irresistible Faefolk, Nidalee, Cat Form, Kai'Sa, Survivor, Pit Rookie, Punch First, Sabotage, Thrill of the Hunt, Rampage. Emperor's Dais / Seat of Power / Star Spring is the Ottawa battlefield trio.",
        "matchups": "Crushes slow Ornn and Nasus. Splits with Yi. Hated by well-timed Defy plus a hold, and by Kennen that storms on your score turn. Barcelona Top 8 is the regional proof; Ottawa is the Showdown proof.",
        "pick": "Play Rengar in a field that will sit back. Do not take it into a table of Irelia and Akali that never give you the second battlefield.",
    },
    "Azir, Emperor of the Sands": {
        "plan": "Calm-Order tokens. Barcelona Top 4 with Guards! and Soul Sword. Auckland 10K still posted Azir in the Top 8 next to Kennen. You go wide, recycle, and win through copy effects rather than a single bomb.",
        "keys": "Guards!, Soul Sword, Emperor's Dais, cheap soldiers, Defy, Discipline. Keep the token count above what Rhasa can sunder.",
        "matchups": "Good against linear combat. Bad against Seal of Discord and against Irelia that picks off the emperor. Side extra holds and extra copies of your go-wide payoff.",
        "pick": "A real A-tier legend if you like combat math more than stacked-deck sequencing.",
    },
    "Fiora, Grand Duelist": {
        "plan": "Body-Order duelist. Quiet at Barcelona, then a Singapore Top 8. You win single combat, not wide turns.",
        "keys": "Worthy / Victorious champion, Punch First, Challenge, En Garde, combat gear. Often shares Body cards with Yi and Sett.",
        "matchups": "Preferred into one-threat Kennen draws. Punished by go-wide Azir and by Akali that never duels fair. Wuhan put Fiora in Top 4 in a value room.",
        "pick": "A specialist anti-hero. Register it when you expect legends that present one unit at a time.",
    },
    "Diana, Scorn of the Moon": {
        "plan": "Chaos-Mind moonfall. Former regional winner that still Best-Ofs. Auckland 10K had three Dianas in the Top 10. You play spells, flip the battlefield, and grind.",
        "keys": "Lunari champion, Tideturner, Hwei, Vex, Apathetic, Stupefy, Time Warp in greedy lists, Chaos/Mind runes.",
        "matchups": "Fine into Kennen if you have discard and counter. Worse against Rengar speed. Conversion from Day 1 to Top 64 was real in Wuhan.",
        "pick": "The spell-based alternative to Ezreal in the same domains. Take Diana if you want more unit interaction and less pure draw-go.",
    },
    "Jayce, Defender of Tomorrow": {
        "plan": "Body-Mind inventor ramp. Singapore's promo legend and a real Day 2 option. You accelerate into bombs and try not to die to Lightning Rush.",
        "keys": "Brilliant Inventor, Dazzling Aurora / Platewyrm lines in some lists, Mobilize, Catalyst of Aeons, Elder Dragon in the greedy versions. NRG Milwaukee posted several Jayce Day 2s.",
        "matchups": "Wins long games vs Ornn-fair. Loses to Kennen on the play if your ramp skip is slow. Incomplete lists are common — copy a complete 62–66 card submission, not a placeholder.",
        "pick": "Play Jayce if you like ramp and the room is full of midrange, not storm.",
    },
    "Ezreal, Prodigal Explorer": {
        "plan": "Chaos-Mind spells. Singapore Top 16s on attrition. You draw, recycle, and never present a battlefield the way Yi does.",
        "keys": "Prodigy / explorer package, Stacked Deck, Time Warp in some lists, cheap cantrips, Chaos/Mind runes.",
        "matchups": "Outlasts fair Ornn. Explodes to Rengar. Can steal Game 1 vs Kennen if you have the counter suite.",
        "pick": "A B-tier legend for players who want Diana's domains with more instant-speed cards.",
    },
    "LeBlanc, Deceiver": {
        "plan": "Mind-Order clones. Best-Of at Barcelona and a Day 2 legend in Singapore. You copy, bounce, and win through extra bodies that were not in the opener.",
        "keys": "Deceiver champion, clone spells, cheap Order units, Mind draw. RCS Hobby Con put Tempo LeBlanc in the Top 4.",
        "matchups": "Tricky into Kennen because extra units eat Rhasa poorly. Better against single-threat combat. Side extra interaction.",
        "pick": "Play LeBlanc if you want a Mind legend that is not Ezreal or Viktor and you enjoy combat tricks.",
    },
    "Kha'Zix, Voidreaver": {
        "plan": "Body-Chaos evolve. Singapore Top 16 and a Barcelona Best-Of. Isolate, grow, score.",
        "keys": "Mutating Horror, Traveling Merchant, Treasure Hunter, Fizz, Void Assault, Invert Timelines in greedy lists.",
        "matchups": "Good against legends that present one unit. Bad against Azir wide and against Kennen that never 1v1s you. Keep isolation spells.",
        "pick": "A B-tier spicy Body splash if you are bored of Yi and Rengar.",
    },
    "Rek'Sai, Void Burrower": {
        "plan": "Fury-Order tunnels. One of Barcelona's larger Day 1 legends. You punch through the ground and score before the hold is built.",
        "keys": "Void burrow package, cheap Fury units, Order recycle, Punch First. Conversion to Top 64 was weaker than the Day 1 share.",
        "matchups": "Races Ornn. Loses to well-built Yi and to Kennen that storms over your tunnel. Auckland still posted Rek'Sai in the Top 16.",
        "pick": "Take Rek'Sai as an aggressive change-up, not as your Regional Qualifier lock.",
    },
    "Draven, Glorious Executioner": {
        "plan": "Chaos-Fury axes. Still a Best-Of when the table wants the old Origins pair. You spin, execute, and hope the storm decks are elsewhere.",
        "keys": "Audacious / executioner champion, axe payoffs, cheap Chaos units, Fury combat.",
        "matchups": "Can race a slow Ornn. Cannot race a good Kennen. Ottawa kept a few Dravens in the Top 32.",
        "pick": "C-tier. Fun Showdown legend, not the regional pair.",
    },
    "Vex, Gloomist": {
        "plan": "Calm-Chaos gloom. Conversion is real in stacked-deck rooms because you tax their hand and their cheer.",
        "keys": "Apathetic / Cheerless, gloom spells, Tideturner overlap with Irelia, cheap Calm.",
        "matchups": "Better against Kennen than the C-tier label suggests if you draw the tax pieces. Worse against combat-first Yi.",
        "pick": "A side-strategy legend. Register it when you have a read that the room is 40% storm.",
    },
    "Nasus, Curator of the Sands": {
        "plan": "Calm-Mind stacks. High Barcelona Day 1 count, weaker conversion — except Top Shelf Masters, where ThunderTrees won a 128-player event on Astral Heron, Thousand-Tailed Watcher, Bellows Breath, and Time Warp.",
        "keys": "Nasus, Ascended, Astral Heron, Thousand-Tailed Watcher, Ravenbloom Student, Scuttle Crab, Bellows Breath, Premonition, Time Warp. 5 Calm / 7 Mind in the winning list.",
        "matchups": "Wins the longest games in the format. Dies to Rengar and to Kennen on the play. Side Vilemaw and extra counters.",
        "pick": "Play Nasus if you want Ornn's domains with a bigger late game and you can survive the first six turns.",
    },
    "Lillia, Bashful Bloom": {
        "plan": "Calm-Mind dream-sleep. Barcelona Best-Of. You tap, bloom, and try to be Ornn with more sleep and fewer forges.",
        "keys": "Bashful Bloom champion, sleep spells, Scuttle, Calm/Mind value.",
        "matchups": "Same problem as Nasus: too slow for Rengar, too fair for Kennen. Fine in a sleepy City Challenge.",
        "pick": "C-tier. A comfort legend, not a Regional Qualifier hammer.",
    },
    "Lucian, Purifier": {
        "plan": "Body-Fury double-shot. Wuhan's best Fury-Body legend over Rengar in that particular value room. Aggressive with Kai'Sa.",
        "keys": "Purifier champion, Kai'Sa, Survivor, Punch First, Body/Fury combat.",
        "matchups": "Races Ornn. Splits with Rengar. Hated by Irelia that never lets you double-shot a hold.",
        "pick": "C-tier with a Wuhan spike. Copy a complete Wuhan or Barcelona Best-Of, not a random 40-card stub.",
    },
    "Mel, Soul's Reflection": {
        "plan": "Chaos-Mind council mage. Time Warp piles that Best-Of'd Barcelona. You play the long game with extra turns and extra spells.",
        "keys": "Time Warp, Mind draw, Chaos tricks, council payoffs.",
        "matchups": "Outlasts Nasus. Loses to anything that scores on turn four. Keep this for rooms that will let you warp.",
        "pick": "C-tier combo-adjacent. Do not take it to a Showdown full of Rengar.",
    },
    "Viktor, Herald of the Arcane": {
        "plan": "Mind-Order recruit. Low share. NRG $5k still posted a Viktor in the Top 8 on a budget list. You go wide with recruits, not with Azir tokens.",
        "keys": "Herald champion, recruit payoffs, Order wide, Mind draw.",
        "matchups": "Can steal a Swiss from people who only prepared Kennen and Yi. Collapses to real interaction.",
        "pick": "C-tier. A budget legend for a local, not your Regional Qualifier plan.",
    },
    "Lux, Lady of Luminosity": {
        "plan": "Mind-Order light. Singapore playmat promo and a fringe Day 2 legend. Control, counters, one big spell.",
        "keys": "Crownguard / luminosity champion, counters, Order recycle, Mind draw.",
        "matchups": "Can brick Kennen if the counter suite is real. Cannot beat a battlefield race. Keep it as a local control option.",
        "pick": "C-tier control. Play it if you refuse to play Ezreal and still want Mind-Order.",
    },
    "Sett, The Boss": {
        "plan": "Body-Order pit-boss. Low regional share; kuxist's Łódź Showdown list is the public proof it still functions. You brawl, punch, and call to glory.",
        "keys": "Kingpin, Pit Rookie, First Mate, Fiora, Victorious, Punch First, Sabotage, Call to Glory, Arena Bar.",
        "matchups": "Fair against other Body decks. Behind vs Kennen. Fine as a Showdown spicy.",
        "pick": "D-tier with a pulse. Register it for a 200-player Showdown, not for Singapore.",
    },
    "Pyke, Bloodharbor Ripper": {
        "plan": "Chaos-Fury execute. Best-Of at Barcelona, rare in regional Top 8s. You dock, butcher, and try to delete a unit that was supposed to hold.",
        "keys": "Dockside Butcher overlap with Rengar lists, execute spells, cheap Chaos.",
        "matchups": "A sideboard legend more than a main legend in 2026. Full Pyke legends struggle to score twice.",
        "pick": "D-tier. Steal Pyke cards for Rengar instead of forcing the legend.",
    },
    "Ambessa, Matriarch of War": {
        "plan": "Body-Order Noxus. Barcelona Best-Of with Wolf combat. You go to war, not to the storm.",
        "keys": "Wolf combat, Body units, Order recycle, Punch First.",
        "matchups": "Same slot as Sett and Fiora with worse conversion. Keep it as a Best-Of hunt, not a Swiss plan.",
        "pick": "D-tier Best-Of legend.",
    },
    "Poppy, Keeper of the Hammer": {
        "plan": "Body-Order hammer. Barcelona Best-Of in a tiny share. You keep the hammer, you keep the battlefield, you do not keep a Top 8.",
        "keys": "Paragon champion, Body units, Order go-wide, hammer payoffs.",
        "matchups": "Too slow for Kennen, too narrow for Yi. A locals legend.",
        "pick": "D-tier. Play it if it is the box you opened.",
    },
    "Vi, Piltover Enforcer": {
        "plan": "Fury-Order gauntlet. Best-Of at Barcelona; Day 2 conversion was rough. You punch a hole and hope it was the right battlefield.",
        "keys": "Peacekeeper shows up in other legends' lists more than Vi legends convert. Enforcer champion, Fury combat, Order recycle.",
        "matchups": "Vi, Peacekeeper is a Kennen and Yi card. The Vi legend is a different, worse deck.",
        "pick": "D-tier. Play Peacekeeper in Kennen; do not force the legend.",
    },
    "Shen, Eye of Twilight": {
        "plan": "Calm-Order Kinkou tank. A Best-Of legend that lives on holds. You stall, you shield, you hope they cannot storm over the temple.",
        "keys": "Kinkou champion, Disciple of Shen, Ki Barrier, Scuttle, Sona, Calm/Order runes. Leader of the Kinkou Order is a unit name, not a format term.",
        "matchups": "Holds vs combat. Folds vs Kennen storm. Fine if you are hunting a Best-Of and the table is all Yi.",
        "pick": "D-tier hold legend.",
    },
    "Renata Glasc, Chem-Baroness": {
        "plan": "Mind-Order chem-baron. Hostile Takeover and porobot lines. You buy the board instead of winning combat.",
        "keys": "Chem-Baroness champion, Hostile Takeover, Patched Porobot, Mind draw, Order recycle.",
        "matchups": "Gimmick-plus. Can steal a local. Will not survive a Regional Qualifier Swiss of Kennen and Yi.",
        "pick": "D-tier value pile.",
    },
    "Jax, Grandmaster at Arms": {
        "plan": "Body-Calm lamppost. Rampage midrange that is just worse Bladesman. Barcelona still Best-Of'd it.",
        "keys": "Grandmaster champion, Rampage, Body units, Calm tricks.",
        "matchups": "If you are going to play Body-Calm, play Wuju Bladesman.",
        "pick": "D-tier. Only when Bladesman is not in the pool.",
    },
    "Ivern, Green Father": {
        "plan": "Calm-Order Daisy. Go-wide that Best-Of'd Barcelona. You grow the forest and hope they cannot Discord it.",
        "keys": "Daisy / Green Father champion, go-wide Calm, Order tokens.",
        "matchups": "Wide vs combat. Dead vs storm. A Best-Of hunt.",
        "pick": "D-tier forest.",
    },
    "Jhin, Virtuoso": {
        "plan": "Fury-Mind four-shot. Spell-heavy Best-Of. You count to four and try to make the fourth shot the game.",
        "keys": "Virtuoso champion, Fury spells, Mind draw, four-shot payoffs.",
        "matchups": "Combo-adjacent. Loses to interaction. Do not take it to a 2,000-player RQ as your main.",
        "pick": "D-tier virtuoso.",
    },
    "Renekton, Butcher of the Sands": {
        "plan": "Body-Fury rage. Combat that still takes a Best-Of. You butcher, you rage, you are not Rengar.",
        "keys": "Butcher champion, Body units, Fury combat, Punch First.",
        "matchups": "Play Rengar instead unless you specifically want the rage package.",
        "pick": "D-tier butcher.",
    },
    "Rumble, Mechanized Menace": {
        "plan": "Fury-Mind scrap. Porobot and Production Surge. Barcelona Best-Of.",
        "keys": "Mechanized champion, Patched Porobot, Production Surge, Fury/Mind spells.",
        "matchups": "Gimmick gear. Can steal a local. Will not convert a Regional Qualifier.",
        "pick": "D-tier scrap heap.",
    },
    "Zed, Master of Shadows": {
        "plan": "Chaos-Fury clones. Still Best-Ofs in Vendetta Standard. You copy, you shadow, you try to be a combat Kennen.",
        "keys": "Master of Shadows champion, clone units, Chaos tricks, Fury combat.",
        "matchups": "Worse Kennen with extra clones. Sometimes that is enough to Best-Of. Rarely enough to Top 8.",
        "pick": "D-tier shadows.",
    },
    "Sivir, Battle Mistress": {
        "plan": "Body-Chaos ricochet. Barcelona Best-Of with dragons and stacked deck. You bounce damage and hope the dragon lands.",
        "keys": "Battle Mistress champion, ricochet payoffs, dragons, Stacked Deck.",
        "matchups": "A Best-Of curiosity. The stacked-deck copies belong in Kennen.",
        "pick": "D-tier ricochet.",
    },
    "Kai'Sa, Daughter of the Void": {
        "plan": "Fury-Mind survivor. Shenzhen City Challenge winner and 13 lists in this scrape window. You evolve, shoot hextech, and Time Warp the games that go long. Falling Star and Thousand-Tailed Watcher are the close.",
        "keys": "Kai'Sa, Survivor, Watchful Sentry, Lecturing Yordle, Brynhir Thundersong, Thousand-Tailed Watcher, Hextech Ray, Stupefy, Falling Star, Temporal Breach, Time Warp. 7 Fury / 5 Mind is the winning Shenzhen split.",
        "matchups": "Outlasts fair Ornn. Splits with Mel and Ezreal for the spell-heavy Mind pair. Hated by Rengar that scores before Survivor hits the table. Side Icathian Rain and extra execution.",
        "pick": "The best Fury-Mind legend in this window. Register it when you want a City Challenge winner that is not Kennen or Yi.",
    },
    "Teemo, Swift Scout": {
        "plan": "Chaos-Mind mushrooms. One public Showdown list in this scrape: Strategist champion, Sprite Fountain, Stacked Deck, Guerrilla Warfare, and a pile of switcheroo plus temporal breach.",
        "keys": "Teemo, Strategist, Teemo, Scout, Sprite Fountain, Stacked Deck, Switcheroo, Temporal Breach, Sprite Call, Consult the Past, Nocturne, Horrifying.",
        "matchups": "A spicy local. Do not take it to a Regional Qualifier as your main. Side Invert Timelines and Baron Nashor if you insist.",
        "pick": "D-tier scout. Fun, not the meta.",
    },
}


def html_for(name: str, meta: dict, list_count: int, list_href: str) -> str:
    row = STRAT.get(name)
    domains = " / ".join(meta.get("domains") or ())
    if not row:
        return (
            f"<p>{meta.get('blurb') or 'Public Standard legend.'}</p>"
            f"<p>Domains: {domains}. {list_count} public lists on this site.</p>"
            f'<p><a href="{list_href}">Open lists →</a></p>'
        )
    return f"""
        <p class="muted">Vendetta Standard · August–September 2026 · {domains}</p>
        <h3>Game plan</h3>
        <p>{row['plan']}</p>
        <h3>Key cards</h3>
        <p>{row['keys']}</p>
        <h3>Matchups</h3>
        <p>{row['matchups']}</p>
        <h3>When to register it</h3>
        <p>{row['pick']}</p>
        <p><a href="{list_href}">{list_count} public lists →</a></p>
"""


def hub_excerpt(name: str, meta: dict, strat_href: str) -> str:
    row = STRAT.get(name)
    if not row:
        return f'<p class="leader-take">{meta.get("blurb") or ""}</p>'
    return (
        f'<p class="leader-take">{row["plan"]}</p>'
        f'<p><a href="{strat_href}">Full {meta.get("short") or name} strategy →</a></p>'
    )
