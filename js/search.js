
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
