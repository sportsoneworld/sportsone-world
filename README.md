# SportsOne

A production-ready static sports-news publishing platform.

**Markdown → VS Code → Git → GitHub → GitHub Actions → Hugo → GitHub Pages → sportsone.world**

You write an article as a plain text file. You press Publish. Two minutes later
it is live. There is no login, no admin panel, no database and no server to pay
for or keep running.

---

## New here? Read these, in this order

| # | Guide | What it covers |
|---|-------|----------------|
| 1 | [docs/01-setup-vs-code-and-github.md](docs/01-setup-vs-code-and-github.md) | Installing everything on a brand-new computer and connecting VS Code to GitHub |
| 2 | [docs/02-publishing-and-managing-articles.md](docs/02-publishing-and-managing-articles.md) | Publishing daily, editing, updating live scores, archiving and deleting old stories |
| 3 | [docs/03-tools-and-dependencies.md](docs/03-tools-and-dependencies.md) | Every tool this project uses, which versions, and how each is configured |
| 4 | [docs/04-deployment-and-domain.md](docs/04-deployment-and-domain.md) | Turning on GitHub Pages and pointing the GoDaddy domain at it |
| 5 | [docs/05-troubleshooting.md](docs/05-troubleshooting.md) | "It broke and I don't know why" — written for a non-technical reader |
| 6 | [docs/06-design-system.md](docs/06-design-system.md) | Colours, type scale, spacing and layout rules, for whoever changes the design |
| 7 | [docs/07-moving-to-a-windows-laptop.md](docs/07-moving-to-a-windows-laptop.md) | Moving the project from one computer to another, and what to install on Windows |

**Handed this as a zip file?** Start with
**[DISTRIBUTION.md](DISTRIBUTION.md)** — unzipping on Windows, running it, and
putting it online, start to finish.

---

## Quick start for a developer

```bash
git clone https://github.com/<your-username>/sportsone-world.git
cd sportsone-world
hugo server
```

Open <http://localhost:1313>. Edits appear instantly as you save.

Publish:

```bash
git add .
git commit -m "Add match report"
git push
```

GitHub Actions does the rest. Nothing else to run.

---

## Writing an article

```bash
hugo new content posts/football/riverside-win.md
```

That creates `content/posts/football/riverside-win.md` with every front-matter
field already filled in and explained. Write the story under the second `---`,
set `draft: false`, commit and push.

A minimal article looks like this:

```markdown
---
title: "Riverside edge Kingsport with a late winner"
date: 2026-08-13T19:40:00+05:30
draft: false
summary: "Ten men, ninety-four minutes and one set piece."
image: "/images/riverside-winner.jpg"
imageAlt: "Riverside players celebrating in front of the away end"
categories: ["Football", "Premier League", "Match Reports"]
author: "Devendra Nair"
---

The story goes here, in plain Markdown. No HTML required.
```

Pictures go in `static/images/`. A file saved as
`static/images/riverside-winner.jpg` is written in Markdown as
`/images/riverside-winner.jpg` — drop the word `static`.

### Choosing where a story appears

Nothing in the article decides that. You choose it in two plain-text files, by
writing the story's slug:

| File | What it controls |
|------|------------------|
| `data/homepage.yaml` | Spotlight (5), the Top Stories panel (4, rotating), the 4 stories beside it, Editor's Picks (6) |
| `data/sports.yaml` | Each sport's carousel (5) and its two fixed stories — used on the sport page *and* in that sport's front-page section |
| `data/scores.yaml` | Live scores. Refreshed automatically every 15 minutes; `featured_matches` is yours and survives every refresh |
| `data/scores-source.yaml` | Which sports the refresh fetches, and from where |
| `data/navigation.yaml` | The toolbar, the Cricket and Football dropdowns, the mobile menu and the footer link columns |
| `data/videos.yaml` | The three clips at the foot of each sport page |

A slot you leave short, or a slug you mistype, is filled with the newest unused
story — the page is never half empty and never shows a broken card. Full
explanation in [docs/02](docs/02-publishing-and-managing-articles.md).

---

## What is in this repository

```text
sportsone-world/
├── archetypes/          Template for a new article (hugo new)
├── assets/
│   ├── css/             Design system, one small file per concern
│   └── js/              ~300 lines: nav, menu, carousels, score filters, search
├── content/
│   ├── posts/           EVERY ARTICLE — organised into sport folders
│   │   ├── football/
│   │   ├── cricket/
│   │   └── ...
│   ├── categories/      One page per sport and per sport section
│   ├── about.md  contact.md  terms.md  privacy.md  accessibility.md
│   └── scores.md  search.md  privacy-options.md
├── data/                THE EDITORIAL CONTROLS — plain text, you edit these
│   ├── homepage.yaml    Spotlight, Top Stories, Editor's Picks
│   ├── sports.yaml      Each sport's carousel and fixed stories
│   ├── scores.yaml      Live scores — refreshed automatically, pins are yours
│   ├── scores-source.yaml  Which sports the refresh fetches
│   ├── videos.yaml      Three clips per sport page
│   └── navigation.yaml  Toolbar, dropdowns, mobile menu, footer links
├── scripts/
│   └── fetch-scores.py  Pulls live scores into data/scores.yaml
├── layouts/             Page templates (Hugo)
│   ├── baseof.html  home.html  page.html  section.html  term.html
│   ├── scores.html      The full live-scores board
│   ├── posts/page.html  The article page
│   ├── _partials/       Header, footer, cards, SEO, live scores
│   ├── _shortcodes/     pullquote, keypoints, scoreline, stats, figure
│   └── _markup/         How Markdown images, links and tables are rendered
├── static/
│   ├── images/          YOUR PICTURES GO HERE
│   │   ├── photos/      Article photography, all freely licensed
│   │   └── brand/       The two logo marks, one per system theme
│   ├── fonts/           Self-hosted Cambo, Inter and Archivo
│   ├── icons/           Favicons
│   └── CNAME            The custom domain: sportsone.world
├── .github/workflows/
│   ├── deploy.yml       Builds and publishes on every push
│   └── scores.yml       Refreshes the live scores every 15 minutes
├── .vscode/             One-click tasks so you never type a command
├── docs/                The guides listed above
└── hugo.toml            The only settings file you need to touch
```

---

## How the site is put together

* **Homepage** — Spotlight (five rotating stories), Top Stories (a rotating
  four-story panel with four more stacked beside it), six Editor's Picks
  alongside More Headlines, the horizontal Live Scores strip, then a carousel
  and two stories for each sport.
* **Carousels** — one implementation, used everywhere. Five stories by default,
  rotating every five seconds, no play/pause control. Each is a scroll-snapping
  row first and a slideshow second, so it still works, swipes and takes keyboard
  focus with JavaScript switched off. The frame is fixed by a design token, so a
  photograph of any dimensions is cropped into an identical box and changing a
  picture can never move the page.
* **Light and dark** — the site follows the reader's system setting, and the
  logo swaps with it: the red mark on white in light, the white mark on red in
  dark. No script, no flash of the wrong one.
* **Bylines** — on the article page only. Never on a card, a feed, a carousel or
  the front page.
* **Live scores** — refreshed every fifteen minutes by a scheduled GitHub
  Action that rewrites `data/scores.yaml` and commits it. The site stays
  completely static: readers' browsers never call an API, and there is no key in
  the page. Matches you pin under `featured_matches` survive every refresh and
  always lead the strip. If the provider is down the refresh fails and the last
  good scores stay up.
* **Image credits** — every photograph carries the photographer and licence in
  10px type. On an article it sits directly beneath the picture; on a card it
  takes the place a category label would normally occupy, because the reader
  already knows which section they are in. All of them are listed at
  `/credits/`. Add `imageCredit` to an article's front matter and the line
  appears; leave it out for your own photography and it does not.
* **Video** — three clips at the foot of each sport page, from
  `data/videos.yaml`. Only the still image loads with the page; YouTube is not
  contacted until a reader presses play. The channel name beneath each clip is
  the credit and links back to the channel.
* **Search** — Hugo writes a `/index.json` index at build time and a small
  script filters it in the browser. Nothing is sent anywhere.
* **Categories** — created automatically from article front matter. Add
  `categories: ["Hockey"]` to an article and the Hockey page, its RSS feed and
  its navigation entry all appear on the next build. No code change needed.

---

## Performance and privacy

* One CSS file and one JavaScript file, both minified and cache-busted.
* Fonts are self-hosted — the site makes **zero** third-party requests.
* No trackers, no analytics, no cookies, no consent banner needed.
* Everything is static HTML, so there is no server to attack or patch.

---

## The starter articles

The twenty-nine articles are **real**: factual pieces about real, well-documented
events — Headingley 2019, Istanbul 2005, Berlin 2009, Lake Placid 1980 and so
on. They are there to show the site working with genuine copy rather than lorem
ipsum, and to be replaced by your own reporting.

Every photograph is sourced from Wikimedia Commons under a licence that permits
reuse — public domain, CC0, CC BY or CC BY-SA — and credited beneath the picture
and on `/credits/`.

Two things to know if you keep any of them:

* Where a photograph is a **file picture** rather than the moment described, the
  caption says so ("Eden Gardens, pictured in 2011"). Keep that habit — it is
  the difference between a file photo and a misleading one.
* The bylines are placeholder names. Change them to your own before publishing.

Before you launch, delete the starter stories:

```bash
rm -rf content/posts/football content/posts/cricket content/posts/tennis \
       content/posts/basketball content/posts/motorsport content/posts/athletics \
       content/posts/other-sports
mkdir -p content/posts/football
```

…and `rm -rf static/images/photos` if you are not keeping the pictures.

Then empty the story lists in `data/homepage.yaml` and `data/sports.yaml` — with
no slugs in them every slot fills itself with your newest stories, so the site
works from your very first article and you can start choosing placements once
you have a few. `static/images/placeholder.svg` is the fallback that appears
when an article has no picture of its own; keep it.

---

## The distributable build

`public/` is the finished website: 251 pages of plain HTML with one CSS file,
one JavaScript file, the fonts, the icons and the photography. Nothing else is
needed to serve it — no Hugo, no Node, no server-side anything. Upload the
contents of `public/` to any web root.

It is rebuilt from source with:

```bash
HUGO_ENVIRONMENT=production hugo --minify --gc --cleanDestinationDir
```

To look at it locally before uploading, serve it — do not open the files
directly, because the links are root-absolute and `file://` cannot resolve them:

```bash
cd public && python3 -m http.server 8080     # then open http://localhost:8080
```

`public/` is in `.gitignore` on purpose: GitHub Actions builds it on every push,
so the copy in the repository would only ever go stale. It is here as the
ready-to-distribute artefact.

**One rule, learned the hard way:** never delete `public/` while `hugo server`
is running. The server keeps serving from what it thinks is there, the
stylesheet 404s, and every page renders as unstyled HTML. Stop the server first.

---

## Licences

* Site code and templates: yours.
* Fonts in `static/fonts/` — Inter, Archivo and Cambo, all SIL Open Font
  License 1.1, self-hosted with attribution retained upstream.
* Logo files in `static/images/brand/` and `static/icons/` — supplied by you.
* Photographs in `static/images/photos/` — sourced from Wikimedia Commons under
  public-domain, CC0, CC BY and CC BY-SA licences. Each one is credited on the
  story it appears on and listed at `/credits/`.
