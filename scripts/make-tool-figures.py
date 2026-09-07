#!/usr/bin/env python3
"""
=============================================================================
 BUILD  docs/images/tool/*.png   —  the screenshots in the tool guide

     python3 scripts/make-tool-figures.py

 Run this after changing the look of the publishing tool, then rebuild the
 Word guide with scripts/make-tool-guide.py. Between them, no picture in that
 document is ever drawn by hand or pasted in from anywhere.

 WHAT IT DOES

   Starts the publishing tool, drives it through a whole story in a real
   Chrome window exactly as a journalist would — types the words, files a
   photograph, chooses Spotlight position 2, opens each preview — and
   photographs every step. Then it deletes the story it wrote, so the project
   is left exactly as it was found.

 WHAT IT NEEDS

     pip install playwright
     Google Chrome

   Playwright is used only by this script. It is not needed to run the
   publishing tool, and a journalist never installs it.

 THE ONE PICTURE IT DOES NOT MAKE

   fig-tool-published.png shows a story that really was sent to GitHub, and
   this script deliberately never publishes anything. If that picture ever
   needs remaking, take it by hand the next time you publish for real.
=============================================================================
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("This needs Playwright.  Run:  pip install playwright")

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("This needs Pillow.  Run:  pip install Pillow")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "images" / "tool"
WORK = ROOT / ".cms" / "figures"
TOOL = "http://127.0.0.1:1314/"

SLUG = "riverside-hold-on-for-a-first-win-of-the-season"

HEADLINE = "Riverside hold on for a first win of the season at the Riverside"
SUB = ("Two goals in four minutes either side of the interval gave Riverside "
       "their first three points since the opening weekend.")
BODY = """Riverside had not won since the opening weekend. They led inside three
minutes and did not have a shot on target after that.

## The goals

Ellis turned in at the near post from a corner, and four minutes into the
second half Okafor doubled it with a header that the goalkeeper reached but
could not keep out.

## What it means

The win lifts Riverside out of the relegation places for the first time since
August. Their manager described it afterwards as a performance built on
"seventy minutes of defending and twenty of football"."""


# The running orders, saved before anything is touched.
#
# Deleting the demonstration story takes it back out of Spotlight, but it
# cannot put back whatever that story pushed OFF the bottom of the slot —
# on the real site that is a deliberate one-way editorial act. So the two
# files are copied first and put back afterwards, byte for byte.
DATA_FILES = ("homepage.yaml", "sports.yaml", "scores.yaml")


def save_running_orders():
    WORK.mkdir(parents=True, exist_ok=True)
    for name in DATA_FILES:
        source = ROOT / "data" / name
        if source.exists():
            shutil.copy2(source, WORK / (name + ".before"))


def restore_running_orders():
    for name in DATA_FILES:
        kept = WORK / (name + ".before")
        if kept.exists():
            shutil.copy2(kept, ROOT / "data" / name)


def clean_project():
    """Remove the demonstration story, so running this changes nothing."""
    sys.path.insert(0, str(ROOT / "scripts" / "cms"))
    import hugo_project as hp
    for slug in (SLUG, SLUG + "-2"):
        hp.delete_article(slug)
        for photo in hp.PHOTO_DIR.glob(slug + "*"):
            photo.unlink()


def demo_photograph(path: Path):
    """A stand-in picture, so no real agency photograph ends up in the guide."""
    im = Image.new("RGB", (2400, 1350), (18, 52, 96))
    d = ImageDraw.Draw(im)
    for x in range(0, 2400, 60):
        d.line([(x, 0), (x - 400, 1350)], fill=(26, 74, 130), width=18)
    d.ellipse([980, 500, 1420, 940], fill=(216, 35, 42))
    d.ellipse([1060, 580, 1340, 860], fill=(255, 255, 255))
    im.save(path, quality=90)


def console_picture(path: Path):
    """A drawing of the black window, so a Windows reader knows what to
    expect before they double-click anything."""
    W, H = 1200, 620
    im = Image.new("RGB", (W, H), (12, 12, 12))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 34], fill=(58, 58, 58))

    def font(size):
        for candidate in ("/System/Library/Fonts/Menlo.ttc",
                          "C:/Windows/Fonts/consola.ttf",
                          "/System/Library/Fonts/Supplemental/Courier New.ttf"):
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue
        return ImageFont.load_default()

    mono = font(15)
    d.text((12, 9), "SportsOne - Publishing Tool", font=mono,
           fill=(235, 235, 235))
    lines = [
        ("", None),
        (" " + "=" * 70, (150, 150, 150)),
        ("   SPORTSONE  -  the publishing tool", (255, 255, 255)),
        (" " + "=" * 70, (150, 150, 150)),
        ("", None),
        ("   Starting the website preview... ready.", (200, 200, 200)),
        ("", None),
        ("   The tool is open at   http://localhost:1314/", (120, 220, 255)),
        ("   Publishing to GitHub  yes - https://github.com/you/sportsone-world.git",
         (150, 235, 150)),
        ("", None),
        ("   Your browser should open on its own. If it does not, type the",
         (200, 200, 200)),
        ("   address above into Chrome.", (200, 200, 200)),
        ("", None),
        ("   LEAVE THIS WINDOW OPEN while you work.", (255, 225, 120)),
        ("   Closing it stops the tool and the preview.", (200, 200, 200)),
        ("", None),
        (" " + "=" * 70, (150, 150, 150)),
    ]
    y = 52
    for text, colour in lines:
        if text:
            d.text((14, y), text, font=mono, fill=colour or (210, 210, 210))
        y += 26
    im.save(path)


def main() -> int:
    if not shutil.which("hugo"):
        sys.exit("Hugo is not installed, so the tool cannot draw a preview.")

    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    photo = WORK / "demo-photo.jpg"
    demo_photograph(photo)
    console_picture(OUT / "fig-tool-window.png")
    print("  fig-tool-window.png")

    save_running_orders()
    clean_project()

    server = subprocess.Popen(
        [sys.executable, str(ROOT / "scripts" / "cms" / "server.py")],
        cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    try:
        import urllib.request
        for _ in range(80):
            try:
                urllib.request.urlopen(TOOL, timeout=1)
                break
            except Exception:
                time.sleep(0.5)
        else:
            sys.exit("The tool did not start.")

        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome")
            page = browser.new_page(viewport={"width": 1600, "height": 1000})

            def shot(name):
                page.wait_for_timeout(400)
                page.screenshot(path=str(OUT / name))
                print(f"  {name}")

            page.goto(TOOL, wait_until="networkidle")
            shot("fig-tool-open.png")

            page.fill("#f-title", HEADLINE)
            page.fill("#f-summary", SUB)
            page.fill("#f-body", BODY)
            page.wait_for_timeout(2600)
            shot("fig-tool-written.png")

            page.set_input_files("#f-photo", str(photo))
            page.wait_for_timeout(3000)
            page.fill("#f-imageAlt", "Ellis runs towards the corner flag, arms out")
            page.fill("#f-imageCaption", "Ellis celebrates the opening goal")
            page.fill("#f-imageSource", "Getty Images")
            page.wait_for_timeout(2400)
            shot("fig-tool-photo.png")

            page.select_option("#f-sport", "Football")
            page.wait_for_timeout(600)
            page.click('[data-section="Premier League"]')
            page.wait_for_timeout(2400)

            page.click("#addPlace")
            page.wait_for_timeout(900)
            page.select_option('[data-role="slot"]', "spotlight")
            page.wait_for_timeout(900)
            page.select_option('[data-role="pos"]', "2")
            page.wait_for_timeout(2400)
            page.evaluate(
                "document.querySelector('#placements')"
                ".scrollIntoView({block:'center'})")
            page.wait_for_timeout(400)
            page.screenshot(path=str(WORK / "placement.png"))

            # The detail crop of the running order, which is the heart of
            # choosing a position.
            im = Image.open(WORK / "placement.png")
            im.crop((14, 500, 520, 800)).resize((1012, 600), Image.LANCZOS) \
              .save(OUT / "fig-tool-order.png")
            print("  fig-tool-order.png")

            page.click('[data-tab="article"]')
            page.wait_for_timeout(2600)
            shot("fig-tool-preview-article.png")

            page.click('[data-tab="home"]')
            page.wait_for_timeout(3600)
            page.screenshot(path=str(WORK / "home.png"))
            Image.open(WORK / "home.png").crop((528, 60, 1600, 720)) \
                 .save(OUT / "fig-tool-highlight.png")
            print("  fig-tool-highlight.png")

            page.click('[data-tab="sport:football"]')
            page.wait_for_timeout(3600)
            shot("fig-tool-preview-sport.png")

            page.click("#goPublish")
            page.wait_for_timeout(2600)
            shot("fig-tool-confirm.png")
            page.click("#confirmBack")
            page.wait_for_timeout(500)

            page.click('[data-view="stories"]')
            page.wait_for_timeout(1600)
            shot("fig-tool-stories.png")

            page.click('[data-view="scores"]')
            page.wait_for_timeout(1600)
            shot("fig-tool-scores.png")

            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=6)
        except subprocess.TimeoutExpired:
            server.kill()
        clean_project()
        restore_running_orders()
        shutil.rmtree(WORK, ignore_errors=True)

    print("\n  The demonstration story has been removed; the project is "
          "unchanged.")
    print("  Next:  python3 scripts/make-tool-guide.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
