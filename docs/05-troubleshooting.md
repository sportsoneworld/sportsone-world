# 5 · When something goes wrong

Written for someone who is not a developer. Find your symptom, follow the steps.

---

## First, the two things that are always true

**1. You cannot break the live website by making a mistake in a file.**
If a file is wrong, the build stops and the *existing* site keeps serving. The
worst case is that your new article does not appear.

**2. Nothing is ever lost.**
Every version of every file is kept in GitHub's history, permanently. Even a
deleted article can be recovered.

So: breathe, and work through the steps.

---

## "My article is not on the website"

Work down this list. It is almost always number 1 or number 2.

**1. Is it still a draft?**
Open the file. Near the top it must say `draft: false`. If it says `draft: true`,
change it, save, and publish again.

**2. Did you actually publish it?**
Look at the Source Control icon in VS Code's left sidebar. A blue number badge
means you have changes that have not been sent yet. Run
**Terminal ▸ Run Task… ▸ 3 · Publish everything**.

**3. Has the build finished?**
Go to your repository on GitHub, click the **Actions** tab. The most recent
entry should have a green tick. A yellow dot means "still working" — wait a
minute. A red cross means the build failed; see the next section.

**4. Is the date in the future?**
Check `date:` in the article. If it is later than right now, Hugo deliberately
holds the article back. Set it to a time in the past and publish again.

**5. Is there an `expiryDate` in the past?**
If so, the article has been deliberately retired. Remove that line.

**6. Are you looking at an old copy?**
Press `Cmd + Shift + R` (Mac) or `Ctrl + F5` (Windows) to force the browser to
fetch a fresh copy. Or try the page on your phone, on mobile data.

---

## "The Actions tab shows a red cross"

The build failed. The live site is unaffected. Here is how to read the error.

1. Click the **Actions** tab.
2. Click the failed run (the one with the red cross).
3. Click **Build the website** in the left panel.
4. Click the step with the red cross to expand it.
5. Look at the **last ten lines**. The error is there.

### The errors you are actually likely to see

**`failed to unmarshal YAML` or `error parsing front matter`**

Something is wrong between the two `---` lines at the top of an article, or in
`data/scores.yaml`. The message names the file. Usually one of:

* A colon inside a value that is not in quotes:
  `title: Riverside: the inside story` ❌
  `title: "Riverside: the inside story"` ✅
* A tab used instead of spaces in `data/scores.yaml`
* A missing closing quote

**`REF_NOT_FOUND` or `page not found`**

A link points at an article that does not exist. Check the address you typed —
it should be a full path like `/posts/riverside-edge-kingsport/`, with a slash at
each end.

**`Error: module ... not found` or a Hugo version complaint**

The pinned Hugo version could not be downloaded, usually a temporary GitHub
glitch. Click **Re-run all jobs** on the failed run. If it fails twice, check
that `HUGO_VERSION` in `.github/workflows/deploy.yml` is a version that actually
exists at <https://github.com/gohugoio/hugo/releases>.

**`public/index.html is missing`**

One of the workflow's own safety checks caught something. Scroll further up the
log — the real error is above it.

### If you cannot work it out

Find the *last thing you changed* and undo it:

1. VS Code ▸ Source Control panel
2. Find the file next to the change
3. Click the **↩︎ Discard Changes** arrow beside it
4. Publish again

If it was already published, ask a developer, or copy the error message into a
search engine — Hugo's messages are well documented.

---

## "The preview will not start"

**`command not found: hugo`**

Hugo is not installed, or the Terminal cannot find it.
Run `hugo version`. If that fails too, reinstall — see
[docs/03](03-tools-and-dependencies.md#hugo). On Windows, close and reopen
VS Code after installing.

**`Error: listen tcp 127.0.0.1:1313: bind: address already in use`**

A preview is already running, probably in another Terminal tab. Either use that
one, or stop it: click into the Terminal panel and press `Ctrl + C`. Or run a
second one on a different port:

```bash
hugo server --port 1414
```

**The page loads but has no styling — just black text on white**

The stylesheet failed to build. Stop the preview (`Ctrl + C`), then:

```bash
hugo version
```

If it does not say **extended**, that is the cause. Install the extended
edition.

---

## "A picture is not showing"

In order of likelihood:

**1. Wrong path.** The file goes in `static/images/`, but the path you write
leaves `static` out:

| File on disk | What you write |
|--------------|----------------|
| `static/images/goal.jpg` | `/images/goal.jpg` |
| `static/images/2026/goal.jpg` | `/images/2026/goal.jpg` |

It must start with a `/`.

**2. Capital letters.** `Goal.JPG` and `goal.jpg` are different files as far as
the web server is concerned, even though they look the same on your Mac or
Windows machine — which is exactly why it works locally and fails when
published. Use lower case for every file name, always.

**3. Spaces in the name.** `team photo.jpg` breaks. Use `team-photo.jpg`.

**4. You forgot to publish the picture.** Adding an image to the folder is a
change like any other. Run **Publish everything** again.

---

## "The live scores disappeared"

**The whole strip is gone from the front page.** Two possible causes. Either
`hugo.toml` has `showLiveScores = false` — set it to `true` — or the
`featured_matches:` list at the top of `data/scores.yaml` is empty. The strip
shows only the matches listed there, and deliberately does not render at all
when none are chosen.

**A match is on `/scores/` but not on the front page.** That is the mechanism
working: add its `id` to `featured_matches:` to put it up.

**The scores have stopped updating.** Actions tab ▸ "Refresh live scores". A red
cross there means the provider was unreachable — the run deliberately writes
nothing in that case, so the site keeps showing the last good scores rather than
going blank. It will pick itself up on the next run. If every run for the last
few hours is red, the provider is having a bad day; you can still edit
`data/scores.yaml` by hand in the meantime.

**A score I typed in by hand disappeared.** The refresh rewrites the `sports:`
section every fifteen minutes. It never touches `featured_matches:`. If you want
to run the scores by hand permanently, disable the workflow: Actions tab ▸
"Refresh live scores" ▸ ⋯ ▸ Disable workflow.

**A picture has no credit under it.** Add `imageCredit` and `imageLicense` to
that article's front matter. Nothing appears if they are absent, which is what
you want for your own photography and not what you want for anybody else's.

**A sport or match is missing everywhere.** Its block was deleted or its
indentation is wrong. Open `data/scores.yaml` and compare it to a block that
does work — every line of a match must be indented exactly as far as the
equivalent line above it.

**The build failed after editing it.** That file is the most indentation-fussy
in the project. To get back to a working state:

1. VS Code ▸ Source Control
2. Find `data/scores.yaml`
3. Click **↩︎ Discard Changes**
4. Try again, changing one value at a time and previewing between changes

---

## "The website looks broken on my phone"

**First, check it is not just a cached copy.** In your phone's browser settings,
clear the cache, or open the site in a private/incognito tab.

**If it is genuinely broken**, note down:

* which phone and which browser
* which page
* what looks wrong — ideally a screenshot

The layout is built mobile-first and is checked for horizontal overflow at
320px, 390px, 768px, 1024px and 1920px, so a genuine break is most likely
caused by something in an article rather than by the site itself. The usual
culprits are:

* A very long word or URL pasted as plain text with no spaces
* A table with many columns — these scroll inside their own box by design;
  if one is pushing the page wide, it may have been pasted as raw HTML
* An image referenced by an external address that is very large

---

## "sportsone.world does not load"

**Wait first.** DNS changes take between 10 minutes and 24 hours. If you set it
up in the last day, that is the answer.

Then, in order:

**1. Does the GitHub address work?**
Try `https://yourname.github.io/sportsone-world/`. If that works, the website is
fine and the problem is purely the domain.

**2. Is the custom domain saved?**
Repository **Settings ▸ Pages ▸ Custom domain** should say `sportsone.world`.

**3. Are the DNS records right?**
Go to <https://dnschecker.org>, type `sportsone.world`, choose **A**. You should
see `185.199.108.153`, `.109.153`, `.110.153` and `.111.153`. If you see
something else, go back to GoDaddy and check
[docs/04](04-deployment-and-domain.md#2b--set-the-dns-records-at-godaddy) — most
often an old GoDaddy "parked" A record was not deleted.

**4. "Your connection is not private" / certificate warning.**
GitHub has not finished issuing the HTTPS certificate. Wait an hour. Then in
**Settings ▸ Pages**, untick and re-tick **Enforce HTTPS**.

---

## "VS Code will not publish"

**"Please make sure you configure your user.name and user.email in git"**

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**"Authentication failed" / it keeps asking for a password**

GitHub no longer accepts account passwords from Git. Sign in properly instead:
click the person icon at the bottom-left of VS Code ▸ **Sign in with GitHub**.

**"Updates were rejected because the remote contains work that you do not have
locally"**

Someone (or you, on another computer) changed things on GitHub. Run
**Terminal ▸ Run Task… ▸ 5 · Get the latest changes from GitHub**, then publish
again.

**"You have divergent branches"**

Run once:

```bash
git config --global pull.rebase true
```

Then try again.

---

## "I deleted something by accident"

**Not published yet:** VS Code ▸ Source Control ▸ find the file ▸ **↩︎ Discard
Changes**. It comes straight back.

**Already published:** it is still in the history.

1. Go to the repository on GitHub
2. Click **Commits** (the clock icon above the file list)
3. Find the commit where you deleted it
4. Click the commit, then the **…** menu ▸ **Revert**

Or ask a developer for `git revert` — it takes them thirty seconds.

---

## "Everything is confusing and I want to start this afternoon over"

If you have not published yet, this throws away all your uncommitted changes and
returns to the last published state:

```bash
git reset --hard
git clean -fd
```

⚠️ This deletes work you have not published. Only run it when that is what you
want.

---

## Getting help

When asking anyone — a developer, a forum, an AI assistant — include:

1. **What you were trying to do**
2. **What you clicked or ran**
3. **The exact error message**, copied as text, not described
4. **A screenshot** of the Actions log if the build failed

That turns a twenty-minute conversation into a two-minute one.

**Useful places**

* Hugo documentation — <https://gohugo.io/documentation/>
* Hugo forum, friendly and fast — <https://discourse.gohugo.io/>
* GitHub Pages documentation — <https://docs.github.com/en/pages>
* GitHub Actions status, when things break for everyone at once —
  <https://www.githubstatus.com/>

---

## A monthly two-minute check

* Open the site on a phone and a laptop. Does the homepage look right?
* Click the newest article. Does the picture load?
* Actions tab: were the last few runs green?
* Are the live scores in `data/scores.yaml` still current, or stale?
