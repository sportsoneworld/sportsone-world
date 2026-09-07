#!/usr/bin/env python3
"""
=============================================================================
 THE SPORTSONE PUBLISHING TOOL  —  the part that runs on your laptop

 WHAT THIS IS

   A small web page, served from your own computer, that writes SportsOne
   articles for you. You never see it on the internet and neither does anyone
   else: it listens only to this machine.

 WHAT HAPPENS WHEN YOU START IT

   1. It starts Hugo — the program that builds SportsOne — in preview mode.
   2. It starts itself on http://localhost:1314
   3. It opens that address in your browser.

   Two programs, one window. Close the black window and both stop.

 WHY THE PREVIEW IS THE REAL WEBSITE

   The preview is not a drawing of what SportsOne looks like. It IS SportsOne,
   built by Hugo from the same templates, the same stylesheet and the same
   fonts that produce the live site — just running on this laptop instead of
   on the internet. That is why what you see is what you get: there is no
   second design that could drift out of step with the first.

   This page shows it to you through itself rather than sending your browser
   straight to Hugo, for one reason: it lets the tool draw a red outline
   around your story on the front page so you can see exactly where it landed.

 SECURITY

   No password, no token and no GitHub key is ever written into this page or
   sent to your browser. Publishing shells out to `git`, which uses the
   credentials already stored on this computer — the same ones you use in VS
   Code. If git cannot authenticate, the tool says so and does nothing.
=============================================================================
"""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hugo_project as hp                                    # noqa: E402

ROOT = hp.ROOT
UI_DIR = Path(__file__).resolve().parent / "ui"

CMS_PORT = 1314
HUGO_PORT = 1313
HUGO_HOST = "127.0.0.1"

# Where the tool keeps its own working files. Ignored by git — nothing in here
# is part of the website.
WORK_DIR = ROOT / ".cms"

# The only addresses this server answers with the tool itself. Every other
# address is the website being previewed and is passed through to Hugo.
UI_PATHS = {"/", "", "/index.html", "/app.css", "/app.js"}


class Hugo:
    """The preview server. Started as a child of this program so that closing
    one window stops everything."""

    def __init__(self, port: int):
        self.port = port
        self.process = None
        self.log = WORK_DIR / "hugo-preview.log"

    def start(self) -> bool:
        WORK_DIR.mkdir(parents=True, exist_ok=True)
        hugo = shutil.which("hugo")
        if not hugo:
            return False

        # -D and --buildFuture so a story you are still writing, or one dated
        # later today, can be previewed. The live site is built WITHOUT both
        # of those, which is exactly why the tool checks the date before it
        # lets you publish.
        command = [
            hugo, "server",
            "--port", str(self.port),
            "--bind", HUGO_HOST,
            "--buildDrafts",
            "--buildFuture",
            "--disableFastRender",
            "--navigateToChanged=false",
            "--noHTTPCache",
            # The tool reloads the preview itself, at the moment it knows the
            # story was saved. Hugo's own live-reload script would race it and
            # its websocket cannot be passed through this server.
            "--disableLiveReload",
        ]
        handle = open(self.log, "w", encoding="utf-8")
        self.process = subprocess.Popen(
            command, cwd=str(ROOT), stdout=handle, stderr=subprocess.STDOUT)
        return self.wait_until_ready()

    def wait_until_ready(self, seconds: int = 60) -> bool:
        deadline = time.time() + seconds
        while time.time() < deadline:
            if self.process and self.process.poll() is not None:
                return False
            try:
                with socket.create_connection((HUGO_HOST, self.port), 0.4):
                    return True
            except OSError:
                time.sleep(0.25)
        return False

    def alive(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def errors(self) -> str:
        """Hugo's own message when a build fails, so the tool can show it
        rather than leaving a blank preview."""
        if not self.log.exists():
            return ""
        text = self.log.read_text(encoding="utf-8", errors="replace")
        found = [line for line in text.split("\n")
                 if re.search(r"^(ERROR|Error:|Built in .*error)", line.strip())]
        return "\n".join(found[-6:])

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()


HUGO = Hugo(HUGO_PORT)


# --------------------------------------------------------------------------
#  Git. Only ever called from the Publish button.
# --------------------------------------------------------------------------

def git(*args, timeout: int = 120):
    """Run a git command inside the project and return (ok, output)."""
    try:
        done = subprocess.run(
            ["git"] + list(args), cwd=str(ROOT), capture_output=True,
            text=True, timeout=timeout)
    except FileNotFoundError:
        return False, ("Git is not installed on this computer, so the story "
                       "cannot be sent to the website. Everything you have "
                       "written is saved safely in the project folder.")
    except subprocess.TimeoutExpired:
        return False, (f"git {args[0]} took too long and was stopped. Check "
                       "your internet connection and try Publish again.")
    output = (done.stdout + done.stderr).strip()
    return done.returncode == 0, output


def git_status() -> dict:
    """What the tool can and cannot do with git right now, in plain English."""
    if not shutil.which("git"):
        return {"ready": False,
                "reason": "Git is not installed on this computer.",
                "fix": "Install Git for Windows, then start the tool again."}
    if not (ROOT / ".git").exists():
        return {"ready": False,
                "reason": "This project folder is not connected to GitHub yet.",
                "fix": "Until it is, the tool saves and previews stories "
                       "normally but cannot publish them. See section 2 of "
                       "the tool guide."}
    ok, remote = git("remote", "get-url", "origin")
    if not ok or not remote.strip():
        return {"ready": False,
                "reason": "This project has no GitHub address set.",
                "fix": "Run: git remote add origin <your repository address>"}
    ok, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    return {"ready": True, "remote": remote.strip(),
            "branch": branch.strip() if ok else "main"}


def publish_to_github(paths: list[str], message: str) -> dict:
    """Add exactly the files this story touched, commit them and push.

    Only the named files are staged. Anything else you happen to be part-way
    through in the project is left alone and is not published by accident."""
    status = git_status()
    if not status.get("ready"):
        return {"ok": False, "stage": "setup",
                "message": status["reason"], "fix": status.get("fix", "")}

    existing = [p for p in paths if (ROOT / p).exists()]
    if not existing:
        return {"ok": False, "stage": "files",
                "message": "There were no files to publish."}

    ok, out = git("add", "--", *existing)
    if not ok:
        return {"ok": False, "stage": "add",
                "message": "Git could not take the files ready.", "detail": out}

    ok, staged = git("diff", "--cached", "--name-only")
    if not staged.strip():
        return {"ok": True, "stage": "nothing", "pushed": False,
                "message": "Everything was already published. Nothing to send."}

    ok, out = git("commit", "-m", message)
    if not ok:
        return {"ok": False, "stage": "commit",
                "message": "Git could not save the change.", "detail": out}

    ok, out = git("push", timeout=180)
    if not ok:
        return {"ok": False, "stage": "push", "pushed": False,
                "message": "The story was saved on this computer but could "
                           "not be sent to GitHub. Check your internet "
                           "connection, then press Publish again.",
                "detail": out}

    return {"ok": True, "stage": "done", "pushed": True,
            "files": staged.strip().split("\n"),
            "message": "Sent to GitHub. The website rebuilds itself and the "
                       "story is live in about two or three minutes."}


# --------------------------------------------------------------------------
#  Showing the real website back to you
#
#  Everything under /site/ is fetched from Hugo and passed straight through,
#  so the preview is byte-for-byte the page Hugo built. The only thing added
#  is a small stylesheet that outlines your story, and it is added only when
#  the address asks for it with ?highlight=<web address>.
# --------------------------------------------------------------------------

HIGHLIGHT = """
<style id="sportsone-cms-highlight">
  @keyframes sportsone-cms-pulse {
    0%, 100% { box-shadow: 0 0 0 3px #d8232a, 0 0 0 9px rgba(216,35,42,.22); }
    50%      { box-shadow: 0 0 0 3px #d8232a, 0 0 0 16px rgba(216,35,42,0); }
  }
  .sportsone-cms-found {
    animation: sportsone-cms-pulse 1.9s ease-in-out infinite;
    border-radius: 3px;
    position: relative;
    scroll-margin-top: 96px;
  }
  /* Top-right, because headlines start at the left and the flag must never
     sit on top of the words the journalist is trying to read. */
  .sportsone-cms-flag {
    position: absolute; top: 0; right: 0; z-index: 40;
    background: #d8232a; color: #fff;
    font: 700 11px/1 'Inter', system-ui, sans-serif;
    letter-spacing: .12em; text-transform: uppercase;
    padding: 6px 9px; pointer-events: none;
  }
</style>
<script id="sportsone-cms-script">
(function () {
  var slug = %SLUG%;
  if (!slug) return;

  function mark() {
    var link = document.querySelector('a[href$="/posts/' + slug + '/"]');
    if (!link) return false;

    // Outline the whole item, not just the words. These are the real
    // containers the site builds: .cslide is one slide of a carousel and
    // .card is one card in any feed (layouts/_partials/cards/).
    var box = link.closest('.cslide, .card, .headline-list li, li')
              || link.parentElement;
    if (box.classList.contains('sportsone-cms-found')) return true;
    box.classList.add('sportsone-cms-found');

    var flag = document.createElement('span');
    flag.className = 'sportsone-cms-flag';
    flag.textContent = 'Your story';
    if (getComputedStyle(box).position === 'static') box.style.position = 'relative';
    box.appendChild(flag);

    box.scrollIntoView({ block: 'center', behavior: 'smooth' });
    return true;
  }

  function run() {
    if (mark()) return;
    // Carousels build their slides after the page loads, and rotate. Keep
    // looking for a few seconds so the story is found once its slide exists.
    var tries = 0;
    var timer = setInterval(function () {
      if (mark() || ++tries > 40) clearInterval(timer);
    }, 250);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else { run(); }
})();
</script>
"""


def build_highlight(slug: str) -> bytes:
    return HIGHLIGHT.replace("%SLUG%", json.dumps(slug)).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "SportsOneCMS"

    # The tool prints its own progress; the raw request log would bury it.
    def log_message(self, fmt, *args):
        pass

    # ---------------- small helpers ----------------

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, body: bytes, content_type: str, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    # ---------------- GET ----------------

    def do_GET(self):
        path = self.path.split("?")[0]
        query = self.path.split("?", 1)[1] if "?" in self.path else ""

        if path.startswith("/site/") or path == "/site":
            return self.proxy(path[len("/site"):] or "/", query)
        if path.startswith("/api/"):
            return self.api_get(path, query)
        if path in UI_PATHS:
            return self.serve_ui(path)

        # Everything else belongs to the website being previewed.
        #
        # The pages Hugo builds ask for their stylesheet at /css/sportsone.css
        # and their fonts at /fonts/…, addresses that start at the top of the
        # site. Inside the preview frame those are asked of THIS server, not of
        # the /site/ address the page itself was fetched from, so they have to
        # be passed through as well. Without this the preview arrives as bare
        # unstyled HTML — which is the one thing it must never be.
        return self.proxy(path, query)

    def serve_ui(self, path):
        name = "index.html" if path in ("/", "") else path.lstrip("/")
        target = (UI_DIR / name).resolve()
        if not str(target).startswith(str(UI_DIR.resolve())) or not target.exists():
            return self.send_bytes(b"Not found", "text/plain; charset=utf-8", 404)
        kinds = {".html": "text/html; charset=utf-8",
                 ".css": "text/css; charset=utf-8",
                 ".js": "application/javascript; charset=utf-8",
                 ".svg": "image/svg+xml"}
        kind = kinds.get(target.suffix, "application/octet-stream")
        return self.send_bytes(target.read_bytes(), kind)

    def proxy(self, path, query):
        """Fetch a page from Hugo and hand it on unchanged."""
        target = f"http://{HUGO_HOST}:{HUGO_PORT}{path}"

        highlight = ""
        keep = []
        for part in query.split("&"):
            if part.startswith("highlight="):
                highlight = urllib.parse.unquote(part.split("=", 1)[1])
            elif part:
                keep.append(part)
        if keep:
            target += "?" + "&".join(keep)

        try:
            with urllib.request.urlopen(target, timeout=30) as response:
                body = response.read()
                kind = response.headers.get("Content-Type", "text/html")
                status = response.status
        except urllib.error.HTTPError as error:
            body, kind, status = error.read(), \
                error.headers.get("Content-Type", "text/html"), error.code
        except Exception:
            message = ("<h1>The preview is not running</h1><p>Hugo has "
                       "stopped. Close this window and start the tool "
                       "again.</p>")
            return self.send_bytes(message.encode(), "text/html; charset=utf-8",
                                   502)

        if highlight and "text/html" in kind:
            marker = b"</body>"
            block = build_highlight(highlight)
            body = (body.replace(marker, block + marker)
                    if marker in body else body + block)

        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    # ---------------- the tool's own data ----------------

    def api_get(self, path, query):
        if path == "/api/bootstrap":
            return self.send_json(bootstrap())
        if path == "/api/articles":
            return self.send_json({"articles": hp.list_articles()})
        if path == "/api/slots":
            return self.send_json({"slots": slots_with_contents()})
        if path == "/api/scores":
            return self.send_json({"sports": hp.read_matches(),
                                   "featured": hp.read_featured_matches()})
        if path == "/api/status":
            return self.send_json({"hugo": HUGO.alive(),
                                   "hugoErrors": HUGO.errors(),
                                   "git": git_status()})
        if path.startswith("/api/article/"):
            slug = urllib.parse.unquote(path[len("/api/article/"):])
            article = hp.load_article(slug)
            if article is None:
                return self.send_json({"error": "No such story."}, 404)
            return self.send_json(article)
        return self.send_json({"error": "Unknown request."}, 404)

    # ---------------- POST ----------------

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            payload = self.read_json()
        except Exception:
            return self.send_json({"error": "The tool could not read that."}, 400)

        try:
            if path == "/api/check":
                return self.send_json({
                    "problems": hp.validate(payload,
                                            bool(payload.get("for_publish")))})
            if path == "/api/save":
                return self.send_json(save(payload))
            if path == "/api/upload":
                return self.send_json(upload(payload))
            if path == "/api/read-text":
                return self.send_json(read_text_file(payload))
            if path == "/api/placement":
                return self.send_json(apply_placement(payload))
            if path == "/api/scores":
                message = hp.write_featured_matches(payload.get("featured") or [])
                return self.send_json({"ok": True, "message": message,
                                       "featured": hp.read_featured_matches()})
            if path == "/api/publish":
                return self.send_json(publish(payload))
            if path == "/api/delete":
                slug = (payload.get("slug") or "").strip()
                return self.send_json({"ok": hp.delete_article(slug)})
        except Exception as error:                       # noqa: BLE001
            return self.send_json({
                "error": "Something went wrong inside the tool.",
                "detail": f"{type(error).__name__}: {error}"}, 500)

        return self.send_json({"error": "Unknown request."}, 404)


# --------------------------------------------------------------------------
#  What each button actually does
# --------------------------------------------------------------------------

def slots_with_contents() -> list[dict]:
    """Every place a story can go, and what is in each one right now, so the
    tool can show the running order before anything is changed."""
    titles = {a["slug"]: a["title"] for a in hp.list_articles()}
    out = []
    for slot in hp.all_slots():
        current = hp.read_slot(slot)
        out.append({**slot,
                    "current": [{"slug": s, "title": titles.get(s, s),
                                 "missing": s not in titles} for s in current]})
    return out


def bootstrap() -> dict:
    sports = hp.list_sports()
    return {
        "brand": "SportsOne",
        "sports": sports,
        "sections": sorted({c["name"] for s in sports for c in s["children"]}),
        "slots": slots_with_contents(),
        "articles": hp.list_articles(),
        "git": git_status(),
        "hugo": HUGO.alive(),
        "today": hp.now_stamp()[:16],
        "sitePort": CMS_PORT,
    }


def save(payload: dict) -> dict:
    """Save the story to the project. Called by Save Draft, and by Publish
    before anything is sent anywhere."""
    problems = hp.validate(payload, False)
    if any(p["level"] == "stop" for p in problems):
        return {"ok": False, "problems": problems}

    result = hp.save_article(payload)
    placement_notes = []
    if payload.get("placements") is not None:
        placement_notes = apply_placement({
            "slug": result["slug"],
            "placements": payload.get("placements") or []})["notes"]

    return {"ok": True, "problems": problems, **result,
            "placementNotes": placement_notes,
            "article": hp.load_article(result["slug"])}


def apply_placement(payload: dict) -> dict:
    """Put the story exactly where the desk asked, and nowhere else.

    It is taken out of every slot first, so changing your mind never leaves a
    copy behind in the place you changed it from."""
    slug = (payload.get("slug") or "").strip()
    if not slug:
        return {"ok": False, "notes": ["No story was named."]}

    hp.unplace_everywhere(slug)
    notes = []
    for choice in payload.get("placements") or []:
        slot_id = choice.get("slot")
        position = int(choice.get("position") or 1)
        notes.append({"slot": slot_id,
                      "message": hp.place(slug, slot_id, position)})
    if not notes:
        notes.append({"slot": "", "message":
                      "Not placed by hand — the story appears in Latest News "
                      "and on its sport page, newest first."})
    return {"ok": True, "notes": notes, "slots": slots_with_contents()}


def upload(payload: dict) -> dict:
    """Take a photograph from the browser and file it where the site wants it.

    The picture arrives as text inside the message rather than as a file
    upload, which keeps this server small and means there is no temporary
    folder to clean up afterwards."""
    slug = hp.slugify(payload.get("slug") or "photo")
    data = payload.get("data") or ""
    name = payload.get("name") or "photo.jpg"
    suffix = payload.get("suffix") or ""

    if "," in data:
        data = data.split(",", 1)[1]
    try:
        raw = base64.b64decode(data)
    except Exception:
        return {"ok": False, "message": "That file could not be read."}

    if Path(name).suffix.lower() not in hp.IMAGE_TYPES:
        return {"ok": False,
                "message": f"{name} is not a picture. Use a JPG or a PNG."}
    if not raw:
        return {"ok": False, "message": "That picture is empty."}

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    temp = WORK_DIR / f"upload{Path(name).suffix.lower()}"
    temp.write_bytes(raw)
    try:
        result = hp.save_photo(temp, slug, suffix)
    except Exception as error:                            # noqa: BLE001
        return {"ok": False,
                "message": f"That picture could not be used: {error}"}
    finally:
        temp.unlink(missing_ok=True)

    return {"ok": True, **result}


def read_text_file(payload: dict) -> dict:
    """Read an uploaded .txt or .md file the same way the Inbox does.

    A journalist who already writes stories as text files, in the shape the
    Publishing Guide describes, gets the headline, the sub-headline and the
    settings filled in for them."""
    data = payload.get("data") or ""
    if "," in data:
        data = data.split(",", 1)[1]
    try:
        text = base64.b64decode(data).decode("utf-8-sig", errors="replace")
    except Exception:
        return {"ok": False, "message": "That file could not be read."}

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    temp = WORK_DIR / "upload.txt"
    temp.write_text(text, encoding="utf-8")
    try:
        fields, body, passthrough = hp._imp.read_story(temp)
    finally:
        temp.unlink(missing_ok=True)

    if passthrough is not None:
        parsed, body2 = hp.parse_front_matter(
            "---\n" + passthrough + "\n---\n" + body)
        cats = parsed.get("categories") or []
        return {"ok": True, "title": parsed.get("title", ""),
                "summary": parsed.get("summary", ""), "body": body2,
                "sport": cats[0] if cats else "",
                "sections": cats[1:], "tags": parsed.get("tags") or [],
                "imageCaption": parsed.get("imageCaption", ""),
                "imageAlt": parsed.get("imageAlt", ""),
                "imageSource": parsed.get("imageSource", ""),
                "author": parsed.get("author", "")}

    sections = [s.strip() for s in re.split(r"[,;]", fields.get("_section", ""))
                if s.strip()]
    tags = [t.strip() for t in re.split(r"[,;]", fields.get("tags", ""))
            if t.strip()]
    return {"ok": True,
            "title": fields.get("title", ""),
            "summary": fields.get("summary", ""),
            "body": body,
            "sport": (fields.get("_sport") or "").strip(),
            "sections": sections,
            "tags": tags,
            "imageCaption": fields.get("imageCaption", ""),
            "imageAlt": fields.get("imageAlt", ""),
            "imageSource": fields.get("imageSource", ""),
            "author": fields.get("author", ""),
            "frontPage": (fields.get("_homepage") or "").strip(),
            "order": fields.get("weight", "")}


def publish(payload: dict) -> dict:
    """Save, check, place, then send to GitHub — and stop at the first
    problem rather than publishing half a story."""
    payload = dict(payload)
    payload["draft"] = False

    problems = hp.validate(payload, True)
    if any(p["level"] == "stop" for p in problems):
        return {"ok": False, "stage": "check", "problems": problems}

    result = hp.save_article(payload)
    slug = result["slug"]
    placement = apply_placement({"slug": slug,
                                 "placements": payload.get("placements") or []})

    # Hugo is watching the folder. Give it a moment, then make sure the site
    # still builds before anything is committed.
    time.sleep(1.2)
    errors = HUGO.errors()
    if errors and "ERROR" in errors:
        return {"ok": False, "stage": "build",
                "message": "The website did not build with this story in it, "
                           "so nothing has been published.",
                "detail": errors}

    paths = [result["path"], "data/homepage.yaml", "data/sports.yaml"]
    image = (payload.get("image") or "").strip()
    if image.startswith("/images/"):
        stem = Path(image).stem
        for candidate in hp.PHOTO_DIR.glob(f"{stem}*"):
            paths.append(str(candidate.relative_to(ROOT)))
    for extra in payload.get("extraImages") or []:
        if str(extra).startswith("/images/"):
            stem = Path(str(extra)).stem
            for candidate in hp.PHOTO_DIR.glob(f"{stem}*"):
                paths.append(str(candidate.relative_to(ROOT)))

    headline = (payload.get("title") or slug).strip()
    outcome = publish_to_github(sorted(set(paths)),
                                f"Publish: {headline}")
    return {"ok": outcome.get("ok", False), "stage": outcome.get("stage"),
            "message": outcome.get("message"), "detail": outcome.get("detail"),
            "fix": outcome.get("fix"), "problems": problems,
            "slug": slug, "url": f"/posts/{slug}/",
            "placementNotes": placement["notes"],
            "files": outcome.get("files", [])}


# --------------------------------------------------------------------------
#  Starting up
# --------------------------------------------------------------------------

LINE = "=" * 70


def free_port(preferred: int) -> int:
    """If something else is already using the port — usually a copy of the
    tool left running in another window — quietly move up until one is free."""
    for port in range(preferred, preferred + 12):
        try:
            with socket.create_connection((HUGO_HOST, port), 0.3):
                continue                    # something is listening; try next
        except OSError:
            return port
    return preferred


def ensure_gitignored():
    """Keep the tool's own working folder out of the website."""
    path = ROOT / ".gitignore"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if "/.cms/" in text:
        return
    addition = ("\n# The publishing tool's working folder — logs and part-"
                "finished uploads.\n# Nothing in here belongs to the website."
                "\n/.cms/\n")
    path.write_text(text.rstrip("\n") + "\n" + addition, encoding="utf-8")


def preflight() -> bool:
    """The two things that must be true before the tool is any use."""
    ok = True
    if not shutil.which("hugo"):
        print("  PROBLEM: Hugo is not installed on this computer.")
        print("           Hugo builds the website and draws every preview.")
        print()
        print("           Install it, then start the tool again:")
        print("             winget install Hugo.Hugo.Extended")
        print()
        ok = False
    try:
        import PIL                                          # noqa: F401
    except ImportError:
        print("  NOTE: the picture tool (Pillow) is not installed.")
        print("        Photographs will be filed at their original size")
        print("        instead of being cut to the three sizes the site")
        print("        serves. To fix it, close this and run:")
        print("          python -m pip install Pillow")
        print()
    return ok


def main() -> int:
    global CMS_PORT, HUGO_PORT

    # Print a line at a time. Python holds output back when it is not writing
    # straight to a console, and the one thing this window must never do is
    # stop half way through a sentence while it is actually still working.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass

    print()
    print(LINE)
    print("  SPORTSONE  ·  the publishing tool")
    print(LINE)
    print()

    if not (ROOT / "hugo.toml").exists():
        print("  PROBLEM: this does not look like the SportsOne project.")
        print(f"           Looked in: {ROOT}")
        print()
        input("  Press Enter to close. ")
        return 1

    if not preflight():
        input("  Press Enter to close. ")
        return 1

    ensure_gitignored()

    HUGO_PORT = free_port(HUGO_PORT)
    HUGO.port = HUGO_PORT
    print("  Starting the website preview...", end=" ", flush=True)
    if not HUGO.start():
        print("could not start.")
        print()
        print("  Hugo would not run. Its own message:")
        print()
        for line in (HUGO.errors() or "  (no message)").split("\n"):
            print(f"    {line}")
        print()
        input("  Press Enter to close. ")
        return 1
    print("ready.")

    CMS_PORT = free_port(CMS_PORT)
    if CMS_PORT == HUGO_PORT:
        CMS_PORT = free_port(HUGO_PORT + 1)

    server = ThreadingHTTPServer((HUGO_HOST, CMS_PORT), Handler)
    address = f"http://localhost:{CMS_PORT}/"

    status = git_status()
    print()
    print(f"  The tool is open at   {address}")
    print(f"  Publishing to GitHub  {'yes — ' + status.get('remote', '') if status.get('ready') else 'not set up yet'}")
    if not status.get("ready"):
        print(f"                        {status.get('reason','')}")
    print()
    print("  Your browser should open on its own. If it does not, type the")
    print("  address above into Chrome.")
    print()
    print("  LEAVE THIS WINDOW OPEN while you work.")
    print("  Closing it stops the tool and the preview.")
    print()
    print(LINE)
    print()

    threading.Timer(0.8, lambda: webbrowser.open(address)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopping...")
    finally:
        server.server_close()
        HUGO.stop()
        print("  Closed. Nothing you saved has been lost.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
