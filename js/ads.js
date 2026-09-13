(function () {
  var cfg = window.RBDB_ADS || {};
  var client = (cfg.adsenseClient || "").trim();
  var enabled = !!cfg.enabled && !!client;

  function hideSlots() {
    document.querySelectorAll("[data-ad-slot]").forEach(function (el) {
      el.hidden = true;
    });
  }

  function fillAdsense(slot) {
    var ins = document.createElement("ins");
    ins.className = "adsbygoogle";
    ins.style.display = "block";
    ins.setAttribute("data-ad-client", client);
    ins.setAttribute("data-ad-slot", slot.getAttribute("data-ad-slot") || "");
    ins.setAttribute("data-ad-format", slot.getAttribute("data-ad-format") || "auto");
    ins.setAttribute("data-full-width-responsive", "true");
    slot.appendChild(ins);
    slot.hidden = false;
    try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (err) {}
  }

  function boot() {
    var slots = document.querySelectorAll("[data-ad-slot]");
    if (!enabled) {
      hideSlots();
      return;
    }
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(client);
    s.crossOrigin = "anonymous";
    s.onload = function () {
      slots.forEach(fillAdsense);
    };
    document.head.appendChild(s);
    if (cfg.adsenseAutoAds) {
      try { (window.adsbygoogle = window.adsbygoogle || []).push({ google_ad_client: client, enable_page_level_ads: true }); } catch (err) {}
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
