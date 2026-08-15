# 1 · Setting up your computer and connecting VS Code to GitHub

**Who this is for:** someone who has never used a code editor before.
**How long it takes:** about 45 minutes, once, ever.
**What you need:** a computer, an internet connection, and an email address.

Read it in order. Do not skip a step. Every time you see a box like this:

```bash
something to type
```

…it means: open the black window (the Terminal) and type that line, then press
Enter. Instructions for opening the Terminal are in Step 0.

> **The videos linked in this guide are YouTube searches, not specific
> videos.** Clicking one opens a results page with several current tutorials.
> That is deliberate — individual videos get deleted or go out of date, search
> results do not.

---

## Step 0 · Meet the Terminal

You will use this about four times in total, and after that almost never.

**On a Mac**
Press `Cmd + Space`, type `Terminal`, press Enter. A white or black window
opens with a blinking cursor. That is it.

**On Windows**
Press the Windows key, type `Terminal`, press Enter. (On older Windows, type
`PowerShell` instead.)

Nothing you type there can break your computer. If a command looks like it has
hung, press `Ctrl + C` to stop it.

---

## Step 1 · Create a GitHub account

GitHub is where your articles live and where the website is published from.
It is free.

1. Go to <https://github.com/signup>
2. Use an email address you will keep.
3. Pick a username you are happy to have in a web address — for example
   `sportsone-world`.
4. Verify the email GitHub sends you.
5. **Turn on two-factor authentication** when GitHub prompts you. GitHub now
   requires it. Use the "authenticator app" option and install
   Google Authenticator or Microsoft Authenticator on your phone.
   Save the recovery codes GitHub shows you somewhere safe — a password
   manager, or printed and put in a drawer. You will need them if you lose
   your phone.

📺 [Search: "how to create a GitHub account 2025"](https://www.youtube.com/results?search_query=how+to+create+a+github+account+2025)

---

## Step 2 · Install Git

Git is the thing that actually sends your articles to GitHub. You will never
have to understand it — VS Code drives it for you — but it must be installed.

**Mac**

Type this and press Enter:

```bash
git --version
```

* If it prints something like `git version 2.39.5`, Git is already installed.
  Move on to Step 3.
* If a window pops up offering to install "command line developer tools", click
  **Install** and wait. That is Git.

**Windows**

1. Go to <https://git-scm.com/download/win> — the download starts by itself.
2. Run the installer.
3. Click **Next** on every screen. The defaults are correct. Do not change
   anything.
4. Click **Install**, then **Finish**.

📺 [Search: "install git windows"](https://www.youtube.com/results?search_query=install+git+windows+beginner)

---

## Step 3 · Install VS Code

VS Code is the program you will actually write in. It is free and made by
Microsoft.

1. Go to <https://code.visualstudio.com/>
2. The big blue button already knows whether you are on Mac or Windows. Click it.
3. **Mac:** the download is a `.zip`. Double-click it, then drag the blue
   **Visual Studio Code** icon into your **Applications** folder.
   **Windows:** run the `.exe`. On the "Select Additional Tasks" screen, tick
   **"Add to PATH"** — this matters. Then click through to Install.
4. Open VS Code.

📺 [Search: "install visual studio code beginner"](https://www.youtube.com/results?search_query=install+visual+studio+code+beginner+tutorial)

---

## Step 4 · Install Hugo

Hugo is the engine that turns your Markdown into the website. You need it only
so you can *preview* the site on your own computer — GitHub installs its own
copy when it publishes.

**Mac**

The easiest route is Homebrew. If you do not have Homebrew, paste this whole
line into the Terminal and press Enter, then follow its prompts (it will ask for
your Mac password — typing it shows nothing on screen, that is normal):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

When it finishes, it prints two or three lines beginning with `eval` — run those
exactly as printed. Then:

```bash
brew install hugo
```

**Windows**

Open Terminal and run:

```bash
winget install Hugo.Hugo.Extended
```

If `winget` is not recognised, install it from the Microsoft Store
("App Installer"), close the Terminal, open it again and retry.

**Check it worked — both platforms**

```bash
hugo version
```

You should see something containing `v0.165` (or higher) **and the word
`extended`**. If you do not see `extended`, uninstall and install the extended
version — the plain version cannot build this site's stylesheet.

📺 [Search: "install hugo static site generator"](https://www.youtube.com/results?search_query=install+hugo+static+site+generator)

---

## Step 5 · Put this project on GitHub

You currently have this project as a folder on your computer. It needs to live
on GitHub.

### 5a · Create the empty repository

1. Go to <https://github.com/new>
2. **Repository name:** `sportsone-world`
3. **Description:** `SportsOne.world — sports news publishing platform`
4. Choose **Private** for now. You can make it public later; the *website* is
   public either way.
5. **Do not tick** "Add a README file", "Add .gitignore" or "Choose a licence".
   The project already has them and ticking these causes a conflict.
6. Click **Create repository**.
7. Leave that page open. You need the address it shows, which looks like
   `https://github.com/yourname/sportsone-world.git`

### 5b · Open the project in VS Code

1. Open VS Code.
2. **File ▸ Open Folder…**
3. Select the `sportsone-world` folder and click Open.
4. If VS Code asks *"Do you trust the authors of the files in this folder?"* —
   click **Yes, I trust the authors**.
5. A box appears in the bottom-right offering to install recommended
   extensions. Click **Install All**. This takes a minute and you only do it
   once.

### 5c · Sign in to GitHub from VS Code

1. Click the round person icon at the very bottom-left of VS Code.
2. Choose **Sign in with GitHub to use GitHub Pull Requests**.
3. Your browser opens. Click **Continue** and then **Authorize**.
4. The browser asks to reopen VS Code. Allow it.

You are now signed in. VS Code will handle passwords from here on.

### 5d · Send the project up for the first time

1. Click the **Source Control** icon in the left sidebar — it looks like a small
   branching line, third from the top.
2. Click **Initialize Repository**.
3. In the message box at the top, type `Initial commit`.
4. Click the blue **Commit** button. If it asks "there are no staged changes,
   commit all?" click **Yes**.
5. Click **Publish Branch**.
6. VS Code asks where to publish. Choose the `sportsone-world` repository you
   created, or paste its address.

Refresh your GitHub page in the browser. All your files are there.

> **If VS Code complains "Make sure you configure your user.name and
> user.email in git"**, run these two lines in the Terminal, using your own
> name and the email address on your GitHub account, then try again:
>
> ```bash
> git config --global user.name "Your Name"
> git config --global user.email "you@example.com"
> ```

---

## Step 6 · See the website on your own computer

In VS Code:

1. Menu: **Terminal ▸ Run Task…**
2. Choose **1 · Preview the website**
3. Wait for the message `Web Server is available at http://localhost:1313/`
4. Hold `Cmd` (Mac) or `Ctrl` (Windows) and click that address.

Your browser opens the full site. Leave this running while you write — every
time you save a file, the browser updates by itself within a second.

To stop it, click into the Terminal panel and press `Ctrl + C`.

---

## Step 7 · Switch the website on

Follow [docs/04-deployment-and-domain.md](04-deployment-and-domain.md). It takes
about ten minutes and you do it once.

---

## You are done

From now on your entire job is:

1. **Terminal ▸ Run Task ▸ 2 · New article**
2. Write it
3. **Terminal ▸ Run Task ▸ 3 · Publish everything**

That is the whole system. The next guide,
[docs/02-publishing-and-managing-articles.md](02-publishing-and-managing-articles.md),
covers it in detail.

---

## Optional: using a second computer

Do steps 2, 3 and 4 on the new machine, then instead of Step 5:

```bash
git clone https://github.com/yourname/sportsone-world.git
cd sportsone-world
hugo server
```

Before you start writing on either machine, run
**Terminal ▸ Run Task ▸ 5 · Get the latest changes from GitHub** so the two
computers do not disagree with each other.
