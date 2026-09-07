# Automated sports news every morning — research and recommendation

**Question asked:** can SportsOne pull the latest relevant sports news from
around the world every morning at about 06:00 IST, for free, using GitHub
Actions and Cloudflare?

**Short answer:** yes for *finding and drafting*, no for *publishing unattended*.
The retrieval, the fact-checking and above all the photography are the hard
parts, and none of them are solved by a language model. Build the pipeline so
a journalist opens their laptop at 07:00 to eight drafted stories with sources
attached, not to eight stories already live.

Everything below is costed at £0 for the first two phases.

---

## Contents

1. [The mistake to avoid](#1--the-mistake-to-avoid)
2. [Which free LLM API](#2--which-free-llm-api)
3. [How accurate each one is, and at what](#3--how-accurate-each-one-is-and-at-what)
4. [Can an LLM fetch current news, sources and images?](#4--can-an-llm-fetch-current-news-sources-and-images)
5. [The workflow, end to end](#5--the-workflow-end-to-end)
6. [Publishing into the existing setup](#6--publishing-into-the-existing-setup)
7. [Limitations and risks](#7--limitations-and-risks)
8. [What I would actually build](#8--what-i-would-actually-build)
9. [Costs](#9--costs)

---

## 1 · The mistake to avoid

The natural design is "ask an LLM what happened in sport today and publish the
answer". It fails for three separate reasons, and they are worth separating
because they have three different fixes.

| | The problem | The fix |
|---|---|---|
| **Retrieval** | A model has no idea what happened this morning. Its training stopped months ago. Ask it anyway and it will produce fluent, plausible, invented sport. | Fetch real feeds first. The model only ever sees text you retrieved. |
| **Verification** | Even given a real source, models get scores, dates, spellings and attributions subtly wrong — the exact things a sports desk is judged on. | Check every number and name against a second source or a stats API before a human ever sees the draft. |
| **Imagery** | There is no free, legal, automatic source of today's match photography. This is the part people underestimate. | Do not auto-fetch photographs. Use a controlled file-picture library, or licence an agency feed. |

The rest of this document is the architecture that follows from those three
sentences:

```text
   real feeds  →  cluster & rank  →  LLM drafts  →  validate  →  human  →  publish
   (facts)        (editorial)        (words)        (facts)      (call)
```

The LLM is fourth in that list, not first.

---

## 2 · Which free LLM API

All of these are genuinely free to start and need no card. The important
column is the last one.

| Provider | Free allowance (verify before you build — these change monthly) | Quality for this job | Watch out for |
|---|---|---|---|
| **Google Gemini** — 2.5 Flash / Flash-Lite | The most generous of the general-purpose free tiers; enough for tens of stories a day many times over | **Best.** Long context, follows "use only the text I gave you" instructions well, strong at structured JSON output | **Its terms say Google uses free-tier prompts and outputs "to provide, improve, and develop Google products", and that "human reviewers may read, annotate, and process your API input and output".** Fine for public RSS. Not fine for anything embargoed or exclusive |
| **Cloudflare Workers AI** | 10,000 Neurons/day free on both Free and Paid Workers plans; overflow billed at $0.011 per 1,000 | Good enough for summarising and classifying. Models are smaller (Llama 3.x, Mistral class) so headlines need more editing | Runs *inside* Cloudflare, so if the site moves to Cloudflare Pages there is no extra key, no extra vendor, and no egress. This is the answer to the "using Cloudflare" half of the question |
| **Groq** | Fast, useful daily limits, applied per organisation rather than per key | Good. Very fast, which does not matter for a once-a-day job | Website terms grant a licence for "personal, non-commercial use"; the API terms are separate and less clear. Get this in writing before a commercial newsroom depends on it |
| **GitHub Models** | Included with the GitHub account the site already uses; modest rate limits | Good | Zero plumbing inside GitHub Actions — no new secret, no new vendor. Best *convenience* fit if the job stays in Actions |
| **OpenRouter free models** | Varies by model, and models appear and disappear | Variable | Do not build a daily production job on a free model that can be withdrawn without notice |

### Recommendation

**Gemini 2.5 Flash for the pilot. Move to a paid key before it stops being a
pilot.**

The second sentence matters more than the first. Ten stories a day is roughly
150,000–400,000 tokens — on any current paid tier that is **single-digit cents
per day**. Paying removes, in one step: the "is this allowed commercially"
question, the "Google may read our prompts" question, and the quota-exhaustion
failure mode. A newsroom that will not spend $3 a month on this should not be
automating it.

If the site moves to Cloudflare Pages, **Workers AI is the tidier home** for the
same reason: one vendor, one dashboard, one bill, and the free 10,000 Neurons a
day cover a job this size comfortably.

---

## 3 · How accurate each one is, and at what

Accuracy is not a property of the model. It is a property of what you ask it to
do. Split the job:

| Task | Any of these models | Notes |
|---|---|---|
| Deduplicating 200 headlines into 30 stories | **Reliable** | This is clustering, not knowledge |
| Deciding which 8 of 30 matter to an India-first sports audience | **Reliable enough to shortlist, not to decide** | Ranking is editorial. Let it propose an order; let a person confirm it |
| Summarising a source you handed it | **Reliable** | The single thing LLMs are best at |
| Writing a headline, standfirst, summary, alt text, tags | **Reliable** | Exactly the fields the SportsOne front matter needs |
| Classifying into Cricket / Football / Tennis / Other Sports, and into a section | **Reliable** | Constrain it to the list of sections that exist |
| Stating a score, a date, a transfer fee, a player's club | **Not reliable** | Must come from the retrieved text or a stats API, and must be checked |
| Knowing what happened this morning without being told | **Never** | It cannot. It will still answer |

Two rules turn "not reliable" into "reliable":

1. **Closed-context prompting.** *"Using only the text between the markers, and
   nothing you believe you already know, write …"* Then reject any output
   containing a number that does not appear in the input.
2. **A source per claim.** Ask for JSON with a `sources` array of URLs, one per
   paragraph. A paragraph that cannot cite the text it came from is dropped, not
   published.

---

## 4 · Can an LLM fetch current news, sources and images?

### 4.1 · News — no, and it does not need to

Real feeds do this better, faster and free. In rough order of usefulness to a
sports desk:

| Source | Cost | Commercial use | What it is good for |
|---|---|---|---|
| **Governing-body and club RSS** — ICC, BCCI, FIFA, UEFA, Premier League, ATP, WTA, F1, Olympics, national federations | Free | Primary source, published to be republished as fact | The strongest single input. It is the announcement, not somebody's write-up of it |
| **The Guardian Open Platform** | Free, real API key, no commercial restriction | Yes | Genuinely free and production-grade, including full article text. One publisher's view, but a good one for football and cricket |
| **Currents API / NewsData.io** free tiers | Free | Explicitly permitted on the free tier | Breadth across thousands of outlets. Use for *leads*, not text |
| **NewsAPI.org / GNews** free tiers | Free | **No — development and testing only**, and NewsAPI delays articles and blocks non-localhost use | Prototyping only. Do not ship on these |
| **TheSportsDB** (already wired into this project, see `scripts/fetch-scores.py`) | Free tier | Yes | Scores, fixtures, results. The most *reliable* input you have, because it is data rather than prose |
| **Google News RSS** | Free | Grey. It is not a documented public API | Works, widely used, not something to build a business on |

**The copyright line, plainly:** facts are not copyrightable, expression is. You
may report that Real Madrid signed a player for €125m and cite where you read
it. You may not reproduce, and should not have a model paraphrase, another
outlet's article. A rewritten wire story is both a legal risk and, in Google's
words, "unoriginal content with little user value" — see §7.

The defensible automated story types are therefore narrow and worth naming:

* results, scorecards and fixture round-ups built from a **data** feed;
* stories built from a **press release** by a governing body or club;
* "what to watch today" previews built from the fixture list;
* aggregation pieces that *link out* and add SportsOne's own framing.

Everything else needs a journalist.

### 4.2 · Images — this is the blocker

There is no free, legal, automatic supply of today's sport photography. Every
shortcut here ends badly.

| Option | Verdict |
|---|---|
| **Agency licence** — Getty, Reuters, AP, PA, Imago, Action Images | **The only real answer for current match photography.** Paid, and the API is offered to accounts with an existing agreement. Budget for this before you budget for anything else on this page |
| **Getty's free embed** | Non-commercial websites and blogs only. A commercial newsroom using it is in breach |
| **Wikimedia Commons** | Free, permissive, and what SportsOne already uses. Excellent for *file* pictures — a player, a stadium, a trophy. Almost never has this morning's match |
| **Club and league media portals** | Often free for editorial use with attribution, under per-competition terms. Worth the paperwork; genuinely useful for the sports you cover most |
| **Unsplash / Pexels** | Generic stock. No editorial value and no identifiable athletes at real events |
| **Scraping images from the outlets in your feed** | Copyright infringement. Not an option |
| **AI-generated images** | **Never for news.** A synthetic depiction of a real event that did not look like that is a fabrication, whatever the caption says |

**The practical automated answer** is a *file-picture library keyed to entities*.
Build a small table mapping a player, team, competition or venue to a picture
you already hold the rights to — the 30 photographs in `static/images/photos/`
are the start of one. The bot recognises "Yan Diomande, RB Leipzig" in the text,
attaches the RB Leipzig file picture, and captions it honestly as a file
picture. When it recognises nothing, it attaches nothing and the story goes to
the journalist flagged **needs a photograph**.

That is a real newsroom workflow. Auto-fetching a photograph off the web is not.

---

## 5 · The workflow, end to end

```text
 00:15 UTC ── GitHub Actions, scheduled ──────────────────────────────────┐
                                                                          │
   1  FETCH        ~15 RSS feeds + Guardian API + TheSportsDB fixtures    │
                   → 150–300 raw items, cached with their fetch time      │
                                                                          │
   2  FILTER       drop anything older than 24h, anything already         │
                   covered (hash the headline + entities against the      │
                   last 7 days of content/posts/), anything off-beat      │
                                                                          │
   3  CLUSTER      LLM call #1 — group into distinct stories, one         │
                   cluster per real-world event, with every source URL    │
                                                                          │
   4  RANK         LLM call #2 — score each cluster for an India-first    │
                   sports audience; keep the top 8–10                     │
                                                                          │
   5  VERIFY       no LLM. Cross-check every number and proper noun in    │
                   the cluster against TheSportsDB and a second source.   │
                   Anything single-sourced is marked UNCONFIRMED          │
                                                                          │
   6  DRAFT        LLM call #3, one per story — headline, summary,        │
                   300–500 words, alt text, tags, section, and a          │
                   `sources` array. Closed-context prompt                 │
                                                                          │
   7  ILLUSTRATE   entity → file-picture lookup. No match, no picture,    │
                   and the story is flagged                               │
                                                                          │
   8  WRITE        one .md + one picture per story into inbox/, in the    │
                   same shape a journalist would use, with `Hold: yes`    │
                                                                          │
   9  HAND OVER    commit to a `morning-brief` branch and open a pull     │
                   request titled "Morning brief — 29 August"             │
                                                                          │
  10  NOTIFY       the desk gets one message with 8 links                 │
                                                                          └──
 07:00 IST ── a journalist reads, edits, deletes three, publishes five
```

### Scheduling it for 06:00 IST

IST is UTC+5:30, so 06:00 IST is **00:30 UTC**:

```yaml
on:
  schedule:
    - cron: '15 0 * * *'      # 05:45 IST — early, because it will be late
  workflow_dispatch:
```

Three things GitHub documents about scheduled workflows, all of which matter
here:

* **"The `schedule` event can be delayed during periods of high loads."** In
  practice, five to twenty minutes, occasionally more. Schedule 15 minutes
  early and never promise the desk an exact minute.
* **"Scheduled workflows run on the latest commit on the default branch"** and
  only on the default branch.
* **"In a public repository, scheduled workflows are automatically disabled when
  no repository activity has occurred in 60 days."** A newsroom publishing daily
  will never hit this; a quiet month over the off-season could.

If minute-accuracy ever matters, a **Cloudflare Worker Cron Trigger** is more
punctual than GitHub's scheduler, and can start the GitHub job by API. That is
worth doing only after the pipeline is proven.

---

## 6 · Publishing into the existing setup

### 6.1 · What the setup actually is today

Worth stating plainly, because the brief describes it differently:

| | Today | Note |
|---|---|---|
| Build | GitHub Actions, Hugo 0.165 pinned | `.github/workflows/deploy.yml` |
| Hosting | **GitHub Pages** | `static/CNAME` contains `sportsone.world` |
| DNS | **GoDaddy**, four A records to GitHub | `docs/04-deployment-and-domain.md` |
| Cloudflare | **not currently in use anywhere** | |

So "the existing GitHub + Cloudflare setup" is really a GitHub-only setup. Two
ways forward, both fine:

**Option A — leave hosting alone.** Nothing to change. The morning job is one
more workflow beside the two that already exist. Choose this unless there is a
reason not to.

**Option B — move hosting to Cloudflare Pages.** Free, unlimited bandwidth,
noticeably faster to Indian readers than GitHub Pages, and it puts Workers AI,
Cron Triggers, KV (for the story-seen cache) and R2 (for the picture library) in
the same account as the site. Migration is: connect the repo to Cloudflare
Pages, build command `hugo --minify`, output directory `public`, then move the
domain's nameservers from GoDaddy to Cloudflare. Nothing in the project is tied
to GitHub Pages — `docs/04` already says as much.

### 6.2 · The bot publishes exactly the way a journalist does

The `inbox/` folder added for the newsroom is also the right interface for a
machine. The morning job writes `story-1.md` + `story-1.jpg` into `inbox/`, and
`scripts/import-articles.py` does the resizing, the filing, the front-matter and
the front-page placement. One code path, human or robot, and every safety check
in the importer applies to both.

### 6.3 · One thing that will bite you, and has already

GitHub documents that **"events triggered by the `GITHUB_TOKEN` will not create
a new workflow run"**, with `workflow_dispatch` and `repository_dispatch` as
explicit exceptions. So a commit made by an automation does **not** start the
publish workflow. The fix is one step at the end of the automation:

```yaml
      - name: Ask the site to publish
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: gh workflow run "Build and deploy to GitHub Pages" --ref main
```

…and `actions: write` in that workflow's `permissions:`. This is already done in
`.github/workflows/inbox.yml` and `.github/workflows/scores.yml`.

---

## 7 · Limitations and risks

| Risk | How likely | What it costs you | Mitigation |
|---|---|---|---|
| **Fabricated facts** — invented scores, quotes, transfers | High, if the model is asked anything open-ended | Corrections, and the desk's credibility | Closed-context prompts; reject output containing numbers absent from the input; source per paragraph; a human before publish |
| **Defamation** | Low but catastrophic | Legal exposure. A machine cannot form the honest belief a defence needs | Never auto-publish anything about misconduct, injury, contract disputes or rumour. Hard-block a keyword list |
| **Copyright in text** | Medium | Takedowns, and a bad reputation with the outlets you want to be cited by | Report facts, cite and link. Never paraphrase a whole article |
| **Image rights** | **High, and the most expensive mistake here** | Agency claims are routinely four figures per image | No automatic image fetching. Licensed library only. See §4.2 |
| **Google "scaled content abuse"** | Medium | Deindexing — the site stops existing commercially | Google's policy targets "using generative AI tools … to generate many pages without adding value for users". Publish fewer, edited, genuinely useful stories. Volume is the tell |
| **Free-tier terms** | Certain, on Gemini's free tier | Your prompts and outputs feed a vendor's product improvement, and may be read by humans | Pay. It is cents. Or restrict the free tier to public RSS only |
| **Quota exhaustion mid-run** | Medium | A partial brief, silently | Cap the run; fail loudly; commit nothing on partial failure — the same rule `fetch-scores.py` already follows |
| **A feed changes or dies** | High over a year | Silent under-coverage | Assert a minimum item count per feed and fail the run if a feed returns nothing two days running |
| **Model deprecated** | High over a year | The job stops | Pin the model id; fail loudly; keep a second provider configured |
| **Schedule drift** | Certain | The brief is late | Run 15 minutes early; do not promise a minute |
| **Nobody reads the brief** | The most likely failure of all | Wasted build | One notification, eight links, one click to publish. If the desk has to go looking for it, it will not happen |

---

## 8 · What I would actually build

Three phases. Each one is useful on its own, and each is a decision point.

### Phase 0 — the morning brief. No publishing at all.

At 05:45 IST, fetch the feeds, cluster and rank them, and commit a single file:
`briefs/2026-08-29.md` — thirty candidate stories, grouped by sport, each with a
one-line summary and its source links. Send it to the desk.

No article is written. No picture is chosen. Nothing can go wrong, and it
delivers most of what was actually asked for: *the latest relevant sports news
from around the world, every morning*. Build this first. It is a weekend's work
and it will still be running in a year.

### Phase 1 — drafts into the inbox.

Add the drafting step. Eight stories a morning land in `inbox/` with
`Hold: yes`, a file picture where one matches, and their sources in the file. A
journalist edits, adds the reporting a machine cannot do, and publishes. The
byline stays human, because a human wrote what matters.

Decide here whether the site carries an "assisted by automation" note. Doing it
before anyone asks is cheaper than doing it after.

### Phase 2 — one narrow automatic class, if you want one.

The only story type I would let publish unattended is the one built entirely
from structured data: **results and scoreboard round-ups from TheSportsDB**, with
a template, no free prose, and a file picture of the competition. No injuries,
no transfers, no quotes, no rumour.

### Never

Automatic publication of prose about live events, illustrated by photographs
sourced automatically from the web. Every part of that sentence is a separate
liability, and together they are how automated news sites get sued and
deindexed.

---

## 9 · Costs

| Item | Phase 0 | Phase 1 | Phase 2 |
|---|---|---|---|
| GitHub Actions | Free (public repo) | Free | Free |
| LLM — free tier | £0 | £0 | £0 |
| LLM — paid, recommended | ~$1/mo | ~$3–8/mo | ~$8–15/mo |
| News feeds — RSS, Guardian, TheSportsDB | £0 | £0 | £0 |
| News API breadth — Currents or NewsData free tier | £0 | £0 | £0 |
| Hosting — GitHub Pages *or* Cloudflare Pages | £0 | £0 | £0 |
| Cloudflare Workers AI, if used instead | £0 within 10,000 Neurons/day | £0 | £0 |
| **Photography — the real cost** | — | agency licence, typically **hundreds per month** | same |

Everything except the photography is free or nearly free. The photography is
not, and no amount of engineering makes it so. Decide that question first,
because it determines whether this is a news site or a links page.

---

## Sources

* Gemini API terms — <https://ai.google.dev/gemini-api/terms>
* Gemini API rate limits — <https://ai.google.dev/gemini-api/docs/rate-limits>
* Cloudflare Workers AI pricing — <https://developers.cloudflare.com/workers-ai/platform/pricing/>
* GitHub Actions, events that trigger workflows — <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows>
* GitHub Actions, triggering a workflow (`GITHUB_TOKEN` rule) — <https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow>
* Google Search spam policies, scaled content abuse — <https://developers.google.com/search/docs/essentials/spam-policies>
* Getty Images rights and clearance — <https://www.gettyimages.com/rights-and-clearance>
* The Guardian Open Platform — <https://open-platform.theguardian.com/>

Free-tier limits for every provider named here change frequently. Check the
provider's own page on the day you build, not this document.
