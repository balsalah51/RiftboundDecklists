(function () {
  var REL = "noopener nofollow sponsored";
  var AFF = window.RBDB_AFFILIATES || {};

  function cardmarketSearch(name) {
    var url = "https://www.cardmarket.com/en/Riftbound/Products/Search?searchString=" + encodeURIComponent(name);
    if (AFF.cardmarketId) url += "&affiliateId=" + encodeURIComponent(AFF.cardmarketId);
    return url;
  }

  function ebaySearch(name) {
    var q = name + " Riftbound";
    var url = "https://www.ebay.com/sch/i.html?_nkw=" + encodeURIComponent(q);
    if (AFF.ebayCampId) {
      url += "&mkcid=1&mkrid=711-53200-19255-0&campid=" + encodeURIComponent(AFF.ebayCampId) + "&toolid=10001";
    }
    return url;
  }

  function link(href, label, className) {
    var a = document.createElement("a");
    a.className = className || "retailer-link";
    a.href = href;
    a.target = "_blank";
    a.rel = REL;
    a.textContent = label;
    return a;
  }

  function addDeckExtras() {
    document.querySelectorAll(".text-deck .section-title").forEach(function (title) {
      if (title.querySelector(".retailer-row")) return;
      var h = title.querySelector("h3");
      var name = document.querySelector(".card-entry h4");
      var q = name ? name.textContent.trim() : "Riftbound";
      var row = document.createElement("div");
      row.className = "retailer-row";
      row.appendChild(link(cardmarketSearch(q || "Riftbound"), "Cardmarket", "retailer-link"));
      row.appendChild(link(ebaySearch(q || "Riftbound TCG"), "eBay", "retailer-link"));
      if (AFF.cardnexusUrl) row.appendChild(link(AFF.cardnexusUrl, "CardNexus", "retailer-link"));
      title.appendChild(row);
    });
  }

  function boot() {
    addDeckExtras();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
