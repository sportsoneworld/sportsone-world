#!/usr/bin/env python3
"""
=============================================================================
 IMPORT ARTICLES  —  a folder of stories and pictures  ->  a published site

 THE WORKFLOW THIS EXISTS FOR

   A journalist has a folder that looks like this:

       Article-1.md      Article-1.png
       Article-2.txt     Article-2.jpg
       Article-3.md      Article-3.jpeg

   The words are in the text file. The picture has the SAME NAME as the text
   file, and that is the only thing that connects them. Nothing else has to
   line up, and nothing has to be named in a special way.

   Drop that folder's contents into  inbox/  and run this. It writes proper
   articles into content/posts/, resizes every picture and files it under
   static/images/photos/, puts the stories where the desk asked for them on
   the front page, and empties the inbox.

 HOW TO RUN IT

     python3 scripts/import-articles.py                 (reads inbox/)
     python3 scripts/import-articles.py some/other/folder
     python3 scripts/import-articles.py --dry-run       (say what you'd do)

   On Windows, double-click  Import-Articles.bat  instead. On GitHub it runs
   itself — see .github/workflows/inbox.yml.

 WHAT THE TEXT FILE MAY LOOK LIKE

   1. Nothing special at all. First line is the headline, the next paragraph
      is the summary, everything after that is the story.

   2. A few plain-English lines at the top, then a blank line, then the story:

          Headline: Riverside hold on for a first win of the season
          Sport: Football
          Summary: Two goals in four minutes either side of half time.
          Photo caption: Ellis celebrates the opener.
          Photo source: Getty Images
          Front page: Top stories
          Order: 1

          The story starts here...

   3. A full Hugo front-matter block between --- lines, for anyone who
      already knows how those work. It is passed through untouched; only the
      fields that are missing get filled in.

 WHAT IT NEVER DOES
   It never overwrites an article that already exists, and it never touches a
   picture that is already on the site. If a name is taken it files the new
   story under a slightly different one and says so in the report.

 IF Pillow IS NOT INSTALLED
   Pictures are copied across unchanged instead of being resized, and the
   report says so. Everything else works. To get resizing:  pip install Pillow
=============================================================================
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --------------------------------------------------------------------------
#  Settings. Everything a desk might want to change is in this block.
# --------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

TEXT_TYPES = {".md", ".markdown", ".txt"}
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}

# The website crops every photograph into whatever shape a slot needs, from a
# 21:9 banner on a wide screen down to a 4:5 portrait on a phone. One landscape
# master picture covers all of them — but it is filed at three sizes, because
# a front page carries about thirty pictures and serving the biggest one to
# all of them costs a reader on a phone about 12MB.
#
#   photo.jpg          the story page, and anywhere the picture is the point
#   photo-panel.jpg    the rotating banners on the front and sport pages
#   photo-card.jpg     the cards in the feeds
#
# You never name the last two. layouts/_partials/func/image.html finds them.
SIZES = (("", 2400), ("-panel", 1800), ("-card", 1200))
MASTER_QUALITY = 85          # the point where bigger files stop looking better
MIN_SENSIBLE_WIDTH = 1600    # anything narrower is flagged in the report
SLUG_MAX_CHARS = 50          # how long a web address is allowed to get

PHOTO_DIR = ROOT / "static" / "images" / "photos"
CONTENT_DIR = ROOT / "content" / "posts"

# Which folder each sport's articles live in. Anything not listed goes to
# other-sports, which is what that section is for.
SPORT_FOLDERS = {
    "cricket": "cricket",
    "football": "football",
    "soccer": "football",
    "tennis": "tennis",
}
DEFAULT_SPORT = "Other Sports"

# The front-page slots a journalist may ask for, the key each one lives under
# in data/homepage.yaml, and how many stories that slot holds.
HOMEPAGE_SLOTS = {
    "spotlight":      (("spotlight",), 5),
    "top stories":    (("top_stories", "carousel"), 4),
    "top story":      (("top_stories", "carousel"), 4),
    "top":            (("top_stories", "carousel"), 4),
    "beside top":     (("top_stories", "side"), 4),
    "editors picks":  (("editors_picks",), 6),
    "editor's picks": (("editors_picks",), 6),
    "editors pick":   (("editors_picks",), 6),
    "picks":          (("editors_picks",), 6),
}

# What each of those slots is called in the report, so a journalist reads
# "Top Stories, the big panel" rather than "top_stories:carousel".
SLOT_NAMES = {
    ("spotlight",):               "Spotlight",
    ("top_stories", "carousel"):  "Top Stories, the big panel",
    ("top_stories", "side"):      "Top Stories, the four beside it",
    ("editors_picks",):           "Editor's Picks",
}

IST = timezone(timedelta(hours=5, minutes=30))

# Header lines a journalist may write at the top of the text file. Left is what
# they type (in any capitalisation), right is the front-matter field it becomes.
HEADER_KEYS = {
    "headline": "title", "title": "title",
    "slug": "slug",
    "summary": "summary", "standfirst": "summary", "intro": "summary",
    "sport": "_sport",
    "section": "_section", "sections": "_section",
    "category": "_section", "categories": "_section",
    "tag": "tags", "tags": "tags",
    "author": "author", "byline": "author",
    "role": "authorRole", "author role": "authorRole",
    "date": "date", "published": "date",
    "caption": "imageCaption", "photo caption": "imageCaption",
    "alt": "imageAlt", "photo description": "imageAlt", "image description": "imageAlt",
    "source": "imageSource", "photo source": "imageSource",
    "picture source": "imageSource", "agency": "imageSource",
    "credit": "imageCredit", "photo credit": "imageCredit", "photographer": "imageCredit",
    "front page": "_homepage", "homepage": "_homepage", "home page": "_homepage",
    "order": "weight", "priority": "weight", "position": "weight",
    "draft": "draft", "hold": "draft",
}


# --------------------------------------------------------------------------
#  Small helpers
# --------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Turn a headline into the last part of a web address.

    Kept short on purpose. A twelve-word headline makes a web address nobody
    can read out over the phone, so it is cut at a word boundary. Write a
    `Slug:` line in the article to choose one yourself."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    words = [w for w in re.split(r"[^a-z0-9]+", text) if w]
    out = []
    for w in words:
        if out and len("-".join(out + [w])) > SLUG_MAX_CHARS and len(out) >= 3:
            break
        out.append(w)
    while len(out) > 3 and out[-1] in SLUG_TRAILING_NOISE:
        out.pop()
    return "-".join(out) or "story"


# Words no web address should end on.
SLUG_TRAILING_NOISE = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for",
    "from", "had", "has", "have", "if", "in", "into", "is", "it", "its", "no",
    "not", "of", "on", "or", "so", "than", "that", "the", "then", "to", "was",
    "were", "when", "which", "while", "who", "with",
}


def yaml_quote(value: str) -> str:
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def yaml_list(values) -> str:
    return "[" + ", ".join(yaml_quote(v) for v in values) + "]"


def title_case_headline(text: str) -> str:
    """A file called `riverside-win.md` with no headline in it becomes
    'Riverside win' rather than 'riverside-win'."""
    words = re.split(r"[-_\s]+", text.strip())
    if not words:
        return "Untitled"
    out = " ".join(w for w in words if w)
    return out[:1].upper() + out[1:]


# --------------------------------------------------------------------------
#  Reading the journalist's text file
# --------------------------------------------------------------------------

def split_front_matter(raw: str):
    """Return (front_matter_text, body). Front matter is None when the file
    does not open with a --- fence."""
    if not raw.lstrip().startswith("---"):
        return None, raw
    stripped = raw.lstrip()
    parts = stripped.split("\n")
    for i in range(1, len(parts)):
        if parts[i].strip() == "---":
            return "\n".join(parts[1:i]), "\n".join(parts[i + 1:])
    return None, raw


def read_header_block(body: str):
    """Pull `Key: value` lines off the top of a plain text file.

    Stops at the first blank line, or at the first line that is plainly part of
    the story rather than a header. Returns (fields, remaining_body)."""
    fields, lines = {}, body.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            if fields:          # blank line ends the header block
                i += 1
                break
            i += 1
            continue
        m = re.match(r"^\s{0,3}([A-Za-z][A-Za-z' ]{1,24}?)\s*:\s*(.*)$", line)
        if not m or m.group(1).strip().lower() not in HEADER_KEYS:
            break
        fields[HEADER_KEYS[m.group(1).strip().lower()]] = m.group(2).strip()
        i += 1
    return fields, "\n".join(lines[i:]).strip("\n")


def read_story(path: Path):
    """Read one text file and return (fields, body, passthrough_front_matter)."""
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    fm, body = split_front_matter(raw)
    if fm is not None:
        return {}, body.strip("\n"), fm

    fields, body = read_header_block(body)

    # No headline given: take the first line of the story, and let the rest of
    # the first paragraph be the summary.
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    if "title" not in fields and paragraphs:
        first = paragraphs.pop(0)
        head, _, tail = first.partition("\n")
        fields["title"] = re.sub(r"^#+\s*", "", head).strip()
        if tail.strip():
            paragraphs.insert(0, tail.strip())
        body = "\n\n".join(paragraphs)
    if "summary" not in fields and paragraphs:
        fields["summary"] = re.sub(r"\s+", " ", paragraphs[0])[:280]
    return fields, body.strip("\n"), None


# --------------------------------------------------------------------------
#  The picture
# --------------------------------------------------------------------------

def process_image(src: Path, dest: Path, dry_run: bool):
    """Save the picture at each of the three sizes. Returns (note, warning)."""
    try:
        from PIL import Image, ImageOps      # noqa: PLC0415
    except ImportError:
        if not dry_run:
            dest = dest.with_suffix(src.suffix.lower())
            shutil.copy2(src, dest)
        return (f"copied unchanged as {dest.name}",
                "Pillow is not installed, so the picture was copied at its "
                "original size and only one copy was made. Run:  pip install Pillow")

    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)     # honour the camera's rotation
        w, h = im.size
        warning = None
        if w < MIN_SENSIBLE_WIDTH:
            warning = (f"the picture is only {w}px across. Anything under "
                       f"{MIN_SENSIBLE_WIDTH}px is soft on a big screen — "
                       "ask for a larger copy if you can.")
        if h > w:
            warning = ((warning + " ") if warning else "") + (
                "it is a portrait picture. Every slot on the site is landscape, "
                "so the top and bottom will be cropped off.")

        if im.mode in ("RGBA", "LA", "P"):
            flat = Image.new("RGB", im.size, (255, 255, 255))
            im = im.convert("RGBA")
            flat.paste(im, mask=im.split()[-1])
            im = flat
        else:
            im = im.convert("RGB")

        made = []
        for suffix, width in SIZES:
            out = dest.with_name(f"{dest.stem}{suffix}{dest.suffix}")
            copy = im if im.width <= width else im.resize(
                (width, round(im.height * width / im.width)), Image.LANCZOS)
            # A picture already smaller than a size does not get a copy at
            # that size — the template falls back to the one above it.
            if suffix and im.width <= width * 1.05:
                continue
            if not dry_run:
                out.parent.mkdir(parents=True, exist_ok=True)
                copy.save(out, "JPEG", quality=MASTER_QUALITY, optimize=True,
                          progressive=True)
            made.append(f"{copy.size[0]}px")

        verb = "would file" if dry_run else "filed"
        note = f"{w}x{h}, {verb} {len(made)} sizes ({', '.join(made)}) as {dest.name}"
        if not dry_run and dest.exists():
            note += f", {dest.stat().st_size // 1024} KB"
        return note, warning


# --------------------------------------------------------------------------
#  Putting a story on the front page — data/homepage.yaml, comments and all
# --------------------------------------------------------------------------

def pin_to_slot(yaml_path: Path, keys, slug: str, limit: int,
                position: int | None, dry_run: bool) -> str:
    """Insert `slug` into a list in a YAML file without disturbing anything
    else in it — every comment, blank line and neighbouring block is left
    exactly as it was. `keys` is the path to the list, e.g.
    ("top_stories", "carousel"). `position` is 1 for the top of the slot."""
    where_name = SLOT_NAMES.get(tuple(keys), ":".join(keys))
    if not yaml_path.exists():
        return f"{yaml_path.name} is missing, so nothing was pinned."

    lines = yaml_path.read_text(encoding="utf-8").split("\n")

    # Walk down to the list we want, matching each key at its own indent.
    idx, indent = 0, 0
    for depth, key in enumerate(keys):
        pattern = re.compile(r"^" + (" " * indent) + re.escape(key) + r"\s*:")
        while idx < len(lines) and not pattern.match(lines[idx]):
            idx += 1
        if idx >= len(lines):
            return f"'{where_name}' is not in {yaml_path.name}; nothing pinned."
        idx += 1
        if depth < len(keys) - 1:
            indent += 2

    # The items are the "  - something" lines that follow.
    first = idx
    while idx < len(lines) and (lines[idx].strip().startswith("- ")
                                or not lines[idx].strip()
                                or lines[idx].lstrip().startswith("#")):
        if lines[idx].strip().startswith("#") and not lines[idx].strip().startswith("- "):
            break
        if not lines[idx].strip() and idx + 1 < len(lines) and \
                not lines[idx + 1].strip().startswith("- "):
            break
        idx += 1
    items = [(n, lines[n]) for n in range(first, idx) if lines[n].strip().startswith("- ")]

    if any(re.sub(r"\s*#.*$", "", ln).strip().lstrip("- ").strip() == slug
           for _, ln in items):
        return f"already in {where_name} — left alone."

    bullet_indent = (len(items[0][1]) - len(items[0][1].lstrip())) if items else indent + 2
    new_line = " " * bullet_indent + f"- {slug}"

    where = 0 if position is None else max(0, min(position - 1, len(items)))
    at = items[where][0] if where < len(items) else (items[-1][0] + 1 if items else first)
    lines.insert(at, new_line)

    # Keep the slot to its size: drop whatever fell off the bottom.
    dropped = []
    if limit:
        bullets = [n for n in range(first, idx + 2)
                   if n < len(lines) and lines[n].strip().startswith("- ")]
        for n in reversed(bullets[limit:]):
            dropped.append(re.sub(r"\s*#.*$", "", lines[n]).strip().lstrip("- ").strip())
            del lines[n]

    if not dry_run:
        yaml_path.write_text("\n".join(lines), encoding="utf-8")
    msg = f"{where_name}, position {where + 1}"
    if dropped:
        msg += f" — this pushed {', '.join(reversed(dropped))} out of the slot"
    return msg


# --------------------------------------------------------------------------
#  Building the article
# --------------------------------------------------------------------------

def unique_slug(slug: str) -> str:
    existing = {p.stem for p in CONTENT_DIR.rglob("*.md")}
    taken_urls = set()
    for p in CONTENT_DIR.rglob("*.md"):
        m = re.search(r'^slug:\s*"?([^"\n]+)"?', p.read_text(encoding="utf-8",
                      errors="replace"), re.M)
        if m:
            taken_urls.add(m.group(1).strip())
    candidate, n = slug, 2
    while candidate in existing or candidate in taken_urls:
        candidate, n = f"{slug}-{n}", n + 1
    return candidate


def build_front_matter(f: dict, slug: str, image_path: str) -> str:
    sport = (f.get("_sport") or DEFAULT_SPORT).strip()
    cats = [sport.title() if sport.islower() else sport]
    for extra in re.split(r"[,;]", f.get("_section", "")):
        extra = extra.strip()
        if extra and extra.lower() not in (c.lower() for c in cats):
            cats.append(extra)

    tags = [t.strip() for t in re.split(r"[,;]", f.get("tags", "")) if t.strip()]

    when = f.get("date", "").strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}", when):
        when = datetime.now(IST).strftime("%Y-%m-%dT%H:%M:%S+05:30")
    elif len(when) == 10:
        when += "T09:00:00+05:30"

    draft = str(f.get("draft", "")).strip().lower() in ("true", "yes", "y", "1", "hold")

    rows = [
        f'slug: {yaml_quote(slug)}',
        f'title: {yaml_quote(f.get("title", "Untitled"))}',
        f"date: {when}",
        f"draft: {'true' if draft else 'false'}",
        f'summary: {yaml_quote(f.get("summary", ""))}',
        f'image: {yaml_quote(image_path)}' if image_path else 'image: ""',
        f'imageAlt: {yaml_quote(f.get("imageAlt") or f.get("imageCaption") or f.get("title", ""))}',
    ]
    if f.get("imageCaption"):
        rows.append(f'imageCaption: {yaml_quote(f["imageCaption"])}')
    if f.get("imageSource"):
        rows.append(f'imageSource: {yaml_quote(f["imageSource"])}')
    if f.get("imageCredit"):
        rows.append(f'imageCredit: {yaml_quote(f["imageCredit"])}')
    rows.append(f"categories: {yaml_list(cats)}")
    if tags:
        rows.append(f"tags: {yaml_list(tags)}")
    rows.append(f'author: {yaml_quote(f.get("author", "SportsOne Desk"))}')
    if f.get("authorRole"):
        rows.append(f'authorRole: {yaml_quote(f["authorRole"])}')
    if str(f.get("weight", "")).strip().isdigit():
        rows.append(f'weight: {int(f["weight"])}')
    return "---\n" + "\n".join(rows) + "\n---\n"


def sport_folder(f: dict) -> str:
    return SPORT_FOLDERS.get((f.get("_sport") or "").strip().lower(), "other-sports")


# --------------------------------------------------------------------------
#  One pass over the folder
# --------------------------------------------------------------------------

def find_pairs(folder: Path):
    """Match each text file to the picture with the same name. The comparison
    ignores capitals and spaces, so 'Article 1.MD' finds 'article-1.jpg'."""
    def key(p: Path) -> str:
        return re.sub(r"[^a-z0-9]", "", p.stem.lower())

    texts, images = {}, {}
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.name.startswith("."):
            continue
        if p.suffix.lower() in TEXT_TYPES and p.name.upper() != "README.MD":
            texts[key(p)] = p
        elif p.suffix.lower() in IMAGE_TYPES:
            images.setdefault(key(p), p)
    pairs = [(texts[k], images.get(k)) for k in sorted(texts)]
    orphan_images = [images[k] for k in sorted(images) if k not in texts]
    return pairs, orphan_images


def run(folder: Path, dry_run: bool, keep: bool) -> int:
    if not folder.exists():
        print(f"There is no folder called {folder}. Nothing to do.")
        return 0

    pairs, orphans = find_pairs(folder)
    if not pairs:
        print(f"No articles found in {folder}. Put a .md or .txt file in it, "
              "with a picture of the same name beside it.")
        return 0

    print("=" * 74)
    print(f"  {len(pairs)} STORY(S) FOUND IN {folder.name}/")
    if dry_run:
        print("  DRY RUN — this is only a rehearsal. Nothing will be written.")
    print("=" * 74)

    warnings, done = [], 0
    for text_file, image_file in pairs:
        print(f"\n{text_file.name}")
        fields, body, passthrough = read_story(text_file)

        if passthrough is not None:
            m = re.search(r'^slug:\s*"?([^"\n]+)"?', passthrough, re.M)
            t = re.search(r'^title:\s*"?([^"\n]+)"?', passthrough, re.M)
            base = (m.group(1) if m else slugify(t.group(1) if t else text_file.stem))
            s = re.search(r'^\s*(?:categories:\s*\[\s*")([^"]+)', passthrough, re.M)
            fields["_sport"] = s.group(1) if s else DEFAULT_SPORT
        else:
            if not fields.get("title"):
                fields["title"] = title_case_headline(text_file.stem)
            base = slugify(fields.get("slug") or fields["title"])

        slug = unique_slug(base)
        if slug != base:
            warnings.append(f"{text_file.name}: '{base}' was already taken, so "
                            f"the story was filed as '{slug}'.")

        # --- the picture ---
        image_ref = ""
        if image_file:
            dest = PHOTO_DIR / f"{slug}.jpg"
            note, warn = process_image(image_file, dest, dry_run)
            image_ref = f"/images/photos/{dest.name}"
            print(f"  picture   {image_file.name}: {note}")
            if warn:
                warnings.append(f"{image_file.name}: {warn}")
        else:
            warnings.append(f"{text_file.name}: no picture with a matching name, "
                            "so the story will use the site's placeholder. Name "
                            f"the photograph '{text_file.stem}.jpg' and run again.")
            print("  picture   none found")

        # --- the article ---
        out_dir = CONTENT_DIR / sport_folder(fields)
        out_file = out_dir / f"{slug}.md"
        if passthrough is not None:
            fm = passthrough
            if "image:" not in fm and image_ref:
                fm += f'\nimage: {yaml_quote(image_ref)}'
            if "slug:" not in fm:
                fm = f'slug: {yaml_quote(slug)}\n' + fm
            page = "---\n" + fm.strip("\n") + "\n---\n" + body.strip("\n") + "\n"
        else:
            page = build_front_matter(fields, slug, image_ref) + "\n" + body.strip("\n") + "\n"

        if not dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file.write_text(page, encoding="utf-8")
        print(f"  article   {out_file.relative_to(ROOT)}")
        print(f"  address   /posts/{slug}/")

        # --- the front page ---
        ask = (fields.get("_homepage") or "").strip().lower().rstrip(".")
        ask = re.sub(r"[^a-z' ]", " ", ask).strip()
        if ask and ask not in ("no", "none", "latest", "feed"):
            match = HOMEPAGE_SLOTS.get(ask)
            if match is None:
                for name, spec in HOMEPAGE_SLOTS.items():
                    if name in ask or ask in name:
                        match = spec
                        break
            if match is None:
                warnings.append(f"{text_file.name}: 'Front page: {fields['_homepage']}' "
                                "is not a slot on the front page. Use Spotlight, "
                                "Top stories, Beside top or Editor's picks.")
            else:
                keys, limit = match
                pos = int(fields["weight"]) if str(fields.get("weight", "")).isdigit() else None
                msg = pin_to_slot(ROOT / "data" / "homepage.yaml", keys, slug,
                                  limit, pos, dry_run)
                print(f"  frontpage {msg}")

        if not dry_run and not keep:
            text_file.unlink()
            if image_file:
                image_file.unlink()
        done += 1

    for o in orphans:
        warnings.append(f"{o.name}: a picture with no article of the same name. "
                        "It was left in the inbox.")

    print("\n" + "=" * 74)
    print(f"  {done} article(s) {'would be imported' if dry_run else 'imported'}.")
    if warnings:
        print(f"  {len(warnings)} thing(s) to look at:\n")
        for w in warnings:
            print(f"    - {w}")
    else:
        print("  Nothing to report — every story had a picture and a home.")
    print("=" * 74)
    if not dry_run:
        print("\n  Next: check them in the preview, then publish.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Turn a folder of matching .md/.txt and picture files into "
                    "published SportsOne articles.")
    ap.add_argument("folder", nargs="?", default=str(ROOT / "inbox"),
                    help="the folder to read (default: inbox/)")
    ap.add_argument("--dry-run", action="store_true",
                    help="say what would happen and write nothing")
    ap.add_argument("--keep", action="store_true",
                    help="leave the original files in the folder afterwards")
    args = ap.parse_args()
    return run(Path(args.folder).resolve(), args.dry_run, args.keep)


if __name__ == "__main__":
    sys.exit(main())
