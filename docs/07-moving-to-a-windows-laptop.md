# 7 · Moving the project to a Windows laptop

**Who this is for:** you, right now — the project is on a Mac and needs to be on
a Windows laptop, from which you will take it live.
**How long it takes:** about 40 minutes, most of it installing software.
**What you need:** both computers, and a GitHub account.

This guide covers the *move*. Once the project is on the Windows machine, the
normal guides take over: [docs/01](01-setup-vs-code-and-github.md) for the
GitHub connection, [docs/04](04-deployment-and-domain.md) for going live.

---

## The short version

There are two ways to move it. **Route A puts it on GitHub from the Mac and
downloads it on Windows.** Route B compresses the folder and sends it through
Google Drive.

Route A is better and it is not close — you need the project on GitHub anyway
before anything can be published, so Route B is the same work plus a zip file
in the middle. But Route B is perfectly safe if you prefer it, and both are
written out below.

Either way, one thing must not travel with the project: the **`public/`
folder**. Why is explained in the next section, and it matters more than it
sounds.

---

## `public/` now travels with the project

**This section changed.** It used to tell you to leave `public/` behind, and
that was right at the time: the copy on the Mac had been made by `hugo server`,
so every address inside it — sitemap, robots file, RSS feeds, canonical tags —
was baked as `http://localhost:1313`.

That is no longer the case. `public/` is now a proper production build made with
`--baseURL https://sportsone.world/`, and it is included in the distribution zip
on purpose, as the ready-to-upload website. Verified: **zero** files in it
mention localhost.

You still never edit it by hand, and it is still in `.gitignore` — GitHub
Actions rebuilds it on every push, so a copy committed to the repository would
only go stale. It ships in the zip because a zip is not a repository: it is how
you get a working site onto a machine that has nothing installed yet.

The full picture, including how to run it on Windows:
[DISTRIBUTION.md](../DISTRIBUTION.md).

The other thing to leave behind is the Mac's own litter: `.DS_Store` files. The
zip command in DISTRIBUTION.md excludes them.

---

## Route A · Through GitHub (recommended)

This project is **not yet a Git repository** — nothing has been committed. So
the first step is the same one you would have to do eventually anyway.

### On the Mac

```bash
cd /Users/dipayandhar/Downloads/sportsone-world
find . -name '.DS_Store' -delete
git init -b main
git add .
git commit -m "Initial commit: SportsOne.world"
```

Now create the repository on GitHub and push to it. Follow
[docs/01, Step 5a](01-setup-vs-code-and-github.md) to create the empty
repository — name it `sportsone-world`, **Private**, and tick nothing — then:

```bash
git remote add origin https://github.com/YOURNAME/sportsone-world.git
git push -u origin main
```

Replace `YOURNAME` with your GitHub username. If it asks for a password, use a
Personal Access Token, not your account password — or install the GitHub CLI
(`brew install gh`, then `gh auth login`) which handles it for you.

### On the Windows laptop

Install the software in the next section first, then:

```powershell
mkdir C:\dev
cd C:\dev
git clone https://github.com/YOURNAME/sportsone-world.git
cd sportsone-world
hugo server
```

Done. `.gitignore` left `public/` behind for you, the `.github` and `.vscode`
folders came across intact, and you already have version history.

---

## Route B · Zip file through Google Drive

Google Drive is completely fine for this. Without `public/` the project is about
**1.4 MB across 148 files** — a rounding error to Drive. The only real risks are
losing hidden folders and accidentally including `public/`, and the commands
below prevent both.

### Step 1 · Package it on the Mac

**Do not use Finder's right-click ▸ Compress.** It will include `public/` and
every `.DS_Store`. Use the Terminal:

```bash
cd /Users/dipayandhar/Downloads

rsync -a \
  --exclude 'public/' \
  --exclude 'resources/_gen/' \
  --exclude '.hugo_build.lock' \
  --exclude '.DS_Store' \
  sportsone-world/ /tmp/sportsone-world/

cd /tmp
zip -r ~/Desktop/sportsone-world.zip sportsone-world -x "*.DS_Store"
```

### Step 2 · Check the package before you send it

This is the step people skip and then regret. You are confirming the two hidden
folders survived — without them you have no publishing pipeline and no one-click
tasks:

```bash
unzip -l ~/Desktop/sportsone-world.zip | grep -E "\.github/workflows|\.vscode/tasks|hugo\.toml|static/CNAME"
```

You must see all four lines. Then confirm the size and that `public/` stayed
out:

```bash
ls -lh ~/Desktop/sportsone-world.zip                    # expect roughly 1–2 MB
unzip -l ~/Desktop/sportsone-world.zip | grep -c "public/"   # must print 0
```

If the zip is 4 MB or more, `public/` got in. Delete it and run Step 1 again.

### Step 3 · Send it

Upload `sportsone-world.zip` to Google Drive, share it with yourself, download
it on the Windows laptop.

### Step 4 · Unpack it on Windows — two traps

**Trap 1 · Unblock the file first.** Windows marks anything downloaded from the
internet, and tools then refuse to run files extracted from it. Right-click
`sportsone-world.zip` ▸ **Properties** ▸ tick **Unblock** ▸ **Apply**. Then
extract.

**Trap 2 · You cannot see the folders that matter.** File Explorer hides
`.github` and `.vscode` by default, so it will look like they did not survive.
Turn them on: Explorer ▸ **View** ▸ **Show** ▸ **Hidden items**.

Extract to **`C:\dev\sportsone-world`** — a short path, not somewhere deep under
`Downloads`. Then verify in PowerShell:

```powershell
cd C:\dev\sportsone-world
Get-ChildItem -Force | Select-Object Name
```

You should see `.github`, `.vscode`, `.editorconfig` and `.gitignore` in the
list alongside `content`, `layouts` and `hugo.toml`.

### Step 5 · Then put it on GitHub anyway

You still need the project on GitHub before anything can publish. Follow
[docs/01, Step 5](01-setup-vs-code-and-github.md) from the Windows machine.
(This is why Route A is fewer steps: it does this part first instead of last.)

---

## Other ways to move it

| Method | When it makes sense |
|--------|---------------------|
| **USB stick / external drive** | No internet needed. Format it **exFAT** so both machines can read and write. Same exclusions as Route B. |
| **OneDrive / Dropbox** | Same as Google Drive. If the Windows laptop already syncs OneDrive, the file simply appears — no download step. |
| **WeTransfer** | One-off, no account needed on either end. |
| **AirDrop** | Not an option — AirDrop is Apple-only. |

---

## What to install on Windows

Four things. Note what is *not* on this list: **no Node.js, no npm, no
package.json, no dependency tree.** This project has none, by design — see
[docs/03](03-tools-and-dependencies.md). Hugo is a single self-contained
program.

| Software | Version | Why you need it |
|----------|---------|-----------------|
| **Hugo, extended edition** | **0.165.0 or higher** — must say `extended` | Builds the site. The plain edition **cannot** compile this project's stylesheet. |
| **Git** | 2.30 or higher | Sends your work to GitHub. VS Code drives it for you. |
| **VS Code** | Latest | Where you write. |
| **PowerShell 7** | 7.4 or higher | **Required for the one-click tasks** — see the warning below. |

### The fast way — winget

`winget` is built into Windows 10 (1809+) and Windows 11. Open **Terminal** or
**PowerShell** and run these four lines:

```powershell
winget install Hugo.Hugo.Extended
winget install Git.Git
winget install Microsoft.VisualStudioCode
winget install Microsoft.PowerShell
```

If `winget` is not recognised, install **App Installer** from the Microsoft
Store, close the Terminal, reopen it and try again.

**Close and reopen the Terminal afterwards**, so it picks up the new programs,
then check all four:

```powershell
hugo version      # must contain v0.165 or higher AND the word "extended"
git --version     # 2.30 or higher
code --version
$PSVersionTable.PSVersion   # 7.4 or higher
```

The Hugo check is the one to read carefully. If the word `extended` is missing,
run `winget uninstall Hugo.Hugo` and install `Hugo.Hugo.Extended` again.

### The manual way

If you would rather use installers, [docs/01, Steps 2–4](01-setup-vs-code-and-github.md)
walks through Git, VS Code and Hugo screen by screen. Two notes for Windows:

- **VS Code installer:** on the "Select Additional Tasks" screen, tick
  **"Add to PATH"**.
- **PowerShell 7** is a separate download from
  <https://github.com/PowerShell/PowerShell/releases> — it is not the
  "Windows PowerShell" already on your machine.

### ⚠️ Why PowerShell 7 is not optional

The Windows PowerShell that ships with Windows is version **5.1**, and it does
not understand `&&` — the symbol that chains two commands together. Three of
this project's five one-click tasks use it:

| Task | Uses `&&`? |
|------|-----------|
| 1 · Preview the website | No — works either way |
| 2 · New article | **Yes** |
| 3 · Publish everything | **Yes** |
| 4 · Test the production build | **Yes** |
| 5 · Get the latest changes | No — works either way |

On a stock Windows machine those three fail immediately with
`The token '&&' is not a valid statement separator in this version`. Publishing
is Task 3, so this would stop you on day one.

Installing PowerShell 7 fixes all three, because PowerShell 7 does understand
`&&`. After installing it, make VS Code use it: press `Ctrl + Shift + P`, type
**Terminal: Select Default Profile**, and choose **PowerShell** (the one at
`C:\Program Files\PowerShell\7\pwsh.exe`, not `Windows PowerShell`).

> There is a second, more permanent fix: adding Windows-specific versions of
> those three commands to `.vscode/tasks.json`, so they work on any Windows
> machine with no extra install. It is a small, safe change to one file. Ask
> and it can be done.

### VS Code extensions

Do not install these by hand. Open the project folder in VS Code and it will
offer the whole list — click **Install All**. The list lives in
`.vscode/extensions.json` and is explained in
[docs/03](03-tools-and-dependencies.md).

---

## First run on Windows

```powershell
cd C:\dev\sportsone-world
hugo server
```

Open <http://localhost:1313>.

**Windows Firewall will pop up** the first time asking whether to allow Hugo to
accept connections. **Private networks** is enough — you do not need to tick
Public.

Then confirm the real build works, exactly as GitHub will run it:

```powershell
hugo --minify --gc --cleanDestinationDir --printPathWarnings
```

It should finish in a couple of seconds with no errors and report the number of
pages built. That command recreates `public/` locally — which is fine and
expected on your own machine. It stays out of Git either way.

### Checklist before you move on

| Check | Expected |
|-------|----------|
| `hugo version` | says `extended` |
| `hugo server` | site loads at localhost:1313, pictures and all |
| **Terminal ▸ Run Task ▸ 1** | preview starts |
| **Terminal ▸ Run Task ▸ 4** | prints `BUILD OK — no errors.` |
| `static/CNAME` | contains `sportsone.world` |
| `.github/workflows/deploy.yml` | present |

Task 4 passing is the meaningful one: it proves your Windows machine builds the
site the same way GitHub will.

---

## Taking it live

Everything from here is already documented and unchanged by the move:

1. **Connect VS Code to GitHub** — [docs/01, Steps 5–6](01-setup-vs-code-and-github.md)
2. **Turn on GitHub Pages and point the domain at it** —
   [docs/04](04-deployment-and-domain.md). The one step everybody gets wrong is
   setting **Settings ▸ Pages ▸ Source** to **GitHub Actions**, not "Deploy from
   a branch".
3. **Publish** — **Terminal ▸ Run Task ▸ 3 · Publish everything**. Live in about
   two minutes.

Two things are already prepared for you: `static/CNAME` holds `sportsone.world`,
and the workflow pins **Hugo 0.165.0 extended** so GitHub builds with a known
version regardless of what you have installed locally.

One note on cost, from [docs/04](04-deployment-and-domain.md): GitHub Pages is
free for **public** repositories. If you keep the repository private you need a
paid GitHub plan to publish from it. Starting private and switching to public
before launch is the usual answer.

---

## Before the site is genuinely public

Carried over from the README, and still outstanding:

- **The sixteen sample articles are placeholder content** — invented teams,
  players and results. Delete them before launch; the README has the exact
  command under "The sample articles".
- **Check `hugo.toml`** for anything still pointing at a placeholder — social
  handles and the author details in particular.

---

## If something goes wrong

[docs/05-troubleshooting.md](05-troubleshooting.md) covers the usual failures.
The three most likely on a *newly moved* machine:

| Symptom | Cause |
|---------|-------|
| `hugo: command not found` | Terminal opened before Hugo was installed. Close it and open a new one. |
| `TOCSS ... this feature is not available in your current Hugo version` | You have plain Hugo, not extended. Reinstall `Hugo.Hugo.Extended`. |
| `The token '&&' is not a valid statement separator` | PowerShell 5.1. Install PowerShell 7 — see above. |
