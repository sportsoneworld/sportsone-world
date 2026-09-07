/* ==========================================================================
   SportsOne — on-site search
   Downloads the index Hugo generates at /index.json and filters it in the
   browser. No search service, no API key, nothing to pay for.
   ========================================================================== */
(function () {
  'use strict';

  var input   = document.querySelector('[data-search-input]');
  var list    = document.querySelector('[data-search-results]');
  var statusEl= document.querySelector('[data-search-status]');
  var form    = document.querySelector('[data-search-form]');
  if (!input || !list) return;

  var index = null;
  var loading = false;

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function highlight(text, terms) {
    var out = esc(text);
    terms.forEach(function (t) {
      if (t.length < 2) return;
      out = out.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>');
    });
    return out;
  }

  function score(item, terms) {
    var title = item.title.toLowerCase();
    var cats  = (item.categories || []).join(' ').toLowerCase();
    var tags  = (item.tags || []).join(' ').toLowerCase();
    var sum   = (item.summary || '').toLowerCase();
    var body  = (item.body || '').toLowerCase();
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i];
      var hit = 0;
      if (title.indexOf(t) > -1) hit += 12;
      if (cats.indexOf(t) > -1)  hit += 6;
      if (tags.indexOf(t) > -1)  hit += 5;
      if (sum.indexOf(t) > -1)   hit += 3;
      if (body.indexOf(t) > -1)  hit += 1;
      if (hit === 0) return 0;          // every word must appear somewhere
      total += hit;
    }
    return total;
  }

  function render(query) {
    var terms = query.toLowerCase().split(/\s+/).filter(function (t) { return t.length > 1; });
    list.innerHTML = '';

    if (!terms.length) {
      statusEl.textContent = 'Type at least two characters to search.';
      return;
    }
    if (!index) {
      statusEl.textContent = 'Loading articles…';
      return;
    }

    var results = index.items
      .map(function (item) { return { item: item, s: score(item, terms) }; })
      .filter(function (r) { return r.s > 0; })
      .sort(function (a, b) { return b.s - a.s || b.item.ts - a.item.ts; })
      .slice(0, 40);

    if (!results.length) {
      statusEl.textContent = 'No articles found for “' + query + '”.';
      return;
    }

    statusEl.textContent = results.length + (results.length === 1 ? ' article' : ' articles') +
      ' found for “' + query + '”.';

    var html = results.map(function (r) {
      var it = r.item;
      return '<li>' +
        (it.category ? '<span class="kicker">' + esc(it.category) + '</span>' : '') +
        '<h2 class="search-results__title"><a href="' + esc(it.url) + '">' +
          highlight(it.title, terms) + '</a></h2>' +
        '<p>' + highlight(it.summary || '', terms) + '</p>' +
        '<p class="t-meta">' + esc(it.author) + ' · ' + esc(it.date) + '</p>' +
      '</li>';
    }).join('');
    list.innerHTML = html;
  }

  function load(then) {
    if (index || loading) { then && then(); return; }
    loading = true;
    fetch('/index.json', { credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; loading = false; then && then(); })
      .catch(function () {
        loading = false;
        statusEl.textContent = 'Search is temporarily unavailable. Please browse the sections instead.';
      });
  }

  var debounce = null;
  input.addEventListener('input', function () {
    window.clearTimeout(debounce);
    var q = input.value;
    debounce = window.setTimeout(function () { load(function () { render(q); }); }, 120);
  });

  if (form) form.addEventListener('submit', function (e) { e.preventDefault(); });

  // Support /search/?q=messi coming from the header or an external link
  var params = new URLSearchParams(window.location.search);
  var initial = params.get('q');
  if (initial) {
    input.value = initial;
    load(function () { render(initial); });
  }
  input.focus();
})();
