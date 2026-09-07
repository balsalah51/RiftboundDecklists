(function () {
  var FALLBACK_PARTNER = "https://partner.tcgplayer.com/c/7670706/1780961/21018";
  var CFG = window.RBDB_TCGPLAYER || window.OPDB_TCGPLAYER || {};
  var PRODUCT_LINE = "Riftbound";
  var SEARCH_LINE = "riftbound";
  var REL = "noopener nofollow sponsored";

  function partnerLink() {
    return (CFG.partnerLink || FALLBACK_PARTNER).trim() || FALLBACK_PARTNER;
  }

  function affiliate(dest) {
    if (!dest) return dest;
    if (dest.indexOf("partner.tcgplayer.com") >= 0) return dest;
    var base = partnerLink();
    return base + (base.indexOf("?") >= 0 ? "&" : "?") + "u=" + encodeURIComponent(dest);
  }

  function cardSearchUrl(name) {
    return "https://www.tcgplayer.com/search/" + SEARCH_LINE + "/product?q=" +
      encodeURIComponent(name) + "&productLineName=" + encodeURIComponent(SEARCH_LINE);
  }

  function uniqueCards(cards) {
    var out = [];
    var seen = {};
    (cards || []).forEach(function (row) {
      var qty = row[0];
      var name = (row[1] || "").trim();
      if (!qty || !name || seen[name]) return;
      seen[name] = 1;
      out.push([qty, name]);
    });
    return out;
  }

  function massLine(qty, name) {
    return qty + " " + name;
  }

  function massQuery(cards) {
    return uniqueCards(cards).map(function (row) {
      return massLine(row[0], row[1]);
    }).join("||");
  }

  function massText(cards) {
    return uniqueCards(cards).map(function (row) {
      return massLine(row[0], row[1]);
    }).join("\n");
  }

  function massDest(cards) {
    var q = "productline=" + encodeURIComponent(PRODUCT_LINE);
    var c = massQuery(cards || []);
    if (c) q += "&c=" + encodeURIComponent(c);
    return "https://www.tcgplayer.com/massentry?" + q;
  }

  function massBoxUrl(cards) {
    return affiliate(massDest(cards || []));
  }

  function copyText(text) {
    if (!text) return false;
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;left:-9999px;top:0";
      document.body.appendChild(ta);
      ta.select();
      ta.setSelectionRange(0, text.length);
      var ok = document.execCommand("copy");
      document.body.removeChild(ta);
      if (ok) return true;
    } catch (e) {}
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(function () {});
    }
    return false;
  }

  function openMassEntry(cards, ev) {
    var url = massBoxUrl(cards);
    copyText(massText(cards));
    var win = window.open(url, "_blank", "noopener");
    if (win && ev) {
      ev.preventDefault();
      ev.stopPropagation();
    }
    return url;
  }

  function cardsFromTextDeck(root) {
    var cards = [];
    var seen = {};
    Array.prototype.forEach.call((root || document).querySelectorAll(".text-line"), function (line) {
      var qty = parseInt(((line.querySelector(".qty") || {}).textContent || "").replace(/\D/g, ""), 10);
      var name = ((line.querySelector(".card-title") || {}).textContent || "").trim();
      if (!qty || !name || seen[name]) return;
      seen[name] = 1;
      cards.push([qty, name]);
    });
    return cards;
  }

  function buyLink(href, label, className) {
    var a = document.createElement("a");
    a.className = className;
    a.href = href;
    a.target = "_blank";
    a.rel = REL;
    a.textContent = label;
    a.addEventListener("click", function (e) { e.stopPropagation(); });
    return a;
  }

  function listBuyLink(cards, label, className) {
    var a = buyLink(massBoxUrl(cards), label, className);
    a.addEventListener("click", function (e) { openMassEntry(cards, e); });
    return a;
  }

  function addListButtons() {
    document.querySelectorAll(".text-deck .section-title").forEach(function (title) {
      if (title.querySelector(".buy-tcg")) return;
      var root = title.closest(".text-deck");
      var cards = cardsFromTextDeck(root);
      if (!cards.length) return;
      title.appendChild(listBuyLink(cards, "Buy list on TCGplayer", "buy-tcg"));
    });
  }

  function addHubButtons() {
    document.querySelectorAll(".list-row").forEach(function (row) {
      if (row.querySelector(".buy-tcg")) return;
      var btn = row.querySelector("[data-copy-sim]");
      var sim = btn ? btn.getAttribute("data-sim") : "";
      var cards = [];
      if (sim) {
        sim.split(/\s*\|\|\s*/).forEach(function (part) {
          var m = part.trim().match(/^(\d+)\s*[x×]\s+(.+)$/i);
          if (m) cards.push([parseInt(m[1], 10), m[2].trim()]);
        });
      }
      if (!cards.length) return;
      row.appendChild(listBuyLink(cards, "Buy on TCGplayer", "buy-tcg"));
    });
  }

  function addCardButtons() {
    document.querySelectorAll(".text-line").forEach(function (line) {
      if (line.querySelector(".buy-tcg-inline")) return;
      var name = ((line.querySelector(".card-title") || {}).textContent || "").trim();
      if (!name) return;
      line.appendChild(buyLink(affiliate(cardSearchUrl(name)), "Buy", "buy-tcg-inline"));
    });
    document.querySelectorAll(".card-entry").forEach(function (entry) {
      if (entry.querySelector(".buy-tcg-inline")) return;
      var name = ((entry.querySelector("h4") || {}).textContent || "").trim();
      if (!name) return;
      var wrap = entry.querySelector("div") || entry;
      wrap.appendChild(buyLink(affiliate(cardSearchUrl(name)), "Buy on TCGplayer", "buy-tcg-inline"));
    });
  }

  window.RBDB_TCG = {
    affiliate: affiliate,
    cardSearchUrl: cardSearchUrl,
    massBoxUrl: massBoxUrl,
    openMassEntry: openMassEntry
  };

  function ready() {
    addListButtons();
    addHubButtons();
    addCardButtons();
  }

  function boot() {
    fetch("/data/tcgplayer.json", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : {}; })
      .catch(function () { return {}; })
      .then(function (cfg) {
        if (cfg && cfg.partnerLink) CFG.partnerLink = String(cfg.partnerLink);
        ready();
      });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
