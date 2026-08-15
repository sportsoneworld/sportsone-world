# Distribution — moving SportsOne to a Windows laptop

Everything needed to take this zip from Google Drive to a working site on
Windows. Written to be followed start to finish without prior knowledge.

If you only want to look at the finished website: **[Step 4, Route A](#route-a--just-look-at-the-website)**.

---

## 1 · What is in the zip

One folder, `sportsone-world`, containing both the finished website and the
source it was built from.

| Folder | What it is | Do you touch it? |
|--------|-----------|------------------|
| **`public/`** | **The finished website.** 251 pages of plain HTML, one CSS file, one JavaScript file, the fonts, icons and photography. This is what you upload to a web host. | Never edit by hand — it is regenerated |
| `content/` | Your articles, as plain text files. 29 stories plus the About, Contact, Terms, Privacy and Accessibility pages | Yes — this is where you write |
| `data/` | The editorial controls: what leads the front page, each sport's top stories, the live scores, the navigation, the videos | Yes |
| `static/` | Pictures, fonts, favicons. 29 photographs under `static/images/photos/` | Yes — put new pictures here |
| `layouts/` | Page templates | Rarely |
| `assets/` | The stylesheet (10 files) and the JavaScript (2 files) | Only to change the design |
| `docs/` | Seven guides, written for a non-technical reader | Read |
| `scripts/` | `fetch-scores.py`, which refreshes live scores | No |
| `archetypes/` | The template used when you create a new article | No |
| `.github/` | The two automations: publish on push, refresh scores every 15 minutes | No |
| `.vscode/` | One-click tasks so you never have to type a command | No |

Plus three double-click launchers at the top level — `View-Website.bat`,
`Edit-Website.bat`, `Build-Website.bat` — explained in Step 4.

**Numbers, so you can confirm nothing was lost in transit:**

| | |
|---|---|
| Total files | 603 |
| Source files (everything except `public/`) | 193 |
| Built pages in `public/` | 251 |
| Articles | 29 |
| Photographs | 29 |
| Videos referenced | 12 |
| Unzipped size | ~24 MB |
| Zip size | 21 MB |

---

## 2 · Uploading to Google Drive (on the Mac)

1. Open **Google Drive** in a browser, or the Drive app.
2. Drag `sportsone-world.zip` in. At **21 MB** it uploads in seconds and is far
   below any Drive limit.
3. **Do not let Drive unzip it.** If you use the Drive *app* and drop the
   *folder* rather than the zip, Drive syncs 603 separate files, which is slow
   and loses the file permissions. Upload the **zip**, as one file.
4. Share it with yourself, or download it directly on the Windows laptop while
   signed in to the same account.

**Google Drive will warn that it "can't scan this file for viruses"** on
download, or offer "Download anyway". That message appears for every zip over a
few megabytes. It is not a warning about the contents.

---

## 3 · Unzipping on Windows — read this part

Three things go wrong here, and all three are avoidable.

### 3.1 Unblock the zip BEFORE you extract it

Windows tags every file downloaded from the internet with a hidden marker
("Mark of the Web"). If you extract first, **every one of the 603 files carries
that marker**, and Windows will query the `.bat` launchers each time you run
them.

Clear it once, on the zip, and every extracted file comes out clean:

1. Right-click `sportsone-world.zip` → **Properties**
2. At the bottom of the **General** tab, tick **Unblock** (it only appears if
   the marker is present)
3. **Apply** → **OK**
4. *Now* extract

### 3.2 Extract to a short path

Right-click the zip → **Extract All…** and choose somewhere short, such as:

```
C:\Users\<your-name>\Documents\
```

giving you `C:\Users\<your-name>\Documents\sportsone-world\`.

The longest path inside the project is 93 characters. Windows' classic limit is
260. Extracting into `Documents` leaves plenty of room; extracting into
something like `C:\Users\name\OneDrive\Desktop\New folder (2)\Sports website
final\` does not, and you will get "path too long" errors on files you then
cannot delete.

**Avoid a OneDrive-synced folder** for this. OneDrive's "files on demand"
turns files into placeholders that Hugo cannot read, and you get build errors
that look like missing files.

### 3.3 Use Windows' own extractor, or 7-Zip

The built-in **Extract All…** is fine. So is [7-Zip](https://www.7-zip.org/).
Avoid unzipping inside the Google Drive web preview — it extracts a partial
copy.

### 3.4 Check it arrived whole

Open the extracted folder. You should see, at the top level:

```
archetypes  assets  content  data  docs  layouts  public  scripts  static
hugo.toml   README.md   DISTRIBUTION.md
View-Website.bat   Edit-Website.bat   Build-Website.bat
```

Then confirm the counts from Step 1. In **PowerShell**, from inside the folder:

```powershell
(Get-ChildItem -Recurse -File).Count                       # expect 603
(Get-ChildItem public -Recurse -Filter *.html).Count       # expect 251
(Get-ChildItem static\images\photos -Filter *.jpg).Count   # expect 29
```

If the first number is far below 603, the extraction stopped early — usually
Step 3.2. Delete the folder and extract again to a shorter path.

---

## 4 · Running it

### Route A — just look at the website

**Double-click `View-Website.bat`.**

It starts a small web server and opens `http://localhost:1313`. Leave the black
window open while you browse; press **Ctrl+C** in it, or just close it, to stop.

It needs either Hugo or Python on the machine. If it finds neither it tells you
exactly what to install. See Step 5.

> **Why you cannot just double-click `public\index.html`**
>
> Every address inside the site starts with a slash — `/css/…`, `/images/…`,
> `/categories/cricket/`. That is correct for a website served from a web root,
> and it is what makes the folder uploadable to any host unchanged.
>
> A browser opening a file straight from disk has no web root to resolve those
> against. It looks for `C:\css\…`, finds nothing, and renders the page as raw
> unstyled HTML — enormous text, giant icons, no layout. **The site is not
> broken when this happens.** It is being opened the wrong way. Use the `.bat`.

### Route B — write and preview

**Double-click `Edit-Website.bat`.** Requires Hugo (Step 5).

Hugo watches the folder. Edit any file under `content\` and the browser
refreshes the instant you save. This is the mode you write in day to day —
see [docs/02](docs/02-publishing-and-managing-articles.md).

### Route C — rebuild the finished site

**Double-click `Build-Website.bat`.** Requires Hugo.

Regenerates `public\` from the current source, with the live address
`https://sportsone.world/` baked in. Run this after you have written something
and want an updated folder to upload.

If you host somewhere other than sportsone.world, change the address inside
`Build-Website.bat`, and `baseURL` at the top of `hugo.toml`.

---

## 5 · What to install on Windows

Nothing at all is needed to *read* the source files. To preview or rebuild, you
need Hugo. There is **no Node.js, no npm, no package.json and no dependency
tree** in this project by design — Hugo is one self-contained program.

| Software | Version | Needed for |
|----------|---------|-----------|
| **Hugo, extended edition** | **0.165.0 or higher, and it must say `extended`** | Previewing and rebuilding |
| Git | 2.30+ | Publishing through GitHub (optional) |
| VS Code | Latest | Writing (optional but recommended) |
| Python | 3.10+ | Only as an alternative to Hugo for Route A |

Open **Terminal** or **PowerShell** and run:

```powershell
winget install Hugo.Hugo.Extended
winget install Git.Git
winget install Microsoft.VisualStudioCode
```

**Close the window and open a new one**, then check:

```powershell
hugo version
```

The output **must contain the word `extended`**. If it does not, this project's
stylesheet will not compile:

```powershell
winget uninstall Hugo.Hugo
winget install Hugo.Hugo.Extended
```

If `winget` is not recognised, install **App Installer** from the Microsoft
Store, then reopen the terminal.

Full detail, including the PowerShell 7 requirement for the VS Code one-click
tasks: [docs/07](docs/07-moving-to-a-windows-laptop.md).

---

## 6 · Putting the site online

You have two routes, and they are not exclusive.

### Through GitHub Pages — automatic, recommended

Already configured. `.github/workflows/deploy.yml` builds and publishes on every
push to `main`; `.github/workflows/scores.yml` refreshes live scores every 15
minutes and commits the change, which triggers a publish.

Set up once by following [docs/01](docs/01-setup-vs-code-and-github.md) and
[docs/04](docs/04-deployment-and-domain.md). After that, publishing is: save,
commit, push. Two minutes later it is live.

### By uploading `public/` — manual, works anywhere

Run `Build-Website.bat`, then upload **the contents** of `public\` — not the
folder itself — to your host's web root. Works with any static host: Netlify,
Cloudflare Pages, cPanel, S3, plain FTP.

Two rules:

- Upload the **contents**, so `index.html` sits at the root. If you upload the
  folder you get `yoursite.com/public/`.
- Nothing on the server needs to run. There is no PHP, no database, no Node.
  Any host that serves files will do.

---

## 7 · Before the site is genuinely public

Four things are still placeholders. They are deliberate — I could not invent
them for you.

| Where | What to change |
|-------|----------------|
| `hugo.toml`, `[params.social]` | The X and Instagram URLs are placeholders. Confirm the real accounts or blank the lines to hide the icons. |
| `content/contact.md` | Add a real newsroom email, a tips route, and the editor responsible for complaints. |
| `content/terms.md` | Add your publishing entity and jurisdiction. |
| Article bylines | The 29 starter articles carry placeholder writer names. Change them before publishing under them. |

The 29 starter articles are **real, factual pieces** about real events, there to
show the site working with genuine copy. Delete them when your own reporting
replaces them — the command is in [README.md](README.md#the-starter-articles).

Every photograph is freely licensed (public domain, CC0, CC BY or CC BY-SA),
credited beneath the picture and listed at `/credits/`. If you delete the
articles, delete `static/images/photos/` too.

---

## 8 · Troubleshooting

**The page has no styling — huge text, giant icons, no layout.**
You opened `public\index.html` directly. Close it and use `View-Website.bat`.
See the box in Step 4. This is by far the most common one.

**`hugo` is not recognised as a command.**
Either it is not installed, or the terminal was open before you installed it.
Close every terminal window, open a new one, try `hugo version` again.

**`hugo version` does not say `extended`.**
Reinstall — Step 5. The plain edition cannot compile this stylesheet, and the
error it gives ("this feature is not available in your current Hugo version")
does not make that obvious.

**"The system cannot find the path specified" when running a `.bat`.**
The launcher must stay in the top-level folder, next to `hugo.toml`. Do not move
the `.bat` files to the desktop — they locate the project relative to
themselves.

**Windows SmartScreen warns about the `.bat` file.**
You skipped Step 3.1. Either unblock the zip and extract again, or right-click
the `.bat` → Properties → Unblock. The files are three short text scripts; you
can open them in Notepad and read every line.

**The build fails after I edited a data file.**
Almost always indentation in a `.yaml` file — two spaces, never a tab. The build
failing is the safety net working: nothing is published and the live site does
not change. See [docs/05](docs/05-troubleshooting.md).

**Live scores are stale or empty.**
They refresh through GitHub Actions, which only runs once the project is on
GitHub. Until then `data/scores.yaml` holds whatever was last fetched. You can
refresh manually with `python3 scripts/fetch-scores.py`, or edit the file by
hand. See [docs/02](docs/02-publishing-and-managing-articles.md).

**Port 1313 is already in use.**
Something else is on it — often a previous run you closed the browser on but not
the black window. Close the other window, or edit the `.bat` and change `1313`
to `1314`.

**A file will not delete: "path too long".**
Step 3.2. Move the whole folder somewhere short first, then delete.

---

## 9 · Two things I could not test

Stated plainly rather than discovered by you:

1. **The three `.bat` files have not been run on Windows.** They were written on
   a Mac, which has no way to execute them. The logic is simple — find Hugo or
   Python, start a server, open a browser — and each one prints what it is doing
   before it does it. Every command they run is also given in this document, so
   if a launcher misbehaves you can do the same thing by hand:

   ```powershell
   cd path\to\sportsone-world\public
   py -m http.server 1313
   ```

   ```powershell
   cd path\to\sportsone-world
   hugo server --port 1313
   ```

2. **The GitHub Actions workflows have not run for real.** They are correct as
   written and the build steps were verified locally, but neither has executed
   on GitHub yet, because the project is not yet in a repository. The first push
   will tell you — a green tick or a red cross on the Actions tab.

---

## 10 · Rebuilding this zip

From the Mac, with the dev server stopped:

```bash
cd ~/Downloads/sportsone-world
rm -rf public resources .hugo_build.lock
find . -name ".DS_Store" -delete
HUGO_ENVIRONMENT=production hugo --minify --gc --cleanDestinationDir \
  --baseURL "https://sportsone.world/"
rm -f .hugo_build.lock && rm -rf resources
cd .. && zip -r -X sportsone-world.zip sportsone-world \
  -x "*.DS_Store" -x "*/.hugo_build.lock" -x "*/resources/*" -x "*/.claude/*"
```

`-X` is the important flag: it stops macOS writing its resource-fork files into
the archive, which is what produces a stray `__MACOSX` folder and a pile of
`._filename` files when the zip is opened on Windows.
