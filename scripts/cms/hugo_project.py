#!/usr/bin/env python3
"""
=============================================================================
 THE HUGO PROJECT, AS THE PUBLISHING TOOL SEES IT

 Everything in this file is about reading and writing the SportsOne website's
 own files. Nothing here knows about web pages, buttons or browsers — that is
 server.py's job. This file knows about articles, photographs, the front page
 and the sport pages.

 THE ONE RULE THIS FILE OBEYS

   The website's files stay exactly as they are. data/homepage.yaml and
   data/sports.yaml are written for a journalist to read: every slot has a
   paragraph of plain English above it explaining what it does. So this file
   edits those lists LINE BY LINE and never rewrites them wholesale. Every
   comment, blank line and note survives untouched.

   That is also why this file does not use PyYAML. Loading a YAML file and
   writing it back out would silently delete every one of those comments, and
   the next journalist to open the file would find bare lists with no
   explanation. It would also be one more thing to install.

 WHAT IT REUSES

   scripts/import-articles.py already knows how to resize a photograph into
   the three sizes the site serves, how to turn a headline into a web address,
   and how to slide a story into a slot at a chosen position without
   disturbing the file around it. This file imports those functions rather
   than writing a second copy, so the tool and the Inbox importer can never
   drift apart.
=============================================================================
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

CONTENT_DIR = ROOT / "content" / "posts"
PHOTO_DIR = ROOT / "static" / "images" / "photos"
DATA_DIR = ROOT / "data"
HOMEPAGE_YAML = DATA_DIR / "homepage.yaml"
SPORTS_YAML = DATA_DIR / "sports.yaml"
SCORES_YAML = DATA_DIR / "scores.yaml"
NAV_YAML = DATA_DIR / "navigation.yaml"

IST = timezone(timedelta(hours=5, minutes=30))

IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}


# --------------------------------------------------------------------------
#  Borrow the Inbox importer's proven helpers.
#
#  Its file name has a dash in it, which is not a legal Python module name,
#  so it is loaded by path rather than with a plain `import`.
# --------------------------------------------------------------------------

def _load_importer():
    path = ROOT / "scripts" / "import-articles.py"
    spec = importlib.util.spec_from_file_location("sportsone_importer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_imp = _load_importer()

slugify = _imp.slugify
process_image = _imp.process_image
yaml_quote = _imp.yaml_quote
yaml_list = _imp.yaml_list
pin_to_slot = _imp.pin_to_slot
SPORT_FOLDERS = _imp.SPORT_FOLDERS


# --------------------------------------------------------------------------
#  WHERE A STORY CAN GO
#
#  Every slot below is a real list in a real file on this website. Nothing
#  here is invented: each one was read out of data/homepage.yaml and
#  data/sports.yaml, and `holds` is the number the front page actually
#  renders, taken from layouts/home.html and layouts/term.html.
# --------------------------------------------------------------------------

HOMEPAGE_SLOTS = [
    {
        "id": "spotlight",
        "group": "Homepage",
        "name": "Spotlight",
        "where": "The five rotating stories at the very top of the front page",
        "file": "homepage",
        "keys": ["spotlight"],
        "holds": 5,
    },
    {
        "id": "top_carousel",
        "group": "Homepage",
        "name": "Top Stories — the big panel",
        "where": "The large rotating panel on the left of Top Stories",
        "file": "homepage",
        "keys": ["top_stories", "carousel"],
        "holds": 4,
    },
    {
        "id": "top_side",
        "group": "Homepage",
        "name": "Top Stories — the four beside it",
        "where": "The four stories stacked down the right of Top Stories",
        "file": "homepage",
        "keys": ["top_stories", "side"],
        "holds": 4,
    },
    {
        "id": "editors_picks",
        "group": "Homepage",
        "name": "Editor's Picks",
        "where": "The six stories, two to a row, beside More Headlines",
        "file": "homepage",
        "keys": ["editors_picks"],
        "holds": 6,
    },
]

# The sport blocks. The same five and two run BOTH the top of that sport's own
# page and that sport's block on the front page — layouts/home.html and
# layouts/term.html read the identical list — so a sport's lead is chosen once.
SPORT_SLOT_SHAPES = [
    {
        "suffix": "carousel",
        "name": "{sport} — the rotating five",
        "where": "The carousel at the top of the {sport} page, and the {sport} "
                 "block on the front page",
        "keys_tail": ["carousel"],
        "holds": 5,
    },
    {
        "suffix": "static",
        "name": "{sport} — the two underneath",
        "where": "The two fixed stories directly below the {sport} carousel",
        "keys_tail": ["static"],
        "holds": 2,
    },
]


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").split("\n")


# --------------------------------------------------------------------------
#  Reading the navigation, so the tool offers the sports the site really has
# --------------------------------------------------------------------------

def list_sports() -> list[dict]:
    """The sports in the toolbar, from data/navigation.yaml.

    Returns the sport's display name ("Cricket"), its category slug
    ("cricket", which is also its key in data/sports.yaml) and its
    sub-categories ("Premier League" and so on)."""
    lines = _read_lines(NAV_YAML)
    sports, current = [], None
    in_primary = False

    for line in lines:
        stripped = line.strip()
        if re.match(r"^primary\s*:", line):
            in_primary = True
            continue
        # Any other top-level key ends the primary block.
        if in_primary and re.match(r"^[a-zA-Z_]+\s*:", line):
            break
        if not in_primary or stripped.startswith("#"):
            continue

        m = re.match(r'^\s{2}-\s+name:\s*"?([^"\n]+?)"?\s*$', line)
        if m:
            current = {"name": m.group(1).strip(), "url": "", "key": "",
                       "children": []}
            sports.append(current)
            continue
        m = re.match(r'^\s{4}url:\s*"?([^"\n]+?)"?\s*$', line)
        if m and current is not None:
            current["url"] = m.group(1).strip()
            current["key"] = current["url"].strip("/").split("/")[-1]
            continue
        m = re.match(r'^\s{6}-\s+name:\s*"?([^"\n]+?)"?\s*$', line)
        if m and current is not None:
            current["children"].append({"name": m.group(1).strip(), "url": ""})
            continue
        m = re.match(r'^\s{8}url:\s*"?([^"\n]+?)"?\s*$', line)
        if m and current is not None and current["children"]:
            current["children"][-1]["url"] = m.group(1).strip()

    # "Home" is a link, not a sport.
    return [s for s in sports if s["url"] != "/" and s["key"]]


def sport_slots() -> list[dict]:
    """One pair of slots per sport, built from the sports the site has."""
    out = []
    for sport in list_sports():
        for shape in SPORT_SLOT_SHAPES:
            out.append({
                "id": f"sport_{sport['key']}_{shape['suffix']}",
                "group": sport["name"],
                "name": shape["name"].format(sport=sport["name"]),
                "where": shape["where"].format(sport=sport["name"]),
                "file": "sports",
                "keys": [sport["key"]] + shape["keys_tail"],
                "holds": shape["holds"],
            })
    return out


def all_slots() -> list[dict]:
    return HOMEPAGE_SLOTS + sport_slots()


def slot_by_id(slot_id: str) -> dict | None:
    for slot in all_slots():
        if slot["id"] == slot_id:
            return slot
    return None


def _slot_path(slot: dict) -> Path:
    return HOMEPAGE_YAML if slot["file"] == "homepage" else SPORTS_YAML


# --------------------------------------------------------------------------
#  Reading a slot's current running order
# --------------------------------------------------------------------------

def _find_list_bounds(lines: list[str], keys: list[str]):
    """Locate the block of `  - slug` lines belonging to `keys`.

    Returns (first_line_index, one_past_last_index) or None. The walk mirrors
    pin_to_slot in the Inbox importer so the two can never disagree about
    where a slot starts and ends."""
    idx, indent = 0, 0
    for depth, key in enumerate(keys):
        pattern = re.compile(r"^" + (" " * indent) + re.escape(key) + r"\s*:")
        while idx < len(lines) and not pattern.match(lines[idx]):
            idx += 1
        if idx >= len(lines):
            return None
        idx += 1
        if depth < len(keys) - 1:
            indent += 2

    first = idx
    while idx < len(lines):
        stripped = lines[idx].strip()
        if stripped.startswith("- "):
            idx += 1
            continue
        if stripped.startswith("#"):
            break
        if not stripped:
            # A blank line only ends the block if a bullet does not follow it.
            if idx + 1 < len(lines) and lines[idx + 1].strip().startswith("- "):
                idx += 1
                continue
            break
        break
    return first, idx


def read_slot(slot: dict) -> list[str]:
    """The slugs currently in a slot, in the order the desk wrote them."""
    lines = _read_lines(_slot_path(slot))
    bounds = _find_list_bounds(lines, slot["keys"])
    if not bounds:
        return []
    first, last = bounds
    out = []
    for n in range(first, last):
        if lines[n].strip().startswith("- "):
            value = re.sub(r"\s*#.*$", "", lines[n]).strip()[2:].strip()
            if value:
                out.append(value)
    return out


def remove_from_slot(slot: dict, slug: str) -> bool:
    """Take a story out of a slot. Used when a placement is changed, so a
    story never ends up pinned in two places by accident."""
    path = _slot_path(slot)
    lines = _read_lines(path)
    bounds = _find_list_bounds(lines, slot["keys"])
    if not bounds:
        return False
    first, last = bounds
    removed = False
    for n in range(last - 1, first - 1, -1):
        if not lines[n].strip().startswith("- "):
            continue
        value = re.sub(r"\s*#.*$", "", lines[n]).strip()[2:].strip()
        if value == slug:
            del lines[n]
            removed = True
    if removed:
        path.write_text("\n".join(lines), encoding="utf-8")
    return removed


def place(slug: str, slot_id: str, position: int) -> str:
    """Put a story into a slot at a chosen position, 1 being the top.

    Anything already there moves down; whatever falls past the end of the slot
    drops out, exactly as the Publishing Guide describes it."""
    slot = slot_by_id(slot_id)
    if slot is None:
        return f"'{slot_id}' is not a slot on this website; nothing was placed."
    remove_from_slot(slot, slug)
    return pin_to_slot(_slot_path(slot), slot["keys"], slug,
                       slot["holds"], position, False)


def unplace_everywhere(slug: str) -> list[str]:
    """Take a story off the front page and off every sport page."""
    touched = []
    for slot in all_slots():
        if remove_from_slot(slot, slug):
            touched.append(slot["name"])
    return touched


def placements_of(slug: str) -> list[dict]:
    """Every slot a story currently sits in, and where in each."""
    out = []
    for slot in all_slots():
        current = read_slot(slot)
        if slug in current:
            out.append({"slot": slot["id"], "name": slot["name"],
                        "group": slot["group"],
                        "position": current.index(slug) + 1})
    return out


# --------------------------------------------------------------------------
#  ARTICLES
#
#  The front matter this website uses was read out of the existing stories in
#  content/posts/. Nothing new has been added to it. In particular the
#  sub-headline a journalist types is the `summary` field, which is what
#  layouts/posts/page.html prints as the standfirst under the headline, and
#  what every card in the feeds shows beneath its headline.
# --------------------------------------------------------------------------

# The order fields are written in, so every file this tool writes looks like
# the ones already in content/posts/.
FIELD_ORDER = [
    "slug", "title", "date", "lastmod", "draft", "summary", "image",
    "imageAlt", "imageCaption", "imageSource", "imageCredit",
    "categories", "tags", "author", "authorRole",
]

LIST_FIELDS = {"categories", "tags"}


def parse_front_matter(raw: str):
    """Split a story file into its settings and its words.

    Deliberately small: it understands the handful of shapes this website's
    own files use — a quoted string, a bare value, and a ["one", "two"] list —
    and nothing else."""
    if not raw.lstrip().startswith("---"):
        return {}, raw
    text = raw.lstrip()
    parts = text.split("\n")
    end = None
    for i in range(1, len(parts)):
        if parts[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, raw

    fields = {}
    for line in parts[1:end]:
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value.startswith("[") and value.endswith("]"):
            fields[key] = [v.strip().strip('"').replace('\\"', '"')
                           for v in re.findall(r'"[^"]*"|[^,\[\]]+', value[1:-1])
                           if v.strip()]
        elif value.startswith('"') and value.endswith('"') and len(value) >= 2:
            fields[key] = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        else:
            fields[key] = value
    return fields, "\n".join(parts[end + 1:]).strip("\n")


def build_front_matter(fields: dict) -> str:
    """Write the settings block back out, in this website's own field order."""
    rows = []
    for key in FIELD_ORDER:
        if key not in fields:
            continue
        value = fields[key]
        if key in LIST_FIELDS:
            if not value:
                continue
            rows.append(f"{key}: {yaml_list(value)}")
        elif key in ("date", "lastmod", "draft"):
            rows.append(f"{key}: {value}")
        else:
            if value in (None, ""):
                if key not in ("image",):
                    continue
                rows.append(f'{key}: ""')
            else:
                rows.append(f"{key}: {yaml_quote(value)}")
    return "---\n" + "\n".join(rows) + "\n---\n"


def sport_folder_for(sport: str) -> str:
    """Which folder under content/posts/ a sport's stories live in."""
    return SPORT_FOLDERS.get((sport or "").strip().lower(), "other-sports")


def article_path(slug: str) -> Path | None:
    """Find a story by its web address, wherever it is filed."""
    for path in CONTENT_DIR.rglob("*.md"):
        fields, _ = parse_front_matter(
            path.read_text(encoding="utf-8", errors="replace"))
        if fields.get("slug") == slug or path.stem == slug:
            return path
    return None


def slug_taken(slug: str, ignore_path: Path | None = None) -> bool:
    for path in CONTENT_DIR.rglob("*.md"):
        if ignore_path and path == ignore_path:
            continue
        if path.stem == slug:
            return True
        fields, _ = parse_front_matter(
            path.read_text(encoding="utf-8", errors="replace"))
        if fields.get("slug") == slug:
            return True
    return False


def unique_slug(base: str, ignore_path: Path | None = None) -> str:
    candidate, n = base, 2
    while slug_taken(candidate, ignore_path):
        candidate, n = f"{base}-{n}", n + 1
    return candidate


def list_articles() -> list[dict]:
    """Every story in the project, newest first, with what the tool needs to
    show a list and work out where each one is placed."""
    out = []
    for path in sorted(CONTENT_DIR.rglob("*.md")):
        if path.name == "_index.md":
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        fields, body = parse_front_matter(raw)
        slug = fields.get("slug") or path.stem
        cats = fields.get("categories") or []
        out.append({
            "slug": slug,
            "title": fields.get("title", path.stem),
            "summary": fields.get("summary", ""),
            "date": fields.get("date", ""),
            "draft": str(fields.get("draft", "false")).lower() == "true",
            "image": fields.get("image", ""),
            "categories": cats,
            "sport": cats[0] if cats else "Other Sports",
            "author": fields.get("author", ""),
            "folder": path.parent.name,
            "path": str(path.relative_to(ROOT)),
            "words": len(body.split()),
            "placements": placements_of(slug),
        })
    out.sort(key=lambda a: a["date"], reverse=True)
    return out


def load_article(slug: str) -> dict | None:
    path = article_path(slug)
    if path is None:
        return None
    raw = path.read_text(encoding="utf-8", errors="replace")
    fields, body = parse_front_matter(raw)
    cats = fields.get("categories") or []
    return {
        "slug": fields.get("slug") or path.stem,
        "title": fields.get("title", ""),
        "summary": fields.get("summary", ""),
        "body": body,
        "date": fields.get("date", ""),
        "draft": str(fields.get("draft", "false")).lower() == "true",
        "image": fields.get("image", ""),
        "imageAlt": fields.get("imageAlt", ""),
        "imageCaption": fields.get("imageCaption", ""),
        "imageSource": fields.get("imageSource", ""),
        "imageCredit": fields.get("imageCredit", ""),
        "sport": cats[0] if cats else "Other Sports",
        "sections": cats[1:],
        "tags": fields.get("tags") or [],
        "author": fields.get("author", ""),
        "authorRole": fields.get("authorRole", ""),
        "path": str(path.relative_to(ROOT)),
        "placements": placements_of(fields.get("slug") or path.stem),
    }


def now_stamp() -> str:
    return datetime.now(IST).strftime("%Y-%m-%dT%H:%M:%S+05:30")


def save_article(data: dict) -> dict:
    """Write a story into the website.

    `data` is what the tool's form collected. Returns what happened, including
    the slug actually used, which may differ from the one asked for if that
    web address was already taken."""
    original_slug = (data.get("original_slug") or "").strip()
    existing_path = article_path(original_slug) if original_slug else None

    wanted = (data.get("slug") or "").strip() or slugify(data.get("title", ""))
    wanted = slugify(wanted)
    slug = unique_slug(wanted, ignore_path=existing_path)

    sport = (data.get("sport") or "Other Sports").strip()
    cats = [sport]
    for extra in data.get("sections") or []:
        extra = str(extra).strip()
        if extra and extra.lower() not in (c.lower() for c in cats):
            cats.append(extra)

    when = (data.get("date") or "").strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}", when):
        when = now_stamp()
    elif len(when) == 10:
        when += "T09:00:00+05:30"
    elif len(when) == 16:            # 2026-09-01T14:30 from the browser
        when += ":00+05:30"

    fields = {
        "slug": slug,
        "title": (data.get("title") or "").strip(),
        "date": when,
        "draft": "true" if data.get("draft") else "false",
        "summary": (data.get("summary") or "").strip(),
        "image": (data.get("image") or "").strip(),
        "imageAlt": (data.get("imageAlt") or "").strip(),
        "imageCaption": (data.get("imageCaption") or "").strip(),
        "imageSource": (data.get("imageSource") or "").strip(),
        "imageCredit": (data.get("imageCredit") or "").strip(),
        "categories": cats,
        "tags": [t.strip() for t in (data.get("tags") or []) if str(t).strip()],
        "author": (data.get("author") or "SportsOne Desk").strip(),
    }
    if (data.get("authorRole") or "").strip():
        fields["authorRole"] = data["authorRole"].strip()

    # Deliberately NOT written: `weight`.
    #
    # In layouts/_partials/func/order.html, weight pins a story to the top of
    # EVERY block the site fills automatically — More Headlines, the Latest
    # feed and any slot the desk left short — not just the slot it was chosen
    # for. Editorial position is handled properly by the order of the list in
    # data/homepage.yaml, so writing weight as well would quietly reorder
    # parts of the site nobody asked to change.

    body = (data.get("body") or "").strip("\n")
    page = build_front_matter(fields) + "\n" + body + "\n"

    folder = CONTENT_DIR / sport_folder_for(sport)
    folder.mkdir(parents=True, exist_ok=True)
    out_path = folder / f"{slug}.md"

    # A story that changed sport, or was renamed, must not be left behind in
    # its old folder as a duplicate.
    if existing_path and existing_path.resolve() != out_path.resolve():
        existing_path.unlink()
        if original_slug and original_slug != slug:
            for slot in all_slots():
                remove_from_slot(slot, original_slug)

    out_path.write_text(page, encoding="utf-8")
    return {"slug": slug, "path": str(out_path.relative_to(ROOT)),
            "renamed": slug != wanted, "url": f"/posts/{slug}/"}


def delete_article(slug: str) -> bool:
    path = article_path(slug)
    if path is None:
        return False
    unplace_everywhere(slug)
    path.unlink()
    return True


# --------------------------------------------------------------------------
#  PHOTOGRAPHS
#
#  Filed exactly where the website expects them, and cut to the three sizes
#  it serves, by the same code the Inbox importer uses.
# --------------------------------------------------------------------------

def save_photo(temp_file: Path, slug: str, suffix: str = "") -> dict:
    """Take an uploaded photograph and file it under static/images/photos/."""
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{slug}{suffix}"
    dest = PHOTO_DIR / f"{name}.jpg"
    note, warning = process_image(temp_file, dest, False)
    return {
        "path": f"/images/photos/{dest.name}",
        "note": note,
        "warning": warning,
    }


def photo_exists(web_path: str) -> bool:
    if not web_path.startswith("/images/"):
        return False
    return (ROOT / "static" / web_path.lstrip("/")).exists()


# --------------------------------------------------------------------------
#  LIVE SCORES
#
#  data/scores.yaml is rewritten every fifteen minutes by GitHub Actions, and
#  scripts/fetch-scores.py deliberately carries the `featured_matches:` list
#  across every refresh. So the desk's pins are the one part of that file a
#  human owns, and they are the only part this tool touches.
# --------------------------------------------------------------------------

def read_matches() -> list[dict]:
    """The matches currently in the feed, grouped by sport, with a flag
    saying which ones the desk has pinned to the front page."""
    lines = _read_lines(SCORES_YAML)
    featured = set(read_featured_matches())

    sports, sport, match, team_list = [], None, None, None
    in_sports = False

    for line in lines:
        if re.match(r"^sports\s*:", line):
            in_sports = True
            continue
        if not in_sports:
            continue

        m = re.match(r'^\s{2}-\s+name:\s*"?([^"\n]+?)"?\s*$', line)
        if m:
            sport = {"name": m.group(1).strip(), "matches": []}
            sports.append(sport)
            match = None
            continue
        m = re.match(r"^\s{6}-\s+id:\s*(.+?)\s*$", line)
        if m and sport is not None:
            match = {"id": m.group(1).strip().strip('"'), "competition": "",
                     "state": "", "stateLabel": "", "teams": []}
            match["featured"] = match["id"] in featured
            sport["matches"].append(match)
            team_list = None
            continue
        if match is None:
            continue
        m = re.match(r'^\s{8}(competition|state|stateLabel):\s*"?([^"\n]*?)"?\s*$',
                     line)
        if m:
            match[m.group(1)] = m.group(2).strip()
            continue
        if re.match(r"^\s{8}teams\s*:", line):
            team_list = match["teams"]
            continue
        m = re.match(r'^\s{10}-\s+name:\s*"?([^"\n]*?)"?\s*$', line)
        if m and team_list is not None:
            team_list.append({"name": m.group(1).strip(), "score": ""})
            continue
        m = re.match(r'^\s{12}score:\s*"?([^"\n]*?)"?\s*$', line)
        if m and team_list:
            team_list[-1]["score"] = m.group(1).strip()

    return [s for s in sports if s["matches"]]


def read_featured_matches() -> list[str]:
    lines = _read_lines(SCORES_YAML)
    out, inside = [], False
    for line in lines:
        if re.match(r"^featured_matches\s*:", line):
            inside = True
            continue
        if not inside:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            value = re.sub(r"\s*#.*$", "", line).strip()[2:].strip().strip('"')
            if value:
                out.append(value)
            continue
        if stripped.startswith("#") or not stripped:
            continue
        break                      # the next real key ends the list
    return out


def write_featured_matches(ids: list[str]) -> str:
    """Rewrite just the `featured_matches:` list, leaving the rest of the file
    — including the automatic scores below it — exactly as it was."""
    lines = _read_lines(SCORES_YAML)
    if not lines:
        return "data/scores.yaml is missing; nothing was changed."

    start = None
    for i, line in enumerate(lines):
        if re.match(r"^featured_matches\s*:", line):
            start = i
            break
    if start is None:
        return "There is no featured_matches list in data/scores.yaml."

    end = start + 1
    while end < len(lines):
        stripped = lines[end].strip()
        if stripped.startswith("- ") or stripped.startswith("#") or not stripped:
            end += 1
            continue
        break
    # Keep any trailing blank line that separates this block from `sports:`.
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1

    if ids:
        block = [f"  - {i}" for i in ids]
    else:
        block = ["  # none pinned — the strip is filling itself from the "
                 "live matches below"]

    lines[start + 1:end] = block
    SCORES_YAML.write_text("\n".join(lines), encoding="utf-8")
    return (f"{len(ids)} match(es) pinned to the front page." if ids
            else "No matches pinned; the strip fills itself.")


# --------------------------------------------------------------------------
#  CHECKS BEFORE ANYTHING GOES OUT
#
#  Every one of these is a real way this website can publish something wrong,
#  found by reading hugo.toml and the templates. They are worded for a
#  journalist, not for a developer.
# --------------------------------------------------------------------------

def validate(data: dict, for_publish: bool) -> list[dict]:
    """Returns a list of problems. `level` is "stop" for something that must
    be fixed before publishing, or "warn" for something worth a second look."""
    problems = []

    def stop(field, message):
        problems.append({"level": "stop", "field": field, "message": message})

    def warn(field, message):
        problems.append({"level": "warn", "field": field, "message": message})

    title = (data.get("title") or "").strip()
    body = (data.get("body") or "").strip()
    summary = (data.get("summary") or "").strip()

    if not title:
        stop("title", "The story has no headline.")
    elif len(title) < 12:
        warn("title", "That headline is very short. Is it finished?")

    if not body:
        stop("body", "The story has no words in it.")
    elif len(body.split()) < 40:
        warn("body", f"The story is only {len(body.split())} words long.")

    if not summary:
        warn("summary", "There is no sub-headline. Readers see it on every "
                        "card and in Google, and the article page prints it "
                        "under the headline.")
    elif len(summary) > 300:
        warn("summary", "The sub-headline is over 300 characters. It will be "
                        "cut short on cards.")

    if not (data.get("sport") or "").strip():
        stop("sport", "No sport has been chosen, so the story would not "
                      "appear on any sport page.")

    image = (data.get("image") or "").strip()
    if not image:
        warn("image", "There is no photograph, so the story will show the "
                      "site's grey placeholder.")
    elif not photo_exists(image):
        stop("image", f"The photograph {image} is not in the project. "
                      "Upload it again.")
    elif not (data.get("imageAlt") or "").strip():
        warn("imageAlt", "The photograph has no description. Readers using a "
                         "screen reader will not know what is in it.")

    # hugo.toml sets buildFuture = false, so a story dated even a minute from
    # now builds to nothing at all and the journalist sees a 404 with no
    # explanation. This is the single easiest way to publish silence.
    when = (data.get("date") or "").strip()
    if when:
        parsed = None
        for shape in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(when, shape)
                break
            except ValueError:
                continue
        if parsed is None:
            stop("date", f"'{when}' is not a date this website understands.")
        else:
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=IST)
            if parsed > datetime.now(IST) + timedelta(minutes=1):
                message = ("That date and time is in the future. This website "
                           "is built with future stories switched off, so it "
                           "would publish nothing at all until someone "
                           "rebuilds the site after "
                           f"{parsed.strftime('%d %B %Y at %H:%M')}.")
                if for_publish:
                    stop("date", message)
                else:
                    warn("date", message)

    if for_publish and data.get("draft"):
        stop("draft", "The story is still marked as a draft, so it would be "
                      "left off the site.")

    slug = (data.get("slug") or "").strip()
    if slug:
        original = (data.get("original_slug") or "").strip()
        ignore = article_path(original) if original else None
        if slug_taken(slug, ignore_path=ignore):
            warn("slug", f"The web address /posts/{slug}/ is already used by "
                         "another story, so this one will be filed at a "
                         "slightly different address.")

    for choice in data.get("placements") or []:
        slot = slot_by_id(choice.get("slot", ""))
        if slot is None:
            stop("placements", f"'{choice.get('slot')}' is not a place on "
                               "this website.")
            continue
        position = int(choice.get("position") or 1)
        if position < 1 or position > slot["holds"]:
            stop("placements", f"{slot['name']} holds {slot['holds']} "
                               f"stories, so position {position} does not "
                               "exist.")
    return problems
