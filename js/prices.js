(function () {
  function affiliate(dest) {
    var base = (window.RBDB_TCGPLAYER && window.RBDB_TCGPLAYER.partnerLink) ||
      "https://partner.tcgplayer.com/c/7670706/1780961/21018";
    return base + (base.indexOf("?") >= 0 ? "&" : "?") + "u=" + encodeURIComponent(dest);
  }

  function searchUrl(name) {
    return "https://www.tcgplayer.com/search/riftbound/product?q=" +
      encodeURIComponent(name) + "&productLineName=riftbound";
  }

  function drawSpark(canvas, history, color) {
    if (!canvas || !history || history.length < 2) return;
    var w = canvas.width;
    var h = canvas.height;
    var ctx = canvas.getContext("2d");
    var min = Math.min.apply(null, history);
    var max = Math.max.apply(null, history);
    var span = max - min || 1;
    ctx.clearRect(0, 0, w, h);
    ctx.beginPath();
    history.forEach(function (v, i) {
      var x = (i / (history.length - 1)) * (w - 4) + 2;
      var y = h - 4 - ((v - min) / span) * (h - 8);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = color || "#b42318";
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  function drawMain(canvas, history, labels) {
    if (!canvas) return;
    var w = canvas.width = canvas.clientWidth || 640;
    var h = canvas.height = canvas.clientHeight || 220;
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, w, h);
    var pad = { l: 44, r: 12, t: 12, b: 28 };
    var min = Math.min.apply(null, history);
    var max = Math.max.apply(null, history);
    var span = max - min || 1;
    var dark = document.documentElement.getAttribute("data-theme") === "dark";
    ctx.strokeStyle = dark ? "rgba(255,255,255,0.12)" : "rgba(0,0,0,0.08)";
    ctx.fillStyle = dark ? "#b0a59a" : "#6b6460";
    ctx.font = "11px Inter, system-ui, sans-serif";
    for (var g = 0; g < 4; g++) {
      var gy = pad.t + (h - pad.t - pad.b) * g / 3;
      ctx.beginPath();
      ctx.moveTo(pad.l, gy);
      ctx.lineTo(w - pad.r, gy);
      ctx.stroke();
      var val = max - span * g / 3;
      ctx.fillText("$" + val.toFixed(0), 6, gy + 4);
    }
    ctx.beginPath();
    history.forEach(function (v, i) {
      var x = pad.l + (i / (history.length - 1)) * (w - pad.l - pad.r);
      var y = pad.t + (1 - (v - min) / span) * (h - pad.t - pad.b);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = "#b42318";
    ctx.lineWidth = 2.4;
    ctx.stroke();
    if (labels && labels.length) {
      ctx.fillStyle = dark ? "#b0a59a" : "#6b6460";
      ctx.fillText(labels[0], pad.l, h - 8);
      ctx.fillText(labels[labels.length - 1], w - pad.r - 64, h - 8);
    }
  }

  function boot() {
    document.querySelectorAll("canvas.spark[data-history]").forEach(function (c) {
      var hist = JSON.parse(c.getAttribute("data-history") || "[]");
      var last = hist[hist.length - 1] || 0;
      var prev = hist[0] || last;
      drawSpark(c, hist, last >= prev ? "#2e7d32" : "#b42318");
    });
    var main = document.getElementById("price-main-chart");
    var select = document.getElementById("price-card");
    var meta = document.getElementById("price-meta");
    var buy = document.getElementById("price-buy");
    function render() {
      if (!select || !window.RBDB_PRICES) return;
      var card = window.RBDB_PRICES[select.value];
      if (!card) return;
      if (meta) {
        meta.innerHTML = "<strong>" + card.name + "</strong> · market $" + card.price.toFixed(2) +
          " · 60-day " + (card.change >= 0 ? "+" : "") + card.change.toFixed(1) + "%";
      }
      if (buy) {
        buy.href = affiliate(searchUrl(card.name));
        buy.rel = "noopener nofollow sponsored";
        buy.target = "_blank";
      }
      if (main) drawMain(main, card.history, card.labels);
    }
    if (select) {
      select.addEventListener("change", render);
      window.addEventListener("rbdb-theme", render);
      render();
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
