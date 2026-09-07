#!/usr/bin/env python3
"""
=============================================================================
 BUILD THE PICTURES FOR  docs/Publishing-Guide.docx

     hugo server                                  (in one window)
     python3 scripts/make-guide-figures.py        (in another)
     python3 scripts/make-publishing-guide.py

 Run this after a design change, so the screenshots in the newsroom's guide
 still look like the website the newsroom is looking at.

 It drives a headless Chrome to photograph the real site at localhost:1313,
 draws the numbered callouts on top, and writes everything to docs/images/.
 Nothing here is hand-drawn over a screenshot: the callout positions are
 coordinates in this file, so when the layout moves you move a number.

 Needs:  pip install Pillow      and Google Chrome installed
=============================================================================
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "images"
WORK = OUT / ".work"
SITE = "http://localhost:1313"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Fonts. Swap these two lines if you are running this on Windows.
SUP = "/System/Library/Fonts/Supplemental/"
F_REG, F_BOLD = SUP + "Arial.ttf", SUP + "Arial Bold.ttf"
F_MONO = "/System/Library/Fonts/Menlo.ttc"

RED = (214, 32, 44)
INK = (17, 20, 26)
PAPER = (255, 255, 255)
GREY = (108, 116, 130)
LINE = (206, 212, 222)
PANEL = (245, 246, 248)
GREEN = (22, 130, 78)
AMBER = (176, 116, 0)
CONSOLE_BG = (18, 22, 30)


def font(size, bold=False, mono=False):
    if mono:
        return ImageFont.truetype(F_MONO, size)
    return ImageFont.truetype(F_BOLD if bold else F_REG, size)


def badge(draw, xy, n, r=19, fill=RED, fg=PAPER, size=21):
    x, y = xy
    draw.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=PAPER, width=3)
    f = font(size, bold=True)
    t = str(n)
    l, t_, rr, b = draw.textbbox((0, 0), t, font=f)
    draw.text((x - (rr - l) / 2 - l, y - (b - t_) / 2 - t_), t, font=f, fill=fg)


def wrap(draw, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def caption_block(draw, x, y, items, width, title=None):
    fb, fr = font(23, bold=True), font(22)
    if title:
        draw.text((x, y), title, font=font(27, bold=True), fill=INK)
        y += 44
    for n, (head, body) in enumerate(items, 1):
        badge(draw, (x + 17, y + 16), n, r=16, size=18)
        draw.text((x + 46, y + 3), head, font=fb, fill=INK)
        yy = y + 33
        for line in wrap(draw, body, fr, width - 50):
            draw.text((x + 46, yy), line, font=fr, fill=GREY)
            yy += 29
        y = yy + 16
    return y


def scale_to(im, w):
    return im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS)


def frame(canvas, im, xy):
    x, y = xy
    canvas.paste(im, (x, y))
    ImageDraw.Draw(canvas).rectangle(
        (x - 1, y - 1, x + im.size[0], y + im.size[1]), outline=LINE, width=2)


def shoot(url, out: Path, w=1440, h=1400):
    """Photograph a page of the running site."""
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--virtual-time-budget=5000",
                    f"--window-size={w},{h}", f"--screenshot={out}", url],
                   capture_output=True)
    if not out.exists():
        sys.exit(f"Chrome could not photograph {url}. Is `hugo server` running?")
    return Image.open(out).convert("RGB")


def trim_to_content(im: Image.Image) -> Image.Image:
    """A tall capture of a short page is mostly empty. Cut the empty part off."""
    g, last = im.convert("L"), 0
    for y in range(0, g.size[1], 10):
        if ImageStat.Stat(g.crop((0, y, g.size[0], min(y + 10, g.size[1])))).stddev[0] > 4:
            last = y
    return im.crop((0, 0, im.size[0], min(im.size[1], last + 30)))


# ===========================================================================
#  THE FIGURES
#
#  Each one is a function. Comment a line out at the bottom of the file to
#  skip it. The (x, y) pairs in the `marks` lists are measured on the
#  1440-pixel-wide capture of the real page — when the layout moves, these
#  are the numbers to change.
# ===========================================================================

def annotated_shot(source, crop, marks, key, title, sub, out, shot_w=980):
    shot = scale_to(source.crop(crop), shot_w)
    s = shot_w / (crop[2] - crop[0])
    PAD, KEY_W = 40, 540
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    keyh = 60 + sum(50 + 29 * len(wrap(d0, b, font(22), KEY_W - 50)) for _, b in key)
    H = PAD * 2 + 92 + max(shot.size[1], keyh)
    canvas = Image.new("RGB", (PAD * 3 + shot_w + KEY_W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    d.text((PAD, PAD - 6), title, font=font(36, bold=True), fill=INK)
    d.text((PAD, PAD + 40), sub, font=font(23), fill=GREY)
    top = PAD + 92
    frame(canvas, shot, (PAD, top))
    for n, (x, y) in enumerate(marks, 1):
        badge(d, (PAD + x * s, top + (y - crop[1]) * s), n, r=18, size=20)
    caption_block(d, PAD * 2 + shot_w, top, key, KEY_W)
    canvas.save(OUT / out, quality=88, optimize=True, progressive=True)
    print(" ", out, canvas.size)


def fig_home_shots(home):
    annotated_shot(home, (0, 0, 1440, 1560),
        [(96, 160), (300, 1150), (1390, 800), (330, 868)],
        [("Spotlight", "The five stories at the very top, rotating every five "
          "seconds. Type: Front page: Spotlight"),
         ("Top Stories — the big panel", "Four stories rotating in the large "
          "block. Type: Front page: Top stories"),
         ("Top Stories — the four beside it", "Fixed, in the order you set. "
          "Type: Front page: Beside top"),
         ("The picture credit", "One short line naming the agency. It is not a "
          "link, and it never shows a web address.")],
        "Where a story lands on the front page",
        "The top of sportsone.world, with the slots you can put a story into.",
        "fig-home-top.jpg")

    annotated_shot(home, (0, 1640, 1440, 3120),
        [(300, 1685), (1030, 1685), (150, 3010)],
        [("Editor's Picks", "Six stories, two to a row. Type: Front page: "
          "Editor's picks"),
         ("More Headlines", "Fills itself with the six newest stories that are "
          "not already somewhere on this page. Nothing for you to set."),
         ("Live Scores", "The strip at the foot of this block. It updates "
          "itself every fifteen minutes and is not an article slot.")],
        "Editor's Picks and More Headlines", "Further down the same page.",
        "fig-home-picks.jpg")

    annotated_shot(home, (0, 3340, 1440, 4520),
        [(210, 3378), (400, 3700), (1200, 4340)],
        [("The sport's name", "One block for each sport in the toolbar. A story "
          "appears here because of its Sport: line, not because of anything on "
          "the front page."),
         ("The sport's lead carousel", "Five stories. Chosen once, on the "
          "sport's own settings, and used both here and at the top of the "
          "sport's own page."),
         ("Two stories beside it", "The two fixed stories under the carousel.")],
        "The sport blocks", "Cricket, then Football, then Tennis, then Other Sports.",
        "fig-home-sport.jpg")


def fig_article(article):
    src = article.crop((0, 90, 1060, 1120))
    W = 900
    shot = scale_to(src, W)
    s = W / 1060.0
    marks = [(700, 190), (940, 275), (620, 345), (310, 410), (700, 700),
             (560, 1022), (850, 1052)]
    key = [
     ("The headline", "The first line of your text file, or the Headline: line."),
     ("The summary", "Shows here, on every card and in Google. Summary:"),
     ("The byline", "Author: and Role:. Left out, it says SportsOne Desk."),
     ("Share icons", "Facebook, X, WhatsApp, Reddit and a copy-link button. They "
      "appear on articles only — never on the front page."),
     ("The picture", "The file with the same name as your text file. Cropped "
      "automatically; keep the action near the middle."),
     ("The caption", "Photo caption:"),
     ("The credit", "Photo source:. One or two words. Never a link, never a web "
      "address. The full attribution is on the Image Credits page."),
    ]
    PAD, KEY_W = 40, 560
    canvas = Image.new("RGB", (PAD * 3 + W + KEY_W, PAD * 2 + 92 + shot.size[1]), PAPER)
    d = ImageDraw.Draw(canvas)
    d.text((PAD, PAD - 6), "An article page, part by part", font=font(36, bold=True), fill=INK)
    d.text((PAD, PAD + 40), "Everything here comes from the text file you wrote.",
           font=font(23), fill=GREY)
    top = PAD + 92
    frame(canvas, shot, (PAD, top))
    for n, (x, y) in enumerate(marks, 1):
        badge(d, (PAD + x * s, top + (y - 90) * s), n, r=18, size=20)
    caption_block(d, PAD * 2 + W, top, key, KEY_W)
    canvas.save(OUT / "fig-article.jpg", quality=88, optimize=True, progressive=True)
    print("  fig-article.jpg", canvas.size)


def fig_crops():
    """One photograph, and what every crop on the site does to it."""
    photo = Image.open(ROOT / "static/images/photos/leicester-2015-16.jpg").convert("RGB")
    SHAPES = [("Front-page banner", 21, 9), ("The story page", 16, 9),
              ("A sport carousel", 16, 10), ("Top Stories panel", 1, 1),
              ("On a phone", 4, 5)]

    def cover(im, rw, rh, out_w):
        out_h = round(out_w * rh / rw)
        sc = max(out_w / im.width, out_h / im.height)
        r = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
        l, t = (r.width - out_w) // 2, (r.height - out_h) // 2
        return r.crop((l, t, l + out_w, t + out_h))

    a_o = photo.width / photo.height
    wf = min(min(1.0, (rw / rh) / a_o) for _, rw, rh in SHAPES)
    hf = min(min(1.0, a_o / (rw / rh)) for _, rw, rh in SHAPES)

    W, PAD = 1500, 44
    canvas = Image.new("RGB", (W, 1400), PAPER)
    d = ImageDraw.Draw(canvas)
    d.text((PAD, PAD - 6), "One photograph, five shapes", font=font(38, bold=True), fill=INK)
    for i, line in enumerate(wrap(d, "You send one landscape picture and nothing else. The website "
          "cuts it to whatever shape each part of the site needs, always from the centre. You never "
          "crop anything yourself — but because the crop is always central, keep the thing that "
          "matters near the middle of the frame.", font(24), W - PAD * 2)):
        d.text((PAD, PAD + 46 + i * 32), line, font=font(24), fill=GREY)

    y0 = PAD + 150
    orig = scale_to(photo, 700)
    frame(canvas, orig, (PAD, y0))
    ow, oh = orig.size
    bx, by = ow * (1 - wf) / 2, oh * (1 - hf) / 2
    d.rectangle((PAD + bx, y0 + by, PAD + ow - bx, y0 + oh - by), outline=(60, 220, 130), width=5)
    d.text((PAD, y0 + oh + 14), "YOUR PICTURE   ·   2400 px across or more   ·   JPEG or PNG",
           font=font(21, bold=True), fill=GREY)
    note = (f"The green box is the {round(wf*100)}% of the width and {round(hf*100)}% of the height "
            "that survive every crop on the site. Keep the action inside it.")
    for i, line in enumerate(wrap(d, note, font(21), 700)):
        d.text((PAD, y0 + oh + 44 + i * 28), line, font=font(21), fill=(20, 120, 70))

    x, yy = PAD + 760, y0
    for name, rw, rh in SHAPES:
        t = cover(photo, rw, rh, 300 if rw >= rh else 170)
        frame(canvas, t, (x, yy))
        d.text((x + 320, yy + max(0, t.size[1] // 2 - 30)), name, font=font(24, bold=True), fill=INK)
        d.text((x + 320, yy + max(0, t.size[1] // 2 - 30) + 30), f"{rw} : {rh}",
               font=font(22), fill=GREY)
        yy += t.size[1] + 20
    canvas.crop((0, 0, W, max(yy + 10, y0 + oh + 90))).save(
        OUT / "fig-crops.jpg", quality=88, optimize=True, progressive=True)
    print("  fig-crops.jpg")


def fig_map():
    """The slot map: every place on the front page a story can be put."""
    W, PAD = 1500, 40
    rows = [
        ("Spotlight", "5 stories", "Front page: Spotlight",
         "The big rotating banner at the very top. The desk's five picks, in order.", RED),
        ("Top Stories — big panel", "4 stories", "Front page: Top stories",
         "The large rotating block on the left of the Top Stories row.", RED),
        ("Top Stories — the four beside it", "4 stories", "Front page: Beside top",
         "Fixed, in the order written. They do not rotate.", RED),
        ("Editor's Picks", "6 stories", "Front page: Editor's picks",
         "Two to a row, beside More Headlines.", RED),
        ("More Headlines", "6 stories", "nothing to type",
         "Fills itself with the newest stories not already on the page.", GREY),
        ("Live Scores", "—", "nothing to type",
         "Refreshes on its own every fifteen minutes.", GREY),
        ("Cricket · Football · Tennis · Other Sports", "5 + 2 each", "set per sport",
         "One block per sport. What leads each one is chosen on the sport's own "
         "page settings, not on the front page.", AMBER),
    ]

    fh, fs, fm, fb = font(30, bold=True), font(24), font(23, mono=True), font(23)
    ROW_H, GAP = 128, 14
    H = PAD * 2 + 118 + len(rows) * (ROW_H + GAP) + 150
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)

    d.text((PAD, PAD), "The front page, top to bottom", font=font(38, bold=True), fill=INK)
    d.text((PAD, PAD + 52),
           "Every story you publish goes into the Latest feed automatically. These are the extra places "
           "you can put one.", font=font(24), fill=GREY)

    y = PAD + 118
    for name, count, typ, note, colour in rows:
        d.rounded_rectangle((PAD, y, W - PAD, y + ROW_H), radius=10,
                            fill=PANEL, outline=LINE, width=2)
        d.rounded_rectangle((PAD, y, PAD + 9, y + ROW_H), radius=4, fill=colour)
        d.text((PAD + 32, y + 20), name, font=fh, fill=INK)
        for line in wrap(d, note, fb, 700):
            d.text((PAD + 32, y + 62), line, font=fb, fill=GREY); break
        rest = wrap(d, note, fb, 700)
        if len(rest) > 1:
            d.text((PAD + 32, y + 90), " ".join(rest[1:]), font=fb, fill=GREY)

        d.text((PAD + 800, y + 22), "HOLDS", font=font(18, bold=True), fill=GREY)
        d.text((PAD + 800, y + 48), count, font=font(30, bold=True), fill=INK)

        d.text((PAD + 980, y + 22), "WHAT YOU TYPE IN THE ARTICLE",
               font=font(18, bold=True), fill=GREY)
        tw = d.textlength(typ, font=fm)
        if typ.startswith("Front page"):
            d.rounded_rectangle((PAD + 978, y + 48, PAD + 998 + tw, y + 88),
                                radius=6, fill=(255, 255, 255), outline=colour, width=2)
            d.text((PAD + 988, y + 56), typ, font=fm, fill=INK)
        else:
            d.text((PAD + 980, y + 56), typ, font=fm, fill=GREY)
        y += ROW_H + GAP

    y += 18
    d.rounded_rectangle((PAD, y, W - PAD, y + 108), radius=10,
                        fill=(255, 249, 235), outline=(230, 200, 140), width=2)
    d.text((PAD + 26, y + 20), "Leaving a slot short is fine.", font=font(26, bold=True), fill=INK)
    d.text((PAD + 26, y + 56),
           "Name two stories in a slot that holds five and the website adds the three newest ones that "
           "are not already on the page.", font=font(23), fill=(90, 70, 20))
    canvas.save(str(OUT) + "/fig-map.png")
    print("  fig-map.png", canvas.size)


def fig_routes():
    """The two publishing routes, side by side."""
    W, PAD = 1500, 44
    canvas = Image.new("RGB", (W, 1080), PAPER)
    d = ImageDraw.Draw(canvas)
    d.text((PAD, PAD - 6), "Two ways to publish. Pick one.", font=font(38, bold=True), fill=INK)
    d.text((PAD, PAD + 46),
           "They do exactly the same thing. The second needs nothing installed on your computer at all.",
           font=font(24), fill=GREY)

    def route(x, y, w, title, sub, colour, steps, foot):
        h = 130 + len(steps) * 108 + 90
        d.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=(252, 252, 253),
                            outline=LINE, width=2)
        d.rounded_rectangle((x, y, x + w, y + 78), radius=12, fill=colour)
        d.rectangle((x, y + 60, x + w, y + 78), fill=colour)
        d.text((x + 26, y + 14), title, font=font(28, bold=True), fill=PAPER)
        d.text((x + 26, y + 46), sub, font=font(20), fill=(255, 255, 255, 200))
        yy = y + 104
        for i, (head, body) in enumerate(steps, 1):
            badge(d, (x + 46, yy + 18), i, r=17, size=19, fill=colour)
            d.text((x + 80, yy + 2), head, font=font(24, bold=True), fill=INK)
            ly = yy + 34
            for line in wrap(d, body, font(21), w - 110):
                d.text((x + 80, ly), line, font=font(21), fill=GREY)
                ly += 27
            yy = max(ly + 12, yy + 108)
        d.line((x + 26, y + h - 74, x + w - 26, y + h - 74), fill=LINE, width=2)
        for i, line in enumerate(wrap(d, foot, font(21, bold=True), w - 60)):
            d.text((x + 30, y + h - 60 + i * 27), line, font=font(21, bold=True), fill=GREEN)
        return h

    CW = (W - PAD * 3) // 2
    h1 = route(PAD, PAD + 116, CW, "A · On the newsroom laptop",
               "Windows, with the project folder on it",
        RED,
        [("Put the files in the inbox folder",
          "Open sportsone-world, then inbox. Drag your .md or .txt file and its "
          "picture in."),
         ("Double-click Import-Articles.bat",
          "A window opens, does the work and tells you what it did. Close it."),
         ("Double-click Edit-Website.bat",
          "Reads the stories back to you at localhost:1313 before anyone else "
          "sees them."),
         ("Publish",
          "The usual Publish step. Two or three minutes later it is live.")],
        "Best when you want to read the page back before it goes out.")

    h2 = route(PAD * 2 + CW, PAD + 116, CW, "B · On github.com",
               "Any computer, any browser, nothing installed",
        (36, 82, 168),
        [("Open the inbox folder on GitHub",
          "github.com  ›  your repository  ›  inbox"),
         ("Add file  ›  Upload files",
          "Drag your .md or .txt file and its picture onto the page."),
         ("Commit changes",
          "The green button at the bottom. That is the whole job."),
         ("Wait about three minutes",
          "The import runs by itself, then the site publishes itself. The "
          "Actions tab shows a plain-English report of what happened.")],
        "Best when you are away from the desk, or on a phone.")

    canvas = canvas.crop((0, 0, W, PAD * 2 + 116 + max(h1, h2)))
    canvas.save(str(OUT) + "/fig-routes.png")
    print("  fig-routes.png", canvas.size)


def fig_inbox():
    """The folder, and the same-name rule."""
    W, PAD = 1500, 44
    canvas = Image.new("RGB", (W, 1000), PAPER)
    d = ImageDraw.Draw(canvas)
    d.text((PAD, PAD - 6), "The folder, and the one rule", font=font(38, bold=True), fill=INK)
    d.text((PAD, PAD + 46),
           "The text file and the picture must share a name. Nothing else has to match.",
           font=font(24), fill=GREY)

    # --- a Windows-Explorer-ish panel -------------------------------------------
    X, Y, PW, PH = PAD, PAD + 110, 800, 470
    d.rounded_rectangle((X, Y, X + PW, Y + PH), radius=8, fill=(252, 252, 253),
                        outline=(190, 196, 206), width=2)
    d.rectangle((X + 2, Y + 2, X + PW - 2, Y + 52), fill=(240, 242, 245))
    d.text((X + 22, Y + 16), "This PC  ›  sportsone-world  ›  inbox",
           font=font(22), fill=(60, 66, 78))
    d.line((X + 2, Y + 52, X + PW - 2, Y + 52), fill=(210, 215, 224), width=2)

    rows = [("Article-1.md", "Markdown file", "2 KB", True),
            ("Article-1.png", "PNG image", "1,402 KB", True),
            ("Article-2.txt", "Text document", "1 KB", True),
            ("Article-2.jpg", "JPG image", "988 KB", True),
            ("Article-3.md", "Markdown file", "3 KB", True),
            ("Article-3.jpeg", "JPG image", "1,150 KB", True)]
    y = Y + 66
    d.text((X + 70, y), "Name", font=font(20, bold=True), fill=GREY)
    d.text((X + 420, y), "Type", font=font(20, bold=True), fill=GREY)
    d.text((X + 660, y), "Size", font=font(20, bold=True), fill=GREY)
    y += 34
    for i, (name, kind, size, _) in enumerate(rows):
        if i % 2 == 0:
            d.rounded_rectangle((X + 14, y - 8, X + PW - 14, y + 52), radius=6,
                                fill=(238, 245, 253))
        ic = (X + 30, y + 2, X + 56, y + 36)
        is_img = name.rsplit(".", 1)[1] in ("png", "jpg", "jpeg")
        d.rounded_rectangle(ic, radius=4,
                            fill=(214, 232, 250) if is_img else (232, 234, 238),
                            outline=(150, 170, 195) if is_img else (190, 195, 205), width=2)
        d.text((ic[0] + 5, ic[1] + 8), "IMG" if is_img else "TXT",
               font=font(13, bold=True), fill=(40, 90, 150) if is_img else (90, 96, 108))
        d.text((X + 70, y + 8), name, font=font(23), fill=INK)
        d.text((X + 420, y + 10), kind, font=font(21), fill=GREY)
        d.text((X + 660, y + 10), size, font=font(21), fill=GREY)
        y += 62

    # The pairing brackets
    for i in range(3):
        ty = Y + 100 + i * 124 + 4
        bx = X + PW + 16
        d.line((bx, ty, bx + 16, ty), fill=RED, width=4)
        d.line((bx + 16, ty, bx + 16, ty + 62), fill=RED, width=4)
        d.line((bx, ty + 62, bx + 16, ty + 62), fill=RED, width=4)
        d.ellipse((bx + 26, ty + 12, bx + 64, ty + 50), fill=RED)
        d.text((bx + 36, ty + 18), "=", font=font(28, bold=True), fill=PAPER)

    # --- the key ----------------------------------------------------------------
    kx = X + PW + 130
    items = [
     ("Same name, different ending",
      "Article-1.md and Article-1.png become one story. The ending (.md, .txt, "
      ".png, .jpg, .jpeg) does not matter — the name does."),
     ("Capitals and spaces are ignored",
      "'Article 1.MD' still finds 'article-1.jpg'."),
     ("A picture on its own is never lost",
      "It stays in the folder and the report tells you which story it was "
      "waiting for."),
     ("One picture per story",
      "More pictures go inside the story itself. See the guide."),
    ]
    caption_block(d, kx, Y + 6, items, W - kx - PAD)
    canvas = canvas.crop((0, 0, W, Y + PH + 40))
    canvas.save(str(OUT) + "/fig-inbox.png")
    print("  fig-inbox.png", canvas.size)


def fig_journey():
    """From the inbox to every page the story ends up on."""
    W, PAD = 1500, 44
    canvas = Image.new("RGB", (W, 1100), PAPER)
    d = ImageDraw.Draw(canvas)
    d.text((PAD, PAD - 6), "Where your story goes after you publish",
           font=font(38, bold=True), fill=INK)
    d.text((PAD, PAD + 46),
           "You touch the first box. Everything to the right of it happens on its own.",
           font=font(24), fill=GREY)

    def stage(x, y, w, h, title, lines, fill, edge, bold_title=True):
        d.rounded_rectangle((x, y, x + w, y + h), radius=10, fill=fill, outline=edge, width=2)
        d.text((x + 20, y + 16), title, font=font(23, bold=bold_title), fill=INK)
        yy = y + 50
        for l in lines:
            d.text((x + 20, yy), l, font=font(20), fill=GREY)
            yy += 27

    def arrow(x1, y1, x2, y2, label=None):
        d.line((x1, y1, x2, y2), fill=(150, 158, 172), width=4)
        dx = 1 if x2 >= x1 else -1
        d.polygon([(x2 - 16 * dx, y2 - 11), (x2, y2), (x2 - 16 * dx, y2 + 11)], fill=(150, 158, 172))
        if label:
            d.text(((x1 + x2) / 2 - d.textlength(label, font=font(18)) / 2, y1 - 100),
                   label, font=font(18), fill=(140, 148, 162))

    y = PAD + 130
    stage(PAD, y, 300, 150, "1 · You", [
        "Two files with", "the same name,", "in the inbox folder."], (255, 240, 241), RED)
    arrow(PAD + 310, y + 75, PAD + 380, y + 75, "you press go")

    stage(PAD + 392, y, 300, 150, "2 · The import", [
        "Resizes the picture.", "Writes the article.", "Empties the inbox."],
        (255, 250, 235), (225, 190, 120))
    arrow(PAD + 702, y + 75, PAD + 772, y + 75, "automatic")

    stage(PAD + 784, y, 300, 150, "3 · The build", [
        "Rebuilds all 254", "pages of the site,", "in about a minute."],
        (238, 245, 253), (150, 180, 220))
    arrow(PAD + 1094, y + 75, PAD + 1164, y + 75, "automatic")

    stage(PAD + 1176, y, W - PAD - (PAD + 1176), 150, "4 · Live", [
        "sportsone.world", "Two or three minutes", "after you pressed go."],
        (235, 250, 242), (120, 200, 160))

    # What "live" actually means — every place the story now exists.
    y2 = y + 220
    d.text((PAD, y2), "The same story now exists in all of these places, without you doing anything:",
           font=font(25, bold=True), fill=INK)
    dests = [
     ("Its own page", "sportsone.world/posts/your-headline/ — the address is in the import report."),
     ("The Latest feed", "Every story goes here, newest first, ten to a page."),
     ("Its sport's page", "Cricket, Football, Tennis or Other Sports — from the Sport: line."),
     ("Its section pages", "One page per Section: and per tag, built the first time you use it."),
     ("The front page", "Only if you asked for a slot, or if it is new enough to fill a gap."),
     ("Its author's page", "All of that writer's stories, from the Author: line."),
     ("Search", "Findable from the magnifying glass within the same few minutes."),
     ("The RSS feeds", "One for the site and one for every sport, for readers and aggregators."),
     ("Google and social", "The headline, summary and picture are already set up for both."),
     ("The picture library", "static/images/photos/, renamed to match the story."),
    ]
    cols, cw = 2, (W - PAD * 2 - 40) // 2
    yy = y2 + 46
    for i, (h, b) in enumerate(dests):
        cx = PAD + (i % cols) * (cw + 40)
        cy = yy + (i // cols) * 88
        d.rounded_rectangle((cx, cy, cx + cw, cy + 76), radius=8, fill=PANEL, outline=LINE, width=2)
        d.ellipse((cx + 16, cy + 28, cx + 36, cy + 48), fill=GREEN)
        d.text((cx + 50, cy + 12), h, font=font(23, bold=True), fill=INK)
        d.text((cx + 50, cy + 43), b, font=font(19), fill=GREY)
    bottom = yy + ((len(dests) + 1) // cols) * 88 + 10
    canvas = canvas.crop((0, 0, W, bottom))
    canvas.save(str(OUT) + "/fig-journey.png")
    print("  fig-journey.png", canvas.size)


def fig_order():
    """What Order: does to a slot that is already full."""
    W, PAD = 1500, 44
    canvas = Image.new("RGB", (W, 900), PAPER)
    d = ImageDraw.Draw(canvas)
    d.text((PAD, PAD - 6), "Deciding which story is first", font=font(38, bold=True), fill=INK)
    d.text((PAD, PAD + 46),
           "Front page: chooses the slot. Order: chooses the position inside it. Everything already "
           "there moves down one.", font=font(24), fill=GREY)

    BEFORE = ["The 2019 final decided on boundaries", "Five thousand to one at Leicester",
              "Four hours, forty-eight minutes", "The chase at the Gabba", "Miracle on Ice, 1980"]
    AFTER  = ["A serve-and-volley final", "The 2019 final decided on boundaries",
              "Five thousand to one at Leicester", "Four hours, forty-eight minutes",
              "The chase at the Gabba"]

    def column(x, y, w, title, rows, new_at=None, dropped=None):
        d.text((x, y), title, font=font(25, bold=True), fill=INK)
        yy = y + 44
        for i, r in enumerate(rows):
            is_new = (new_at == i)
            d.rounded_rectangle((x, yy, x + w, yy + 62), radius=8,
                                fill=(255, 240, 241) if is_new else PANEL,
                                outline=RED if is_new else LINE, width=3 if is_new else 2)
            d.ellipse((x + 14, yy + 16, x + 46, yy + 48),
                      fill=RED if is_new else (205, 210, 220))
            t = str(i + 1)
            f = font(19, bold=True)
            d.text((x + 30 - d.textlength(t, font=f) / 2, yy + 22), t, font=f, fill=PAPER)
            d.text((x + 60, yy + 19), r, font=font(22), fill=INK)
            if is_new:
                d.text((x + w - 88, yy + 21), "NEW", font=font(17, bold=True), fill=RED)
            yy += 72
        if dropped:
            d.rounded_rectangle((x, yy + 6, x + w, yy + 62), radius=8,
                                fill=(250, 250, 251), outline=(220, 224, 232), width=2)
            d.text((x + 20, yy + 25), dropped, font=font(21), fill=(160, 166, 178))
        return yy

    CW = 560
    y = PAD + 130
    column(PAD, y, CW, "Spotlight, before", BEFORE)
    column(PAD * 2 + CW + 120, y, CW, "Spotlight, after", AFTER, new_at=0,
           dropped="Miracle on Ice, 1980  —  dropped out of the slot")

    # The arrow and the lines that caused it
    ax = PAD + CW + 42
    d.line((ax, y + 190, ax + 92, y + 190), fill=RED, width=6)
    d.polygon([(ax + 92, y + 176), (ax + 124, y + 190), (ax + 92, y + 204)], fill=RED)

    bx, by = PAD, y + 540
    d.rounded_rectangle((bx, by, W - PAD, by + 130), radius=10, fill=CONSOLE_BG)
    d.text((bx + 28, by + 22), "In the new story's text file, you wrote:",
           font=font(21), fill=(150, 160, 176))
    d.text((bx + 28, by + 56), "Front page: Spotlight", font=font(24, mono=True), fill=(140, 220, 255))
    d.text((bx + 28, by + 90), "Order: 1", font=font(24, mono=True), fill=(140, 220, 255))
    d.text((bx + 520, by + 56), "put it in the Spotlight banner", font=font(21), fill=(150, 160, 176))
    d.text((bx + 520, by + 90), "make it the first of the five", font=font(21), fill=(150, 160, 176))

    canvas = canvas.crop((0, 0, W, by + 174))
    canvas.save(str(OUT) + "/fig-order.png")
    print("  fig-order.png", canvas.size)


def fig_report():
    """A real import report, rendered as the window a journalist sees.

    The text is not typed out here — a sample story is put through the actual
    import script, so the figure can never drift from what the tool prints."""
    box = WORK / "sample-inbox"
    box.mkdir(parents=True, exist_ok=True)
    for f in box.iterdir():
        f.unlink()
    (box / "Article-1.md").write_text(
        "Headline: Riverside hold on for a first win of the season\n"
        "Sport: Football\nSection: Premier League\n"
        "Summary: Two goals in four minutes either side of the interval.\n"
        "Photo caption: Ellis celebrates the opening goal at the Riverside.\n"
        "Photo source: Getty Images\nFront page: Top stories\nOrder: 1\n\n"
        "Riverside had not won since the opening weekend.\n", encoding="utf-8")
    (box / "Article-2.txt").write_text(
        "Six wickets before lunch and a Test that lasted two days\n\n"
        "England were bowled out twice inside two sessions.\n", encoding="utf-8")
    (box / "Article-3.md").write_text(
        "Headline: A serve-and-volley final in an era that had stopped playing them\n"
        "Sport: Tennis\nPhoto source: Reuters\nFront page: Spotlight\n\n"
        "Ninety-one net approaches across four sets.\n", encoding="utf-8")
    for name, size, colour in [("Article-1.png", (2400, 1600), (30, 90, 140)),
                               ("Article-2.jpg", (900, 600), (140, 60, 30)),
                               ("Article-3.jpeg", (1800, 1200), (40, 120, 60)),
                               ("Stray-photo.jpg", (800, 600), (90, 90, 90))]:
        Image.new("RGB", size, colour).save(box / name)

    run = subprocess.run([sys.executable, str(ROOT / "scripts" / "import-articles.py"),
                          str(box), "--dry-run", "--keep"],
                         capture_output=True, text=True)
    lines = [l.replace("would be saved as", "saved as")
              .replace("sample-inbox/", "inbox/")
             for l in run.stdout.rstrip("\n").split("\n")
             if "DRY RUN" not in l]
    lines = [l.replace("would be imported", "imported") for l in lines]

    fm = font(19, mono=True)
    PAD, LH = 44, 27
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    body_w = int(max(d0.textlength(l, font=fm) for l in lines)) + 60
    W = max(body_w + PAD * 2, 1200)
    H = PAD + 120 + 44 + len(lines) * LH + 40 + PAD
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    d.text((PAD, PAD - 6), "What the import tells you", font=font(38, bold=True), fill=INK)
    d.text((PAD, PAD + 46),
           "The window that opens when you run it. Read the last section first — it is the only "
           "part that ever needs you.", font=font(23), fill=GREY)

    top = PAD + 120
    d.rounded_rectangle((PAD, top, W - PAD, H - PAD), radius=10, fill=CONSOLE_BG)
    d.rounded_rectangle((PAD, top, W - PAD, top + 40), radius=10, fill=(38, 44, 56))
    d.rectangle((PAD, top + 26, W - PAD, top + 40), fill=(38, 44, 56))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((PAD + 18 + i * 24, top + 13, PAD + 32 + i * 24, top + 27), fill=c)
    d.text((PAD + 110, top + 11), "SportsOne — import the Inbox",
           font=font(18), fill=(160, 168, 182))

    y = top + 56
    for l in lines:
        col = (226, 232, 240)
        if l.startswith("="):
            col = (110, 122, 140)
        elif l.strip().startswith("- ") or "thing(s) to look at" in l:
            col = (250, 204, 110)
        elif l.strip().endswith("imported.") or "Next:" in l:
            col = (110, 226, 160)
        elif l.startswith("  ") and l.strip():
            col = (150, 200, 245)
        elif l and not l.startswith(" "):
            col = (255, 255, 255)
        d.text((PAD + 26, y), l, font=fm, fill=col)
        y += LH
    canvas.save(OUT / "fig-report.png")
    print("  fig-report.png", canvas.size)


# ===========================================================================
#  RUN THEM ALL
# ===========================================================================

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    print("Photographing the site at", SITE)
    home = trim_to_content(shoot(SITE + "/", WORK / "home.png", 1440, 9000))
    article = shoot(SITE + "/posts/world-cup-2019-final/",
                    WORK / "article.png", 1440, 1350)
    print(f"  front page {home.size[1]}px tall")

    print("Drawing the figures into", OUT)
    fig_home_shots(home)
    fig_article(article)
    fig_crops()
    fig_map()
    fig_routes()
    fig_inbox()
    fig_journey()
    fig_order()
    fig_report()

    # Diagrams use a handful of flat colours, so a small palette is lossless
    # to the eye and roughly a quarter of the size in the Word file.
    for name in ("fig-map", "fig-routes", "fig-inbox", "fig-journey",
                 "fig-order", "fig-report"):
        f = OUT / f"{name}.png"
        if f.exists():
            Image.open(f).convert("RGB").convert(
                "P", palette=Image.ADAPTIVE, colors=128).save(f, optimize=True)

    print("\nDone. Now rebuild the guide:")
    print("  python3 scripts/make-publishing-guide.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
