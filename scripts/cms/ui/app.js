/* ===========================================================================
   THE PUBLISHING TOOL

   Three things happen in this file:

     1. The form on the left is kept in one plain object called `story`.
     2. Whenever that object changes, the story is saved into the project as
        a draft, Hugo rebuilds the site, and the frame on the right reloads.
        That is the whole trick behind the preview: there is no second
        renderer to keep in step, because the preview IS the website.
     3. Publish sends the same object to the server, which checks it, places
        it, and hands it to git.

   No framework, no build step, no packages. It is one file so that anyone
   who has to fix it in five years can read it top to bottom.
   =========================================================================== */

'use strict';

const $ = (id) => document.getElementById(id);
const api = async (path, body) => {
  const options = body
    ? { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body) }
    : {};
  const response = await fetch(path, options);
  return response.json();
};

/* What the journalist has typed. The single source of truth for the form. */
let story = {
  original_slug: '', slug: '', title: '', summary: '', body: '',
  image: '', imageAlt: '', imageCaption: '', imageSource: '', imageCredit: '',
  sport: '', sections: [], tags: [], author: '', date: '',
  draft: true, placements: [], extraImages: []
};

let site = { sports: [], sections: [], slots: [], articles: [], git: {} };
let saveTimer = null;
let previewTab = 'article';
let lastSavedSlug = '';

/* ─────────────────────────── start up ─────────────────────────── */

async function boot() {
  site = await api('/api/bootstrap');

  const sport = $('f-sport');
  sport.innerHTML = site.sports
    .map((s) => `<option value="${esc(s.name)}">${esc(s.name)}</option>`)
    .join('');
  story.sport = site.sports[0] ? site.sports[0].name : '';

  $('f-date').value = site.today;
  story.date = site.today;
  $('f-author').value = 'SportsOne Desk';
  story.author = 'SportsOne Desk';

  drawSections();
  drawGitState();
  drawPreviewTabs();
  wire();
}

function drawGitState() {
  const pill = $('gitState');
  if (site.git && site.git.ready) {
    pill.className = 'pill pill--ok';
    pill.textContent = 'connected to GitHub';
    pill.title = site.git.remote || '';
  } else {
    pill.className = 'pill pill--no';
    pill.textContent = 'publishing not set up';
    pill.title = (site.git && site.git.reason) || '';
  }
}

function drawSections() {
  $('sectionChips').innerHTML = site.sections
    .map((s) => `<button type="button" class="chip" data-section="${esc(s)}">${esc(s)}</button>`)
    .join('');
}

/* ─────────────────────────── the form ─────────────────────────── */

function wire() {
  bind('f-title', 'title');
  bind('f-summary', 'summary');
  bind('f-body', 'body');
  bind('f-imageAlt', 'imageAlt');
  bind('f-imageCaption', 'imageCaption');
  bind('f-imageSource', 'imageSource');
  bind('f-author', 'author');
  bind('f-slug', 'slug');
  bind('f-date', 'date');

  $('f-sport').addEventListener('change', (e) => {
    story.sport = e.target.value;
    drawPreviewTabs();
    queueSave();
  });

  $('f-tags').addEventListener('input', (e) => {
    story.tags = e.target.value.split(',').map((t) => t.trim()).filter(Boolean);
    queueSave();
  });

  $('sectionChips').addEventListener('click', (e) => {
    const chip = e.target.closest('[data-section]');
    if (!chip) return;
    const name = chip.dataset.section;
    const at = story.sections.indexOf(name);
    if (at >= 0) story.sections.splice(at, 1); else story.sections.push(name);
    chip.classList.toggle('is-on', at < 0);
    queueSave();
  });

  document.querySelectorAll('.tools [data-md]').forEach((button) => {
    button.addEventListener('click', () => insertMarkdown(button.dataset.md));
  });

  $('f-photo').addEventListener('change', (e) => uploadPhoto(e.target.files[0]));
  $('f-txt').addEventListener('change', (e) => loadTextFile(e.target.files[0]));
  $('photoClear').addEventListener('click', () => {
    story.image = ''; story.imageCaption = ''; story.imageSource = '';
    $('photoHas').hidden = true; $('photoEmpty').hidden = false;
    $('f-imageCaption').value = ''; $('f-imageSource').value = '';
    queueSave();
  });

  $('addPlace').addEventListener('click', addPlacement);
  $('saveDraft').addEventListener('click', () => saveNow(true));
  $('goPublish').addEventListener('click', openConfirm);
  $('confirmBack').addEventListener('click', () => { $('confirm').hidden = true; });
  $('confirmGo').addEventListener('click', doPublish);

  $('refresh').addEventListener('click', () => showPreview(true));
  $('widthPick').addEventListener('change', (e) => {
    const value = e.target.value;
    $('preview').style.maxWidth = value === 'full' ? '' : value + 'px';
  });

  document.querySelectorAll('.bar__nav .tab').forEach((tab) => {
    tab.addEventListener('click', () => switchView(tab.dataset.view));
  });

  $('storySearch').addEventListener('input', drawStories);
  $('saveScores').addEventListener('click', saveScores);
}

function bind(id, key) {
  const el = $(id);
  el.addEventListener('input', () => {
    story[key] = el.value;
    if (key === 'summary') countSummary();
    if (key === 'body') countWords();
    queueSave();
  });
}

function countSummary() {
  const n = story.summary.length;
  const el = $('sumCount');
  el.textContent = n ? `${n} characters` : '';
  el.classList.toggle('is-over', n > 300);
}

function countWords() {
  const n = story.body.trim() ? story.body.trim().split(/\s+/).length : 0;
  $('wordCount').textContent = n ? `${n} words` : '';
}

function insertMarkdown(mark) {
  const box = $('f-body');
  const start = box.selectionStart;
  const end = box.selectionEnd;
  const chosen = box.value.slice(start, end);

  let replacement;
  if (mark === '**') {
    replacement = `**${chosen || 'important'}**`;
  } else {
    const atLineStart = start === 0 || box.value[start - 1] === '\n';
    replacement = (atLineStart ? '' : '\n') + mark + (chosen || '');
  }
  box.setRangeText(replacement, start, end, 'end');
  box.focus();
  story.body = box.value;
  countWords();
  queueSave();
}

/* ─────────────────────────── files in ─────────────────────────── */

function readAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function uploadPhoto(file) {
  if (!file) return;
  const slugBase = story.slug || slugify(story.title) || 'photo';
  say('filing the photograph…');
  const picture = await readAsDataURL(file);
  const result = await api('/api/upload', {
    slug: slugBase, name: file.name, data: picture
  });
  if (!result.ok) { say(result.message, true); return; }

  story.image = result.path;
  // Show the picture the browser already has in hand rather than asking the
  // preview server for the copy just written. Hugo takes a moment to notice a
  // new file in static/, and in that moment the thumbnail would come back
  // empty and stay empty.
  $('photoThumb').src = picture;
  $('photoNote').textContent = result.warning
    ? result.warning
    : result.note;
  $('photoEmpty').hidden = true;
  $('photoHas').hidden = false;
  say('');
  queueSave();
}

async function loadTextFile(file) {
  if (!file) return;
  const result = await api('/api/read-text', {
    name: file.name, data: await readAsDataURL(file)
  });
  if (!result.ok) { say(result.message, true); return; }

  if (result.title) { story.title = result.title; $('f-title').value = result.title; }
  if (result.summary) { story.summary = result.summary; $('f-summary').value = result.summary; }
  if (result.body) { story.body = result.body; $('f-body').value = result.body; }
  if (result.author) { story.author = result.author; $('f-author').value = result.author; }
  if (result.imageAlt) { story.imageAlt = result.imageAlt; $('f-imageAlt').value = result.imageAlt; }
  if (result.imageCaption) { story.imageCaption = result.imageCaption; $('f-imageCaption').value = result.imageCaption; }
  if (result.imageSource) { story.imageSource = result.imageSource; $('f-imageSource').value = result.imageSource; }
  if (result.tags && result.tags.length) {
    story.tags = result.tags; $('f-tags').value = result.tags.join(', ');
  }
  if (result.sport) {
    const match = site.sports.find(
      (s) => s.name.toLowerCase() === result.sport.toLowerCase());
    if (match) { story.sport = match.name; $('f-sport').value = match.name; }
  }
  if (result.sections && result.sections.length) {
    story.sections = result.sections.slice();
    document.querySelectorAll('[data-section]').forEach((chip) => {
      chip.classList.toggle('is-on', story.sections.includes(chip.dataset.section));
    });
  }
  countSummary(); countWords();
  say('loaded from ' + file.name);
  queueSave();
}

/* ─────────────────────────── placement ─────────────────────────── */

function addPlacement() {
  const taken = story.placements.map((p) => p.slot);
  const free = site.slots.find((s) => !taken.includes(s.id));
  if (!free) { say('Every place on the site is already chosen.'); return; }
  story.placements.push({ slot: free.id, position: 1 });
  drawPlacements();
  drawPreviewTabs();
  queueSave();
}

function drawPlacements() {
  const host = $('placements');
  host.innerHTML = '';

  story.placements.forEach((choice, index) => {
    const slot = site.slots.find((s) => s.id === choice.slot);
    if (!slot) return;

    const groups = {};
    site.slots.forEach((s) => {
      (groups[s.group] = groups[s.group] || []).push(s);
    });
    const options = Object.keys(groups).map((group) => {
      const inner = groups[group].map((s) =>
        `<option value="${s.id}"${s.id === choice.slot ? ' selected' : ''}>${esc(s.name)}</option>`
      ).join('');
      return `<optgroup label="${esc(group)}">${inner}</optgroup>`;
    }).join('');

    const positions = [];
    for (let n = 1; n <= slot.holds; n++) {
      positions.push(
        `<option value="${n}"${n === Number(choice.position) ? ' selected' : ''}>Position ${n}</option>`);
    }

    const row = document.createElement('div');
    row.className = 'place';
    row.innerHTML = `
      <div class="place__top">
        <select class="input" data-role="slot" data-i="${index}">${options}</select>
        <select class="input" data-role="pos" data-i="${index}" style="flex:0 0 128px">${positions.join('')}</select>
        <button type="button" class="place__drop" data-role="drop" data-i="${index}" title="Remove">&times;</button>
      </div>
      <p class="place__where">${esc(slot.where)}. Holds ${slot.holds}.</p>
      ${runningOrder(slot, Number(choice.position))}
    `;
    host.appendChild(row);
  });

  host.querySelectorAll('[data-role="slot"]').forEach((select) => {
    select.addEventListener('change', (e) => {
      const i = Number(e.target.dataset.i);
      story.placements[i].slot = e.target.value;
      story.placements[i].position = 1;
      drawPlacements(); drawPreviewTabs(); queueSave();
    });
  });
  host.querySelectorAll('[data-role="pos"]').forEach((select) => {
    select.addEventListener('change', (e) => {
      const i = Number(e.target.dataset.i);
      story.placements[i].position = Number(e.target.value);
      drawPlacements(); queueSave();
    });
  });
  host.querySelectorAll('[data-role="drop"]').forEach((button) => {
    button.addEventListener('click', (e) => {
      story.placements.splice(Number(e.target.dataset.i), 1);
      drawPlacements(); drawPreviewTabs(); queueSave();
    });
  });
}

/* Show the slot as it will read once this story is in it: the desk's
   existing running order, with the new story slid into the chosen position
   and anything pushed past the end of the slot struck through. */
function runningOrder(slot, position) {
  const mine = lastSavedSlug || slugify(story.title) || 'this-story';
  const others = slot.current.filter((item) => item.slug !== mine);
  const list = others.slice();
  list.splice(Math.max(0, position - 1), 0, {
    slug: mine, title: story.title || 'Your new story', mine: true
  });

  const rows = list.map((item, i) => {
    const out = i >= slot.holds;
    const classes = ['order__row'];
    if (item.mine) classes.push('is-mine');
    if (out) classes.push('is-out');
    return `<div class="${classes.join(' ')}">
      <span class="order__n">${i + 1}</span>
      <span>${esc(trim(item.title, 62))}</span>
    </div>`;
  }).join('');

  const pushed = list.slice(slot.holds);
  const note = pushed.length
    ? `<p class="order__note">This pushes ${esc(trim(pushed[0].title, 44))} out of the slot. It stays on the site — it just stops appearing here.</p>`
    : '';

  return `<div class="order">
    <p class="order__title">How this slot will read</p>${rows}${note}</div>`;
}

/* ─────────────────────────── saving ─────────────────────────── */

function queueSave() {
  clearTimeout(saveTimer);
  if (!story.title || story.title.trim().length < 3) return;
  say('saving…');
  saveTimer = setTimeout(() => saveNow(false), 900);
}

async function saveNow(loud) {
  clearTimeout(saveTimer);
  if (!story.title || story.title.trim().length < 3) {
    if (loud) say('Give the story a headline first.', true);
    return null;
  }

  const payload = Object.assign({}, story, { draft: true });
  const result = await api('/api/save', payload);

  if (!result.ok) {
    showProblems(result.problems || []);
    say('not saved — see above', true);
    return null;
  }

  lastSavedSlug = result.slug;
  story.original_slug = result.slug;
  if (!story.slug) $('f-slug').placeholder = result.slug;

  showProblems(result.problems || []);
  say(loud ? 'Draft saved.' : 'saved');

  site.slots = (await api('/api/slots')).slots;
  drawPlacements();
  drawPreviewTabs();
  showPreview(true);
  return result;
}

function showProblems(list) {
  const host = $('problems');
  if (!list.length) { host.hidden = true; host.innerHTML = ''; return; }
  host.hidden = false;
  host.innerHTML = list.map((p) => `
    <div class="prob prob--${p.level}">
      <span class="prob__mark">${p.level === 'stop' ? '✕' : '!'}</span>
      <span>${esc(p.message)}</span>
    </div>`).join('');
}

function say(text, bad) {
  const el = $('saveState');
  el.textContent = text || '';
  el.style.color = bad ? 'var(--red)' : 'var(--muted)';
}

/* ─────────────────────────── the preview ─────────────────────────── */

function drawPreviewTabs() {
  const tabs = [{ id: 'article', label: 'The story' },
                { id: 'home', label: 'Front page' }];

  const sport = site.sports.find((s) => s.name === story.sport);
  if (sport) tabs.push({ id: 'sport:' + sport.key, label: sport.name + ' page' });

  story.placements.forEach((choice) => {
    const slot = site.slots.find((s) => s.id === choice.slot);
    if (!slot) return;
    if (slot.file === 'homepage' && !tabs.some((t) => t.id === 'home')) {
      tabs.push({ id: 'home', label: 'Front page' });
    }
    if (slot.file === 'sports') {
      const key = slot.keys[0];
      if (!tabs.some((t) => t.id === 'sport:' + key)) {
        const found = site.sports.find((s) => s.key === key);
        tabs.push({ id: 'sport:' + key, label: (found ? found.name : key) + ' page' });
      }
    }
  });

  $('previewTabs').innerHTML = tabs.map((t) =>
    `<button class="vtab${t.id === previewTab ? ' is-on' : ''}" data-tab="${t.id}">${esc(t.label)}</button>`
  ).join('');

  $('previewTabs').querySelectorAll('.vtab').forEach((tab) => {
    tab.addEventListener('click', () => {
      previewTab = tab.dataset.tab;
      drawPreviewTabs();
      showPreview(true);
    });
  });
}

function previewURL() {
  const slug = lastSavedSlug;
  if (!slug) return null;
  const cache = 'cms=' + Date.now();

  if (previewTab === 'article') return `/site/posts/${slug}/?${cache}`;
  if (previewTab === 'home') return `/site/?highlight=${slug}&${cache}`;
  if (previewTab.startsWith('sport:')) {
    return `/site/categories/${previewTab.slice(6)}/?highlight=${slug}&${cache}`;
  }
  return `/site/?${cache}`;
}

let previewTimer = null;
function showPreview(soon) {
  const url = previewURL();
  if (!url) return;
  $('stageEmpty').hidden = true;
  clearTimeout(previewTimer);
  // Hugo needs a moment to notice the file changed and rebuild.
  previewTimer = setTimeout(() => { $('preview').src = url; }, soon ? 550 : 0);
}

/* ─────────────────────────── publishing ─────────────────────────── */

async function openConfirm() {
  const saved = await saveNow(true);
  if (!saved) return;

  const check = await api('/api/check',
    Object.assign({}, story, { draft: false, for_publish: true }));
  const problems = check.problems || [];
  const blocked = problems.some((p) => p.level === 'stop');

  const places = story.placements.length
    ? story.placements.map((choice) => {
        const slot = site.slots.find((s) => s.id === choice.slot);
        return `${esc(slot ? slot.group + ' → ' + slot.name : choice.slot)} <em>· position ${choice.position}</em>`;
      }).join('<br>')
    : '<em>Latest News and its sport page only</em>';

  $('confirmFacts').innerHTML = `
    <div><dt>Headline</dt><dd>${esc(story.title)}</dd></div>
    <div><dt>Sub-headline</dt><dd>${story.summary ? esc(trim(story.summary, 130)) : '<em>none</em>'}</dd></div>
    <div><dt>Sport</dt><dd>${esc(story.sport)}${story.sections.length ? ' · ' + esc(story.sections.join(', ')) : ''}</dd></div>
    <div><dt>Placement</dt><dd>${places}</dd></div>
    <div><dt>Photograph</dt><dd>${story.image
      ? `<img src="/site${story.image}" alt="" style="width:120px;height:74px;object-fit:cover;border-radius:2px">`
      : '<em>none — the site placeholder will be used</em>'}</dd></div>
    <div><dt>Web address</dt><dd>/posts/${esc(lastSavedSlug)}/</dd></div>
  `;

  const host = $('confirmProblems');
  if (problems.length) {
    host.hidden = false;
    host.innerHTML = problems.map((p) => `
      <div class="prob prob--${p.level}">
        <span class="prob__mark">${p.level === 'stop' ? '✕' : '!'}</span>
        <span>${esc(p.message)}</span>
      </div>`).join('');
  } else {
    host.hidden = true;
  }

  $('confirmGo').disabled = blocked;
  $('confirmGo').textContent = blocked
    ? 'Fix the problems above first'
    : 'Publish to SportsOne';
  $('publishLog').hidden = true;
  $('confirm').hidden = false;
}

async function doPublish() {
  const button = $('confirmGo');
  button.disabled = true;
  button.textContent = 'Publishing…';

  const log = $('publishLog');
  log.hidden = false;
  log.className = 'publog';
  log.textContent = 'Saving the story, placing it, and sending it to GitHub…';

  const result = await api('/api/publish', Object.assign({}, story));

  if (result.ok && result.stage === 'done') {
    log.className = 'publog is-ok';
    log.innerHTML = `<strong>Published.</strong><br>${esc(result.message)}<br><br>
      It will appear at
      <a href="https://sportsone.world/posts/${esc(result.slug)}/" target="_blank"
         rel="noopener">sportsone.world/posts/${esc(result.slug)}/</a>`;
    button.textContent = 'Published';
    story.draft = false;
    refreshStories();
  } else if (result.ok) {
    log.className = 'publog';
    log.textContent = result.message || 'Nothing needed publishing.';
    button.disabled = false;
    button.textContent = 'Publish to SportsOne';
  } else {
    log.className = 'publog is-bad';
    let html = `<strong>Not published.</strong><br>${esc(result.message || 'Something went wrong.')}`;
    if (result.fix) html += `<br><br>${esc(result.fix)}`;
    if (result.problems && result.problems.length) {
      html += '<br><br>' + result.problems
        .filter((p) => p.level === 'stop')
        .map((p) => '• ' + esc(p.message)).join('<br>');
    }
    if (result.detail) html += `<code>${esc(result.detail)}</code>`;
    log.innerHTML = html;
    button.disabled = false;
    button.textContent = 'Try again';
  }
}

/* ─────────────────────────── the other two views ─────────────────────────── */

function switchView(name) {
  document.querySelectorAll('.bar__nav .tab').forEach((tab) => {
    tab.classList.toggle('is-on', tab.dataset.view === name);
  });
  $('view-write').hidden = name !== 'write';
  $('view-stories').hidden = name !== 'stories';
  $('view-scores').hidden = name !== 'scores';
  if (name === 'stories') refreshStories();
  if (name === 'scores') drawScores();
}

async function refreshStories() {
  site.articles = (await api('/api/articles')).articles;
  drawStories();
}

function drawStories() {
  const term = ($('storySearch').value || '').toLowerCase();
  const list = site.articles.filter(
    (a) => !term || a.title.toLowerCase().includes(term));

  $('storyList').innerHTML = list.map((a) => {
    const places = a.placements.map(
      (p) => `<span class="badge badge--place">${esc(p.name)} #${p.position}</span>`).join(' ');
    return `<article class="story">
      <img class="story__pic" src="${a.image ? '/site' + esc(a.image) : ''}" alt="">
      <div>
        <p class="story__title">${esc(a.title)}</p>
        <div class="story__meta">
          <span>${esc(a.sport)}</span>
          <span>${esc((a.date || '').slice(0, 10))}</span>
          ${a.draft ? '<span class="badge badge--draft">Draft</span>' : ''}
          ${places}
        </div>
      </div>
      <div class="story__do">
        <button class="btn btn--quiet" data-edit="${esc(a.slug)}">Edit</button>
        <button class="btn btn--quiet btn--danger" data-remove="${esc(a.slug)}">Remove</button>
      </div>
    </article>`;
  }).join('') || '<p class="listing__note">No stories yet.</p>';

  $('storyList').querySelectorAll('[data-edit]').forEach((button) => {
    button.addEventListener('click', () => editStory(button.dataset.edit));
  });

  // Removing takes two clicks rather than a pop-up box. The second click has
  // to be a deliberate one, and the button says exactly what it is about to
  // do while it waits for it.
  $('storyList').querySelectorAll('[data-remove]').forEach((button) => {
    button.addEventListener('click', async () => {
      if (button.dataset.armed !== 'yes') {
        button.dataset.armed = 'yes';
        button.textContent = 'Really remove?';
        button.classList.add('is-armed');
        setTimeout(() => {
          if (!button.isConnected || button.dataset.armed !== 'yes') return;
          button.dataset.armed = '';
          button.textContent = 'Remove';
          button.classList.remove('is-armed');
        }, 4000);
        return;
      }
      button.disabled = true;
      button.textContent = 'Removing…';
      await api('/api/delete', { slug: button.dataset.remove });
      site.slots = (await api('/api/slots')).slots;
      refreshStories();
    });
  });
}

async function editStory(slug) {
  const a = await api('/api/article/' + encodeURIComponent(slug));
  if (a.error) return;

  story = {
    original_slug: a.slug, slug: a.slug, title: a.title, summary: a.summary,
    body: a.body, image: a.image, imageAlt: a.imageAlt,
    imageCaption: a.imageCaption, imageSource: a.imageSource,
    imageCredit: a.imageCredit, sport: a.sport, sections: a.sections || [],
    tags: a.tags || [], author: a.author, date: (a.date || '').slice(0, 16),
    draft: a.draft, extraImages: [],
    placements: (a.placements || []).map(
      (p) => ({ slot: p.slot, position: p.position }))
  };
  lastSavedSlug = a.slug;

  $('f-title').value = a.title;
  $('f-summary').value = a.summary;
  $('f-body').value = a.body;
  $('f-imageAlt').value = a.imageAlt;
  $('f-imageCaption').value = a.imageCaption;
  $('f-imageSource').value = a.imageSource;
  $('f-author').value = a.author;
  $('f-slug').value = a.slug;
  $('f-date').value = story.date;
  $('f-sport').value = a.sport;
  $('f-tags').value = (a.tags || []).join(', ');

  document.querySelectorAll('[data-section]').forEach((chip) => {
    chip.classList.toggle('is-on', story.sections.includes(chip.dataset.section));
  });

  if (a.image) {
    $('photoThumb').src = '/site' + a.image;
    $('photoNote').textContent = 'Already on the site.';
    $('photoEmpty').hidden = true;
    $('photoHas').hidden = false;
  } else {
    $('photoEmpty').hidden = false;
    $('photoHas').hidden = true;
  }

  countSummary(); countWords();
  drawPlacements(); drawPreviewTabs();
  switchView('write');
  showPreview(false);
  say('Editing "' + trim(a.title, 40) + '"');
}

async function drawScores() {
  const data = await api('/api/scores');
  $('scoreList').innerHTML = data.sports.map((sport) => `
    <section class="sportgroup">
      <h3 class="sportgroup__name">${esc(sport.name)}</h3>
      ${sport.matches.map((m) => `
        <label class="match${m.featured ? ' is-on' : ''}">
          <input type="checkbox" data-match="${esc(m.id)}"${m.featured ? ' checked' : ''}>
          <span class="match__teams">
            ${m.teams.map((t) => esc(t.name) + ' ' + esc(t.score)).join(' &nbsp;v&nbsp; ')}
            <span class="match__comp">${esc(m.competition)}</span>
          </span>
          ${m.state === 'live' ? `<span class="match__state">${esc(m.stateLabel || 'Live')}</span>` : ''}
        </label>`).join('')}
    </section>`).join('') || '<p class="listing__note">No matches in the feed right now.</p>';

  $('scoreList').querySelectorAll('[data-match]').forEach((box) => {
    box.addEventListener('change', () => {
      box.closest('.match').classList.toggle('is-on', box.checked);
    });
  });
}

async function saveScores() {
  const ids = [...$('scoreList').querySelectorAll('[data-match]:checked')]
    .map((box) => box.dataset.match);
  const result = await api('/api/scores', { featured: ids });
  $('scoreState').textContent = result.message || 'Saved.';
}

/* ─────────────────────────── odds and ends ─────────────────────────── */

function esc(text) {
  return String(text == null ? '' : text).replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function trim(text, n) {
  text = String(text || '');
  return text.length > n ? text.slice(0, n - 1) + '…' : text;
}

/* Mirrors slugify() in scripts/import-articles.py closely enough to show the
   journalist what the address will be. The server always has the last word. */
function slugify(text) {
  const words = String(text || '').toLowerCase()
    .normalize('NFKD').replace(/[̀-ͯ]/g, '')
    .split(/[^a-z0-9]+/).filter(Boolean);
  const out = [];
  for (const word of words) {
    if (out.length && out.join('-').length + word.length + 1 > 50 && out.length >= 3) break;
    out.push(word);
  }
  return out.join('-');
}

boot();
