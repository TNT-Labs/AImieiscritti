(function () {
  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  if (!input || !results) return;

  var posts = [];
  var loaded = false;

  function esc(s) {
    return (s || "").replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function norm(s) {
    return (s || "").toLowerCase();
  }

  function render(q) {
    q = norm(q).trim();
    if (!loaded) {
      results.innerHTML = '<p class="muted search-hint">Caricamento…</p>';
      return;
    }
    if (!q) {
      results.innerHTML = '<p class="muted search-hint">Scrivi qualcosa per cercare tra gli articoli.</p>';
      return;
    }
    var hits = posts.filter(function (p) {
      return norm(p.title).indexOf(q) !== -1 ||
        norm(p.excerpt).indexOf(q) !== -1 ||
        norm(p.category).indexOf(q) !== -1;
    });
    if (!hits.length) {
      results.innerHTML = '<p class="muted search-hint">Nessun risultato per &ldquo;' + esc(q) + '&rdquo;.</p>';
      return;
    }
    results.innerHTML = hits.map(function (p) {
      return '<article class="card cat-' + esc(p.category) + '">' +
        '<a class="card-link" href="' + esc(p.url) + '">' +
        (p.category ? '<span class="tag ' + esc(p.category) + '">' + esc(p.category) + "</span>" : "") +
        '<h2 class="card-title">' + esc(p.title) + "</h2>" +
        '<p class="card-excerpt">' + esc(p.excerpt) + "</p>" +
        "</a></article>";
    }).join("");
  }

  fetch(input.getAttribute("data-endpoint"))
    .then(function (r) { return r.json(); })
    .then(function (data) { posts = data; loaded = true; render(input.value); })
    .catch(function () { results.innerHTML = '<p class="muted">Ricerca non disponibile al momento.</p>'; });

  input.addEventListener("input", function (e) { render(e.target.value); });
  render("");
})();
