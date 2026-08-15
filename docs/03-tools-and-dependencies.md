# 3 · Every tool this project uses

A reference. You do not need to read it start to finish — look things up here
when you need to.

---

## The short version

| Tool | What it is for | Where it runs | Do you need it? |
|------|----------------|---------------|-----------------|
| **Git** | Records changes and sends them to GitHub | Your computer | Yes |
| **VS Code** | Where you write | Your computer | Yes |
| **Hugo (extended) 0.165.0** | Turns Markdown into the website | Your computer *and* GitHub | Yes, for previewing |
| **GitHub** | Stores the project, runs the publishing | The internet | Yes |
| **GitHub Actions** | Builds and publishes automatically | The internet | Already set up |
| **GitHub Pages** | Serves the website to readers | The internet | Already set up |
| **GoDaddy** | Owns the domain name | The internet | Yes |

Everything except the domain is free.

**There is no Node.js, no npm, no package.json, no build tool chain and no
dependencies to update.** That is deliberate. The only thing that can ever go
out of date is Hugo itself, and that is pinned to a specific version.

---

## Hugo

**What it is.** A program that reads your Markdown files and templates and
writes out a complete website of HTML, CSS and JavaScript files.

**Version.** 0.165.0, **extended** edition. The extended edition is required —
the plain edition cannot process this project's stylesheet.

**Where the version is pinned.** In `.github/workflows/deploy.yml`:

```yaml
env:
  HUGO_VERSION: 0.165.0
```

GitHub installs exactly this version every time. That means a new Hugo release
can never break your site overnight. To upgrade, change that number, push, and
check the Actions tab goes green.

**Installing it locally**

```bash
# Mac
brew install hugo

# Windows
winget install Hugo.Hugo.Extended
```

**Checking it**

```bash
hugo version
```

Must show `v0.165` or higher **and** the word `extended`.

**Keeping local and GitHub in step.** If your local Hugo is much newer than the
pinned version, something might preview fine but fail on GitHub. Once or twice a
year, match them: upgrade locally (`brew upgrade hugo`), then update
`HUGO_VERSION` in the workflow to the same number and push.

**Commands you might use**

| Command | What it does |
|---------|--------------|
| `hugo server` | Preview at <http://localhost:1313>, live-reloading |
| `hugo server -D` | …including drafts |
| `hugo` | Build into `public/` |
| `hugo --minify --gc` | Build the way GitHub does |
| `hugo new content posts/football/x.md` | Create an article from the template |
| `hugo --printPathWarnings` | Warn about two pages claiming the same address |

Documentation: <https://gohugo.io/documentation/>

📺 [Search: "hugo static site tutorial"](https://www.youtube.com/results?search_query=hugo+static+site+generator+tutorial)

---

## Git

**What it is.** The system that records every change and moves files between
your computer and GitHub. VS Code drives it for you — the buttons in the Source
Control panel are Git.

**Version.** Anything from 2.30 onwards. Check with `git --version`.

**One-time configuration** (only needed if VS Code complains):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

**The five commands worth knowing**

| Command | Plain English |
|---------|---------------|
| `git status` | What have I changed? |
| `git add .` | Mark all my changes as ready |
| `git commit -m "note"` | Save them, with a note |
| `git push` | Send them to GitHub — this publishes |
| `git pull` | Get changes made on another computer |

**A word about `main`.** Your work lives on a branch called `main`. The workflow
publishes whenever `main` changes. You never need another branch, though a
developer might create one for a redesign.

📺 [Search: "git and github for beginners"](https://www.youtube.com/results?search_query=git+and+github+for+beginners)

---

## VS Code

**What it is.** A free text editor from Microsoft. To you it is a word processor
that happens to speak Git.

**The four parts of the window you will use**

* **Explorer** (top icon) — the file list
* **Search** (magnifier) — find text across every article at once
* **Source Control** (branching lines) — where you publish
* **Terminal ▸ Run Task…** (top menu) — the one-click jobs

**The extensions this project recommends** — VS Code offers to install them the
first time you open the folder; the list lives in `.vscode/extensions.json`:

| Extension | Why |
|-----------|-----|
| Hugo Language and Syntax Support | Understands Hugo files and front matter |
| Markdown All in One | Makes writing Markdown far easier |
| markdownlint | Points out Markdown mistakes as you type |
| YAML | Catches indentation errors in `data/scores.yaml` |
| GitLens | Shows who changed what, and when |
| GitHub Pull Requests | GitHub sign-in inside VS Code |
| Code Spell Checker | Spelling |
| EditorConfig | Keeps file formatting consistent |

**The settings this project applies** (`.vscode/settings.json`) — auto-save
after 1.5 seconds, word wrap in Markdown, `public/` hidden from the file list,
and `git.postCommitCommand: "push"` so committing also publishes.

**The tasks** (`.vscode/tasks.json`) — the five jobs on the
**Terminal ▸ Run Task…** menu. Documented in
[docs/02](02-publishing-and-managing-articles.md).

📺 [Search: "vs code for writers markdown"](https://www.youtube.com/results?search_query=vs+code+markdown+writing+tutorial)

---

## GitHub Actions

**What it is.** GitHub's built-in automation. The instructions are in
`.github/workflows/deploy.yml`.

**When it runs.** On every push to `main`, and manually from the Actions tab.
It deliberately ignores changes to `docs/`, `README.md` and `.vscode/`, so
editing documentation does not trigger a pointless rebuild.

**What it does**

1. Installs Hugo 0.165.0 extended
2. Checks out your repository, full history
3. Asks GitHub Pages for the site's address
4. Restores a cache of previously generated assets, to be quick
5. Builds: `hugo --minify --gc --cleanDestinationDir --printPathWarnings`
6. **Verifies** — homepage, sitemap, search index, articles folder and hero page
   all exist, and at least five HTML pages were produced
7. Uploads the result and deploys it

**The actions it uses**, all current, official and maintained:

| Action | Version | Purpose |
|--------|---------|---------|
| `actions/checkout` | v4 | Fetch your files |
| `actions/configure-pages` | v5 | Work out the site address |
| `actions/cache` | v4 | Speed up repeat builds |
| `actions/upload-pages-artifact` | v3 | Package the built site |
| `actions/deploy-pages` | v4 | Publish it |

These use the modern GitHub Pages deployment API. The old approach of pushing a
`gh-pages` branch with a third-party action is not used and is not needed.

**Permissions.** The workflow requests only `contents: read`, `pages: write` and
`id-token: write` — the minimum for publishing. It cannot modify your code.

**Secrets.** There are none, because the site needs none. Should you ever add a
service that requires a key, put it in **Settings ▸ Secrets and variables ▸
Actions** and reference it as `${{ secrets.NAME }}`. Never type a key into a
file in the repository.

---

## GitHub Pages

Static file hosting, free, with a CDN and free HTTPS certificates.

| Limit | Value | Realistically |
|-------|-------|---------------|
| Site size | 1 GB | Thousands of articles |
| Bandwidth | ~100 GB/month | Comfortable for a growing news site |
| Builds | ~10 per hour | Publish as often as you like |

Set-up: [docs/04-deployment-and-domain.md](04-deployment-and-domain.md).

---

## Fonts

Three typefaces, all under the SIL Open Font License, all **self-hosted** in
`static/fonts/` — 216 KB in total.

| Font | Used for | Files |
|------|----------|-------|
| **Archivo** | Headlines, section titles, scores | `archivo-latin*.woff2` |
| **Inter** | Navigation, buttons, metadata, cards, all numerals | `inter-latin*.woff2` |
| **Cambo** | Block quotes only | `cambo-latin*.woff2` |
| *System sans / Arial / Helvetica* | Article body text | none — already on every device |

Self-hosting means the site makes **no requests to Google or any other third
party**. Nothing about your readers leaves your domain, so no cookie banner and
no privacy policy about third-party fonts is required.

To swap a font: put the `.woff2` files in `static/fonts/`, update the
`@font-face` rules at the top of `assets/css/01-tokens.css`, and change the
`--font-display` / `--font-ui` variables just below them.

---

## The stylesheet

Nine small CSS files in `assets/css/`, joined into one minified,
content-hashed file at build time — so browsers make exactly one CSS request and
cache it forever, but see changes instantly when you make them.

| File | Contents |
|------|----------|
| `01-tokens.css` | Every colour, size, space and font, declared once |
| `02-base.css` | Reset, typography roles, accessibility |
| `03-layout.css` | Containers, grids, section furniture, image frames |
| `04-header.css` | Masthead, sports bar, mobile drawer, breaking strip |
| `05-cards.css` | The reusable story units |
| `06-home.css` | Homepage blocks and the hero shell |
| `07-widgets.css` | Live scores |
| `08-article.css` | Article page and long-form text |
| `09-footer.css` | Footer |
| `10-carousel.css` | Spotlight, Top Stories and every sport carousel |

To change the look, start in `01-tokens.css`. See
[docs/06-design-system.md](06-design-system.md).

---

## The JavaScript

Two files, about 300 lines in total, no libraries, no frameworks.

| File | Job |
|------|-----|
| `assets/js/site.js` | Sports dropdowns, mobile menu, carousels, live-score filters, copy-link button |
| `assets/js/search.js` | The search page — loaded only on `/search/` |

There is one more script, and it never reaches a reader's browser:

| File | Job |
|------|-----|
| `scripts/fetch-scores.py` | Pulls live scores into `data/scores.yaml`. Runs in GitHub Actions, not on the site. Standard library only — nothing to install. |

Everything else works with JavaScript switched off, and so does most of that
list: the dropdowns open on keyboard focus in CSS alone, and each carousel is a
scroll-snapping row that can be swiped and tabbed through without any script.
The script adds automatic rotation and the arrows and dots — which is why those
controls stay hidden until it has loaded, rather than sitting there doing
nothing.

---

## Security

* No server, no database, no login — there is nothing to break into.
* No third-party scripts, so no supply-chain risk from someone else's CDN.
* No secrets or API keys anywhere in the repository. `.gitignore` blocks `.env`
  files from being committed by accident.
* The workflow has read-only access to your code.
* HTTPS is enforced by GitHub Pages with certificates it renews itself.
* Assets are served with Subresource Integrity hashes, so a modified CSS or JS
  file would be refused by the browser.

---

## Backups

Your work exists in three places at once: your computer, GitHub, and the built
site. GitHub keeps the complete history of every version of every article
forever.

To take a copy you can hold:

```bash
cd /path/above/the/project
git clone --mirror https://github.com/yourname/sportsone-world.git sportsone-backup.git
```

Put that folder on an external drive. It contains everything, including history.

---

## Upgrading, once or twice a year

1. `brew upgrade hugo` (Mac) or `winget upgrade Hugo.Hugo.Extended` (Windows)
2. `hugo version` — note the new number
3. Preview the site locally and click around
4. Update `HUGO_VERSION` in `.github/workflows/deploy.yml` to match
5. Publish, and check the Actions tab goes green

If anything looks wrong, put the old number back and publish again. Nothing else
in the project needs updating, ever.
