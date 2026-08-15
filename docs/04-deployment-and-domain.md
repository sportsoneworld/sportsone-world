# 4 · Switching the website on, and pointing sportsone.world at it

You do this once. Budget half an hour, plus waiting time for the domain.

There are three parts:

1. Turn on GitHub Pages (5 minutes)
2. Point the GoDaddy domain at GitHub (10 minutes, then up to 24 hours of waiting)
3. Turn on HTTPS (2 minutes, after the waiting)

---

## Part 1 · Turn on GitHub Pages

1. Go to your repository on GitHub.
2. Click **Settings** (the tab along the top, on the right).
3. In the left sidebar, click **Pages**.
4. Under **Build and deployment ▸ Source**, choose **GitHub Actions**.
   *Not* "Deploy from a branch". This is the single most common mistake.
5. There is nothing to save — it applies immediately.

### Run the first build

1. Click the **Actions** tab.
2. In the left sidebar click **Build and deploy to GitHub Pages**.
3. Click **Run workflow ▸ Run workflow**.
4. Wait. A yellow dot means it is working; a green tick means it is done.
5. Go back to **Settings ▸ Pages**. At the top it now shows an address like
   `https://yourname.github.io/sportsone-world/`. Click it.

Your website is live. It is on a GitHub address for now; the next part moves it
to your own domain.

> If the run has a red cross instead, open
> [docs/05-troubleshooting.md](05-troubleshooting.md) — the section
> "The Actions tab shows a red cross".

---

## Part 2 · Point sportsone.world at GitHub

### 2a · Tell GitHub about the domain

1. **Settings ▸ Pages**
2. Under **Custom domain**, type `sportsone.world` (no `www`, no `https://`).
3. Click **Save**.

GitHub will show a warning about DNS. That is expected — you have not set it up
yet. That is the next step.

> The repository already contains `static/CNAME` with `sportsone.world` in it,
> which keeps the setting from being wiped by future deployments. Do not delete
> that file.

### 2b · Set the DNS records at GoDaddy

1. Sign in at <https://dcc.godaddy.com/control/portfolio>
2. Find **sportsone.world** and click it.
3. Click **DNS** (or **Manage DNS**).

You are now looking at a table of records. You need to make it contain exactly
these.

**First, delete what is in the way.** GoDaddy adds two records to every new
domain that will conflict:

* Any **A** record where Name is `@` — delete it (it is usually a "parked" page)
* Any **CNAME** record where Name is `www` — delete it

Use the pencil/bin icon at the end of each row.

**Then add four A records.** Click **Add New Record** for each one:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `@` | `185.199.108.153` | 1 Hour |
| A | `@` | `185.199.109.153` | 1 Hour |
| A | `@` | `185.199.110.153` | 1 Hour |
| A | `@` | `185.199.111.153` | 1 Hour |

**Then add one CNAME record**, so `www.sportsone.world` works too:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | `www` | `yourname.github.io` | 1 Hour |

Replace `yourname` with your actual GitHub username. **The trailing dot
matters if GoDaddy adds one — leave it alone either way. Do not include a slash
or the repository name.**

**Optional, for people on IPv6 networks.** Four more records:

| Type | Name | Value |
|------|------|-------|
| AAAA | `@` | `2606:50c0:8000::153` |
| AAAA | `@` | `2606:50c0:8001::153` |
| AAAA | `@` | `2606:50c0:8002::153` |
| AAAA | `@` | `2606:50c0:8003::153` |

Click **Save**.

### 2c · Wait

DNS changes spread across the internet slowly. Usually 10–60 minutes. It can
take up to 24 hours. There is nothing to do but wait, and nothing you can do to
speed it up.

You can watch progress at <https://dnschecker.org> — type `sportsone.world`,
choose **A**, and look for the `185.199.*` addresses appearing around the world.

---

## Part 3 · Turn on HTTPS

Once **Settings ▸ Pages** stops showing a DNS warning:

1. Tick **Enforce HTTPS**.
2. If the box is greyed out, GitHub is still issuing the certificate. Wait an
   hour and come back. It is automatic and free.

Visit <https://sportsone.world>. Green padlock, your site.

---

## What happens on every future push

```text
You press Publish in VS Code
        ↓
Git sends your files to GitHub
        ↓
GitHub Actions starts within seconds
        ↓
  Installs Hugo 0.165.0 (extended)
  Builds the site        →  hugo --minify --gc
  Checks the result      →  is there a homepage? a sitemap?
                            a search index? any articles?
        ↓                       │
  ✅ all checks pass            ❌ any check fails
        ↓                       ↓
  Publishes to GitHub Pages   Stops. The live site is untouched.
        ↓                     You get an email with the error.
  Live on sportsone.world
```

**The important part: a broken build cannot break the live site.** If you mistype
something, the deployment simply does not happen and yesterday's site keeps
serving. You will get an email from GitHub telling you what went wrong.

---

## Checking on a deployment

* **Actions tab** — every publish, with a yellow dot (running), green tick
  (published) or red cross (failed).
* Click any run to see the log. The **Build the website** step contains any
  error message, usually in the last few lines.
* Typical time from push to live: **90 seconds to 2 minutes.**

---

## Frequently asked

**Does it cost anything?**
GitHub Pages is free for public repositories. For a private repository you need
a paid GitHub plan for Pages. The domain renewal at GoDaddy is your only certain
cost.

**Are there limits?**
GitHub Pages allows sites up to 1 GB and roughly 100 GB of traffic per month —
far beyond what a text-and-photos news site uses. Keep photographs under 300 KB
each and you will never approach either.

**Can I use a different host?**
Yes. `hugo --minify` produces a plain `public/` folder that any static host
(Netlify, Cloudflare Pages, S3) will serve. Nothing in the project is tied to
GitHub except the workflow file.

**Someone else needs to publish too.**
Repository **Settings ▸ Collaborators ▸ Add people**. They install VS Code,
clone the repository (docs/01, "using a second computer") and work exactly as
you do.

**I want to see the site before it goes live to everyone.**
Keep the article as `draft: true` and use the local preview. For a full staging
site, a developer can add a second workflow that deploys the `preview` branch to
a separate host — but for a newsroom of one or two people, drafts plus the local
preview cover it.
