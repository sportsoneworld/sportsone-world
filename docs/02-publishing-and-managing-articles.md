# 2 · Publishing and managing articles

This is the guide you will actually use every day. Everything else is set-up.

---

## The five-minute version

1. **Terminal ▸ Run Task… ▸ 2 · New article** — pick the sport, type a file name.
2. Write the story.
3. Change `draft: true` to `draft: false`.
4. **Terminal ▸ Run Task… ▸ 3 · Publish everything**, type what you changed.
5. Wait two minutes. It is live.

That is it. The rest of this document explains each part properly.

---

## Publishing a new article, step by step

### Step 1 — Create the file

**Terminal ▸ Run Task… ▸ 2 · New article**

VS Code asks two questions:

* **Which sport folder?** — pick from the list. This only decides where the file
  is filed on disk. It does **not** decide the web address or which section the
  story appears in.
* **File name** — lower case, words joined by hyphens, no spaces, no capitals,
  no apostrophes. For example `riverside-edge-kingsport`.

The file opens automatically with all the front matter ready.

*Prefer typing?*

```bash
hugo new content posts/football/riverside-edge-kingsport.md
```

### Step 2 — Fill in the top part (the "front matter")

Everything between the first `---` and the second `---` is settings, not
article text. Full field-by-field reference is further down this page.

At minimum you must set: `title`, `summary`, `categories` and `draft: false`.

### Step 3 — Add the picture

1. Copy your image file into the `static/images/` folder. You can drag it there
   from Finder or File Explorer straight into VS Code's file list.
2. Name it in lower case with hyphens: `riverside-winner.jpg` — **not**
   `IMG_2231 copy (2).JPG`.
3. In the front matter, write the path **without the word `static`**:

   ```yaml
   image: "/images/riverside-winner.jpg"
   imageAlt: "Riverside players celebrating in front of the away end"
   ```

**Recommended picture sizes**

| Use | Size | Weight |
|-----|------|--------|
| Hero / main article picture | 1600 × 900 pixels | under 300 KB |
| Pictures inside the article | 1200 × 675 pixels | under 200 KB |

The site crops every picture into a fixed frame, so an odd-sized photo will
never break the layout — but a 6 MB photo straight off a camera will make the
page slow. Shrink it first at <https://squoosh.app> (free, runs in your browser,
nothing is uploaded).

`imageAlt` is the description read aloud to blind readers and shown if the
picture fails to load. Always fill it in. Describe what is happening, not
"photo".

### Step 4 — Write the story

Below the second `---`, in plain Markdown:

```markdown
The opening paragraph. Just type. Leave a blank line between paragraphs.

## A section heading

Another paragraph, with a **bold phrase**, an *italic one* and a
[link to somewhere](https://example.com).

- A bullet point
- Another one

1. A numbered point
2. Another one

> A quote from a player or manager.

![Describe the picture](/images/second-photo.jpg "Caption printed underneath")
```

That is the whole language. There is no HTML anywhere.

### Step 5 — Check it before publishing

If the preview is not already running: **Terminal ▸ Run Task… ▸ 1 · Preview the
website**, then open <http://localhost:1313>.

While you have `draft: true` the article is visible in the preview but will
**not** be published. That is the point of drafts.

### Step 6 — Publish

1. Change `draft: true` to `draft: false`.
2. **Terminal ▸ Run Task… ▸ 3 · Publish everything**
3. Type a short note — "Add match report: Riverside v Kingsport" — and press
   Enter.

Now go to your repository on GitHub and click the **Actions** tab. You will see
your note with a spinning yellow dot. When it turns into a green tick, the
article is live. It usually takes 90 seconds to 2 minutes.

---

## Every front-matter field, explained

```yaml
---
title: "Riverside edge Kingsport with a 94th-minute winner"
slug: "riverside-edge-kingsport"
date: 2026-08-13T19:40:00+05:30
lastmod: 2026-08-13T21:05:00+05:30
draft: false
summary: "Ten men, ninety-four minutes and one set piece."
description: ""
image: "/images/photos/riverside-winner.jpg"
imageAlt: "Riverside players celebrating in front of the away end"
imageCaption: "The winner arrived from the sixth corner of the half."
imageCredit: "A. Photographer"
imageCreditURL: "https://example.org/where-it-came-from"
imageLicense: "CC BY 2.0"
imageLicenseURL: "https://creativecommons.org/licenses/by/2.0/"
thumbnail: ""
categories: ["Football", "Match Reports"]
tags: ["Riverside Athletic", "Kingsport FC"]
author: "Devendra Nair"
authorRole: "Football correspondent"
featured: true
toc: true
---
```

| Field | Required | What it does |
|-------|:--------:|--------------|
| `title` | ✅ | The headline. Keep it under about 90 characters so it does not wrap awkwardly in the hero. |
| `slug` | — | The web address. `slug: "riverside-edge-kingsport"` gives `/posts/riverside-edge-kingsport/`. Without it the address is made from the title, which can get long. **Never change a slug after publishing** — old links break. |
| `date` | ✅ | Publication date and time. `+05:30` is India. A date in the future keeps the article hidden until a build runs after that time — see "Scheduling" below. |
| `lastmod` | — | When you last meaningfully changed the story. Kept for search engines and the sitemap; readers are never shown an "Updated …" line. |
| `draft` | ✅ | `true` = never published. `false` = goes live. |
| `summary` | ✅ | One or two sentences. Used on every card, in Spotlight and, if `description` is blank, in Google results. |
| `description` | — | Only needed when you want the Google description to differ from `summary`. |
| `image` | — | The main picture. If left blank the story falls back to the SportsOne placeholder. |
| `imageAlt` | ✅ if there is an image | Description for screen readers. |
| `imageCaption` | — | Printed under the picture, in small type with a red rule. |
| `imageCredit` | ✅ for any picture you did not take | Who took it. Printed directly under the photograph in the smallest type on the site, and listed on `/credits/`. Leave it out for your own photography and no line appears. |
| `imageCreditURL` | — | Where the picture came from — the file page, the photographer's site. Makes the credit a link. |
| `imageLicense` | ✅ with `imageCredit` | "Public domain", "CC BY 2.0", "CC BY-SA 4.0" and so on. |
| `imageLicenseURL` | — | The licence deed. Required in practice for any Creative Commons picture: the licence says the credit must link to it. |
| `thumbnail` | — | A different, usually tighter-cropped picture for the small cards. |
| `categories` | ✅ | Put the sport first, then its section, then the kind of story: `["Cricket", "International Action", "Match Reports"]`. The sport and section become the red eyebrow above the headline. A new value creates its own page and RSS feed automatically; to put it in the toolbar, add it to `data/navigation.yaml`. |
| `tags` | — | Finer topics — teams, players, tournaments. They get their own pages under `/tags/`. |
| `author` | — | Shown in the byline **on the article page only** — never on the homepage, a sport page or a card. Defaults to "SportsOne Desk". |
| `authorRole` | — | e.g. "Football correspondent". |
| `featured` | — | A flag you can use for your own filtering. Where a story appears is decided in `data/homepage.yaml`, not here. |
| `toc` | — | `true` adds an "In this article" contents box. Worth it for anything over about 1,200 words. |
| `expiryDate` | — | The story disappears from the site after this date. See "Archiving". |
| `noindex` | — | `true` asks Google not to list the page. |
| `match` | — | Optional match details, used by the `scoreline` shortcode inside a story. No scoreline is ever printed above the headline — the Live Scores strip on the front page does that job. |

### Choosing where a story appears

Nothing in an article decides where it lands. You choose that in two plain-text
files, and you never touch a template.

**`data/homepage.yaml` — the front page**

```yaml
spotlight:                       # exactly 5, they rotate every 5 seconds
  - second-test-day-two-collapse
  - riverside-edge-kingsport-late-winner
  - hard-court-semi-final-epic
  - the-ninety-million-midfield-gamble
  - wet-race-strategy-masterclass

top_stories:
  carousel:                      # the big panel: 4 stories, rotating
    - istanbul-2005-milan
    - headingley-2019-stokes
    - raducanu-2021-us-open
    - bolt-berlin-9-58
  side:                          # the 4 stories stacked beside it
    - manchester-city-treble
    - t20-powerplay-batting
    - djokovic-24-majors
    - kipchoge-sub-two

editors_picks:                   # 6, two to a row, beside More Headlines
  - anderson-broad-new-ball
  - dortmund-gegenpressing
  - alcaraz-sinner
  - senna-donington-1993
  - ipl-franchise-economics
  - curry-three-point
```

**`data/sports.yaml` — the top of each sport page**

```yaml
cricket:
  carousel:                      # exactly 5, rotating
    - chasing-under-lights
    - second-test-day-two-collapse
    - spin-doctrine-shift
    - t20-powerplay-economics
    - franchise-calendar-squeeze
  static:                        # the 2 fixed stories underneath
    - academy-fast-bowling-programme
    - auction-overspend-correction
```

The same block also runs that sport's section on the front page, so you choose
a sport's top stories once.

**Naming a story.** Use its slug — the last part of its web address.
`/posts/second-test-day-two-collapse/` is `second-test-day-two-collapse`.

**What happens if you leave a slot short or mistype a slug.** That line is
ignored and the gap is filled with the newest story that is not already
somewhere else on the page. The page is never half empty and no story ever
appears twice in the same run of slots. Your choices always come first.

**What you never have to configure.** More Headlines, every news feed, every
category page and every RSS feed fill themselves, newest first.

**Practical rules of thumb**

* Your five biggest stories go in `spotlight`, in the order you want them seen.
* Put the story you most want read second in `top_stories.static_a` — a fixed
  slot is read more than a rotating one.
* Revisit `data/sports.yaml` about once a week; the feed below it keeps itself
  current every time you publish.

### Match details

```yaml
match:
  competition: "Premier Division · Matchday 3"
  venue: "Riverside Stadium"
  status: "Full time"
  home: { name: "Riverside Athletic", score: "2" }
  away: { name: "Kingsport FC", score: "1" }
```

This prints a navy scoreline panel under the headline and adds sports-event
information for search engines. Every field is optional; if you leave the whole
`match:` block out, nothing appears.

---

## Extras you can drop into an article

These are "shortcodes" — short instructions in curly braces. Copy and paste.

**Pull quote**

```markdown
{{< pullquote source="Ravi Menon, Riverside head coach" >}}
Ten men, one idea, ninety-four minutes.
{{< /pullquote >}}
```

**Key points box**

```markdown
{{< keypoints title="The key points" >}}
- Riverside won with ten men
- Kingsport have conceded five set-piece goals in three matches
{{< /keypoints >}}
```

**Statistics strip** — value and label separated by a `|`

```markdown
{{< stats "6|Corners in the half" "1.42|Riverside xG" "0.81|Kingsport xG" >}}
```

**Scoreline inside the body**

```markdown
{{< scoreline home="Riverside" homeScore="2" away="Kingsport" awayScore="1"
              caption="Premier Division · Riverside Stadium" >}}
```

**Picture with a caption and a chosen shape**

```markdown
{{< figure src="/images/photo.jpg" alt="What is happening"
           caption="Who took it and what it shows" ratio="wide" >}}
```

`ratio` can be `wide` (16:9, the default), `thumb` (square), `portrait` (4:5) or
`banner` (21:9).

---

## Updating an article that is already live

1. Open the file in VS Code and edit it.
2. Update `lastmod:` to now. This makes the "Updated …" line appear, which is
   good practice and good for search engines.
3. **Terminal ▸ Run Task… ▸ 3 · Publish everything**

Never change `slug:` on a published article — anyone who shared the old link
would get a 404.

**Correcting a factual error?** Say so. Add a line at the end of the article:

```markdown
---

*This article was updated on 14 August to correct the attendance figure.*
```

---

## Taking an article down

Three ways, in order of preference.

### 1. Unpublish it but keep it (recommended)

Change `draft: false` to `draft: true`, publish. The page disappears from the
site; the file stays in the repository so you can bring it back.

### 2. Let it expire on a date

```yaml
expiryDate: 2026-12-31T00:00:00+05:30
```

The article vanishes from the site the next time it is built after that date.
Useful for competitions, offers, or a live blog you know will go stale.

> **The catch:** a static site only changes when it is rebuilt. If nobody
> pushes anything for a week, an expired article stays up for that week. If
> that matters to you, see "Rebuilding on a schedule" below.

### 3. Delete it properly

Only when the article should never have existed.

1. Right-click the file in VS Code ▸ **Delete**.
2. Delete its picture from `static/images/` too.
3. Publish.

The file is gone from the site but stays in the repository's history, so it can
be recovered by a developer if you change your mind.

---

## Archiving older articles

Nothing is required. Old articles cost you nothing, keep earning search traffic,
and Hugo builds thousands of pages in seconds. The homepage only ever shows the
newest stories anyway.

If you want them out of the way for tidiness, make a folder and move them:

```text
content/posts/archive/2025/
```

They stay published at the same web addresses — the folder does not affect the
address, because that is set by `slug`. Only move things you want to *keep*
published. To unpublish, use `draft: true` as above.

**A yearly tidy-up, if you like routine:**

1. In VS Code press `Cmd/Ctrl + Shift + F` and search for `date: 2025-`.
2. Drag those files into `content/posts/archive/2025/`.
3. Preview to check nothing looks broken.
4. Publish.

---

## Updating the live scores

The scores widget reads one file: **`data/scores.yaml`**. Open it in VS Code and
type over the values.

```yaml
updated: "13 Aug 2026, 19:45 IST"

sports:
  - name: Football
    matches:
      - competition: "Premier Division · Matchday 3"
        state: live
        stateLabel: "Live"
        venue: "Riverside Stadium"
        teams:
          - name: "Riverside Athletic"
            score: "2"
            detail: "78'"
            active: true
          - name: "Kingsport FC"
            score: "1"
            detail: ""
        note: "Chhetri converts to put Riverside ahead."
        stats:
          - label: "Possession"
            value: "38%"
        link: "/posts/riverside-edge-kingsport/"
```

### Scores now refresh on their own

`data/scores.yaml` is rewritten every fifteen minutes by
`scripts/fetch-scores.py`, run from `.github/workflows/scores.yml`. You do not
have to type in a score again, though you still can — see "Editing by hand"
below.

Which sports are fetched, how many matches are kept and how many days of
fixtures to pull in are set in **`data/scores-source.yaml`**.

A note on where the data comes from: there is no Google live-scores feed. The
Google News API was retired in 2011 and Google has never published match scores
as a public endpoint. The site uses TheSportsDB, whose free tier needs no
account. Swapping provider is one class in `scripts/fetch-scores.py`.

### Choosing which matches go on the front page

The strip on the front page does **not** show everything in this file. It shows
the matches whose `id` you list at the top, in the order you list them, and
those survive every automatic refresh:

```yaml
featured_matches:
  - cricket-001          # on the front page
  - football-001         # on the front page
  - tennis-001           # on the front page
# football-003 is not listed, so it stays off the front page
```

Every match block carries an `id:`. To put a match up, add its id to that list.
To take it down, delete the line — the match itself stays in the file and keeps
appearing on `/scores/`, which always shows everything.

`/scores/` marks the chosen ones "On the front page", so you can always see at a
glance what a reader is being shown.

When you have pinned nothing — or when the matches you pinned have finished and
dropped out of the feed — the strip fills itself with whatever is live. Set
`auto_feature: false` in `data/scores-source.yaml` if you would rather it showed
only your pins and nothing else.

### Editing by hand

You still can, and the automation will not fight you over `featured_matches`.
It will overwrite the `sports:` section on its next run, though, so a score you
type in by hand lasts until the next refresh. To stop that: Actions tab ▸
"Refresh live scores" ▸ ⋯ ▸ Disable workflow. Everything then works exactly as
it did before, with you editing the file.

**The five rules of this file**

1. **Indentation is two spaces, never a tab.** Tabs break it. VS Code inserts
   spaces automatically here — do not fight it.
2. **Anything containing a colon must be in "quotes"** — cricket scores like
   `"218/3"` and times like `"14:00 IST"` especially.
3. `state:` must be exactly one of `live`, `upcoming`, `completed` or `break`.
   That is what colours the badge.
4. `active: true` puts the red dot next to the team currently batting, serving
   or leading. Use it on at most one team per match.
5. **Every match needs a unique `id:`.** Anything is fine as long as no two
   matches share one. If you delete a match, delete its id from
   `featured_matches` too.

To remove a match, delete its whole block, starting at the `- id:`
line. To remove a sport, delete from its `- name:` line down to the next
`- name:` at the same indentation.

**If you get it wrong**, the build fails with a red cross on the Actions tab and
*the live site does not change* — the previous version stays up. Fix the file
and publish again. You cannot break the live site by mistyping this.

Not using live scores at all? Open `hugo.toml` and set:

```toml
showLiveScores = false
```

---

## Adding a new sport

There is no code to change.

**A new category** — write `categories: ["Kabaddi"]` in any article and publish.
Hugo creates `/categories/kabaddi/` and its RSS feed. Give the page a proper
title by creating `content/categories/kabaddi/_index.md`:

```markdown
---
title: "Kabaddi"
description: "Pro league coverage, raider analysis and the youth pipeline."
---
```

(The description is used by Google. It is deliberately not printed under the
heading on the page — sport headings stay clean.)

**Putting it in the toolbar** — open `data/navigation.yaml` and add a block
under `primary:`. Order in the file is order on screen.

```yaml
  - name: "Kabaddi"
    url: "/categories/kabaddi/"
```

**Giving it a dropdown** — add `children:` underneath. A sport with no
`children` is a plain link with no dropdown, which is why Tennis and Other
Sports have none.

```yaml
  - name: "Kabaddi"
    url: "/categories/kabaddi/"
    children:
      - name: "Pro League"
        url: "/categories/pro-league/"
```

Each sub-item needs its own folder under `content/categories/` in the same way.

**Giving it a front-page section** — add a block to `data/sports.yaml` keyed by
the category slug (`kabaddi`). Without one it still works: the carousel fills
itself with that sport's newest stories.

The same file drives the toolbar, the dropdowns, the mobile menu and the footer
Sports column, so they can never disagree with each other.

---

## Video on a sport page

Three clips sit at the foot of each sport page, set in **`data/videos.yaml`**.

```yaml
cricket:
  - id: "KL0ONdUT2zo"          # the part of a YouTube address after watch?v=
    title: "The inspiration behind the ICC Men's Cricket World Cup 2027 brand"
    channel: "ICC"              # printed as the credit under the clip
    url: "https://www.youtube.com/@ICC"
```

Copy a block to add a clip, delete a block to remove one. A sport with no block
simply has no video section and nothing else on the page moves.

**What a reader's browser actually loads.** Only the still image, and only when
they scroll to it. Nothing is requested from YouTube until they press play, and
the player that then appears is the no-cookie one. That is why the section does
not cost the site its "no third-party scripts on load" property.

**Credit.** The channel name under each clip is the credit and links back to the
channel. Keep it filled in — it is the condition on which embedding is offered.

---

## Scheduling an article for later

Set `date:` in the future and `draft: false`.

The catch is the same as with `expiryDate`: the site only changes when it is
rebuilt, so an article dated for 6am tomorrow appears the next time anyone
publishes anything after 6am — not automatically at 6am.

### Rebuilding on a schedule

If you want scheduled articles to appear on the dot, add this to
`.github/workflows/deploy.yml`, immediately under the `workflow_dispatch:` line:

```yaml
  schedule:
    - cron: '30 0,6,12 * * *'   # 06:00, 11:30 and 17:30 India time
```

GitHub's cron runs in UTC, which is India time minus 5 hours 30 minutes. Free
GitHub Actions minutes are generous but not unlimited — three rebuilds a day is
plenty for most newsrooms.

---

## Writing well for this site

* **Headlines** — under 90 characters. Spotlight and the carousels give a
  headline three or four lines; longer headlines still show in full everywhere
  else, but they read better short.
* **Summaries** — one or two sentences, under about 160 characters. This is the
  text Google shows and the text on every card.
* **Sub-headings** — use `##`. Only go down to `###` inside a `##` section.
  Never start an article with `#`; the headline already is the `#`.
* **Alt text** — every picture, every time.
* **Links** — say where the link goes. "The full squad list" beats "click here".
* **Categories** — sport first, then its section, then the kind of story:
  `["Football", "Premier League", "Match Reports"]`. They decide which pages
  and feeds the story appears in. They are deliberately **not** printed above
  the headline: a reader inside Cricket does not need telling they are in
  Cricket. The line in that position is the picture credit instead.
* **Bylines** — you never have to hide one. A byline appears only once a reader
  has opened the article; it is never on a card, a feed or the front page.

---

## Your daily routine, on one line

**Run Task ▸ New article → write → `draft: false` → Run Task ▸ Publish → check
the green tick on the Actions tab.**
