(function () {
  var COPY_LABEL = "Copy list";

  function textList(root) {
    return Array.prototype.map.call(root.querySelectorAll(".text-line"), function (line) {
      var qty = (line.querySelector(".qty") || {}).textContent || "";
      var name = (line.querySelector(".card-title") || {}).textContent || "";
      qty = qty.replace(/\s+/g, "");
      name = name.trim();
      if (!qty || !name) return "";
      if (qty.slice(-1) !== "x") qty += "x";
      return qty + " " + name;
    }).filter(Boolean).join("\n");
  }

  function simText(btn) {
    var raw = btn.getAttribute("data-sim");
    if (raw && raw.trim()) return raw.trim().split(/\s*\|\|\s*/).join("\n");
    var root = btn.closest(".text-deck") || document;
    return textList(root);
  }

  function initCopy() {
    document.querySelectorAll("[data-copy-sim]").forEach(function (btn) {
      if (btn.dataset.bound) return;
      btn.dataset.bound = "1";
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var text = simText(btn);
        if (!text) return;
        var done = function () {
          var prev = btn.textContent;
          btn.textContent = "Copied";
          setTimeout(function () { btn.textContent = prev; }, 1400);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done).catch(function () {
            window.prompt("Copy this Riftbound list", text);
          });
        } else {
          window.prompt("Copy this Riftbound list", text);
        }
      });
    });
  }

  function initFilters() {
    document.querySelectorAll("[data-hub-filters]").forEach(function (bar) {
      if (bar.dataset.bound) return;
      bar.dataset.bound = "1";
      var section = bar.closest(".deck-index");
      if (!section) return;
      var items = section.querySelectorAll("ul.list > li");
      var countEl = section.querySelector(".section-title .muted");
      var total = items.length;
      function apply() {
        var q = ((bar.querySelector("[data-filter=q]") || {}).value || "").toLowerCase();
        var when = (bar.querySelector("[data-filter=when]") || {}).value || "";
        var place = (bar.querySelector("[data-filter=place]") || {}).value || "";
        var event = (bar.querySelector("[data-filter=event]") || {}).value || "";
        var shown = 0;
        items.forEach(function (li) {
          var hay = (li.textContent || "").toLowerCase();
          var date = li.getAttribute("data-date") || "";
          var placing = parseInt(li.getAttribute("data-placing") || "9999", 10);
          var bucket = li.getAttribute("data-event") || "other";
          var ok = true;
          if (q && hay.indexOf(q) < 0) ok = false;
          if (when === "aug" && (date < "2026-08-01" || date >= "2026-09-01")) ok = false;
          if (when === "sep" && date < "2026-09-01") ok = false;
          if (place === "top8" && placing > 8) ok = false;
          if (place === "win" && placing !== 1) ok = false;
          if (event && bucket !== event) ok = false;
          li.hidden = !ok;
          if (ok) shown += 1;
        });
        if (countEl) countEl.textContent = shown === total ? total + " lists" : shown + " of " + total;
      }
      bar.addEventListener("input", apply);
      bar.addEventListener("change", apply);
    });
  }

  var THEME_COOKIE = "rbdb-theme";

  function readThemeCookie() {
    var m = document.cookie.match(/(?:^|; )rbdb-theme=(dark|light)(?:;|$)/);
    return m ? m[1] : "";
  }

  function writeThemeCookie(theme) {
    var parts = [THEME_COOKIE + "=" + theme, "path=/", "max-age=31536000", "SameSite=Lax"];
    if (location.protocol === "https:") parts.push("Secure");
    document.cookie = parts.join("; ");
  }

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function applyTheme(theme, persist) {
    theme = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", theme);
    if (persist !== false) writeThemeCookie(theme);
    var btn = document.getElementById("theme-toggle");
    var dark = theme === "dark";
    if (btn) {
      btn.setAttribute("aria-checked", dark ? "true" : "false");
      btn.setAttribute("aria-label", dark ? "Dark mode" : "Light mode");
      btn.title = dark ? "Switch to light mode" : "Switch to dark mode";
    }
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", dark ? "#13110f" : "#b42318");
    try {
      window.dispatchEvent(new CustomEvent("rbdb-theme", { detail: theme }));
    } catch (err) {}
  }

  function initTheme() {
    var saved = readThemeCookie();
    applyTheme(saved || currentTheme(), !!saved);
    var btn = document.getElementById("theme-toggle");
    if (!btn || btn.dataset.bound) return;
    btn.dataset.bound = "1";
    btn.addEventListener("click", function () {
      applyTheme(currentTheme() === "dark" ? "light" : "dark", true);
    });
  }

  function initYear() {
    var el = document.getElementById("year");
    if (el) el.textContent = String(new Date().getFullYear());
  }

  function initPops() {
    document.querySelectorAll(".text-line").forEach(function (line) {
      line.addEventListener("click", function () {
        line.classList.toggle("is-open");
      });
    });
  }

  function initSharePie() {
    var svg = document.querySelector(".share-pie-svg");
    var root = document.querySelector(".share-pie-card");
    if (!svg || !root) return;

    function frame() {
      var desk = svg.getAttribute("data-desktop-viewbox");
      var mob = svg.getAttribute("data-mobile-viewbox");
      if (window.matchMedia("(max-width:700px)").matches && mob) svg.setAttribute("viewBox", mob);
      else if (desk) svg.setAttribute("viewBox", desk);
    }
    frame();
    window.addEventListener("resize", frame);

    function setOn(id, on) {
      var nodes = root.querySelectorAll('[data-share-id="' + id + '"]');
      nodes.forEach(function (n) {
        if (on) n.classList.add("is-on");
        else n.classList.remove("is-on");
      });
      if (on) svg.classList.add("is-hovering");
      else if (!root.querySelector(".is-on")) svg.classList.remove("is-hovering");
    }
    root.querySelectorAll("[data-share-id]").forEach(function (el) {
      var id = el.getAttribute("data-share-id");
      if (!id) return;
      el.addEventListener("mouseenter", function () { setOn(id, true); });
      el.addEventListener("mouseleave", function () { setOn(id, false); });
      el.addEventListener("focus", function () { setOn(id, true); });
      el.addEventListener("blur", function () { setOn(id, false); });
    });
  }

  function boot() {
    initTheme();
    initYear();
    initCopy();
    initFilters();
    initPops();
    initSharePie();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
