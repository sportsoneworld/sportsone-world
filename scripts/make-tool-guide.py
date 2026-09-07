#!/usr/bin/env python3
"""
=============================================================================
 BUILD  docs/Publishing-Tool-Guide.docx

     python3 scripts/make-tool-guide.py

 The guide to the publishing tool, written for a journalist working on a
 Windows 10 laptop. Everything in it is written here, so the Word file is
 never edited by hand — change the words below and run this again and the
 whole document is rebuilt, screenshots and all.

 The screenshots live in docs/images/tool/ and are real pictures of the
 running tool, not mock-ups.

 This is deliberately a separate document from docs/Publishing-Guide.docx.
 That one covers the Inbox route, which still works exactly as it did. This
 one covers the tool. Neither replaces the other.

 Needs:  pip install python-docx
=============================================================================
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor
except ImportError:
    sys.exit("This needs python-docx.  Run:  pip install python-docx")

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "docs" / "images" / "tool"
OUT = ROOT / "docs" / "Publishing-Tool-Guide.docx"

INK = RGBColor(0x11, 0x14, 0x1A)
GREY = RGBColor(0x5A, 0x62, 0x70)
RED = RGBColor(0xC8, 0x1E, 0x2B)
GREEN = RGBColor(0x14, 0x6B, 0x43)
BODY = "Calibri"
MONO = "Consolas"

doc = Document()

for s in doc.sections:
    s.top_margin = s.bottom_margin = Inches(0.8)
    s.left_margin = s.right_margin = Inches(0.85)
CONTENT_W = 7.0

st = doc.styles["Normal"]
st.font.name = BODY
st.font.size = Pt(11.5)
st.font.color.rgb = INK
st.paragraph_format.space_after = Pt(9)
st.paragraph_format.line_spacing = 1.18

for name, size, colour, before, after in [
        ("Heading 1", 24, RED, 26, 8),
        ("Heading 2", 16, INK, 20, 6),
        ("Heading 3", 13, INK, 14, 4)]:
    h = doc.styles[name]
    h.font.name = BODY
    h.font.size = Pt(size)
    h.font.bold = True
    h.font.color.rgb = colour
    h.paragraph_format.space_before = Pt(before)
    h.paragraph_format.space_after = Pt(after)


# --- helpers (same house style as scripts/make-publishing-guide.py) ---------

def shade(cell, hexcolour):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), hexcolour)
    cell._tc.get_or_add_tcPr().append(el)


def p(text="", size=11.5, bold=False, italic=False, colour=None,
      space_after=9, align=None, mono=False, indent=0):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(space_after)
    if indent:
        par.paragraph_format.left_indent = Inches(indent)
    if align is not None:
        par.alignment = align
    if text:
        r = par.add_run(text)
        r.font.size = Pt(size)
        r.bold = bold
        r.italic = italic
        r.font.name = MONO if mono else BODY
        r.font.color.rgb = colour or INK
    return par


def rich(*parts, space_after=9, indent=0):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(space_after)
    if indent:
        par.paragraph_format.left_indent = Inches(indent)
    for text, opt in parts:
        r = par.add_run(text)
        r.font.size = Pt(opt.get("size", 11.5))
        r.bold = opt.get("bold", False)
        r.italic = opt.get("italic", False)
        r.font.name = MONO if opt.get("mono") else BODY
        r.font.color.rgb = opt.get("colour", INK)
    return par


def bullets(items, style="List Bullet"):
    for it in items:
        par = doc.add_paragraph(style=style)
        par.paragraph_format.space_after = Pt(4)
        if isinstance(it, tuple):
            r = par.add_run(it[0]); r.bold = True; r.font.size = Pt(11.5)
            r2 = par.add_run("  " + it[1]); r2.font.size = Pt(11.5)
        else:
            r = par.add_run(it); r.font.size = Pt(11.5)


def steps(items):
    bullets(items, style="List Number")


def code(lines, fill="F4F5F7"):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    c = t.cell(0, 0)
    shade(c, fill)
    c.width = Inches(CONTENT_W)
    first = True
    for line in lines:
        par = c.paragraphs[0] if first else c.add_paragraph()
        first = False
        par.paragraph_format.space_after = Pt(0)
        par.paragraph_format.space_before = Pt(0)
        par.paragraph_format.line_spacing = 1.15
        r = par.add_run(line)
        r.font.name = MONO
        r.font.size = Pt(10)
        r.font.color.rgb = INK
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def callout(title, body, fill="FFF6E0", accent=RGBColor(0x8A, 0x5D, 0x00)):
    t = doc.add_table(rows=1, cols=1)
    c = t.cell(0, 0)
    shade(c, fill)
    par = c.paragraphs[0]
    par.paragraph_format.space_after = Pt(3)
    r = par.add_run(title)
    r.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = accent
    par2 = c.add_paragraph()
    par2.paragraph_format.space_after = Pt(2)
    r2 = par2.add_run(body)
    r2.font.size = Pt(11)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def figure(name, caption, width=CONTENT_W):
    path = IMG / name
    if not path.exists():
        p(f"[missing figure: {name}]", colour=RED)
        return
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(8)
    par.paragraph_format.space_after = Pt(4)
    par.add_run().add_picture(str(path), width=Inches(width))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(14)
    r = cap.add_run(caption)
    r.italic = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = GREY


def table(headers, rows, widths=None, header_fill="1B1F27"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        shade(c, header_fill)
        par = c.paragraphs[0]
        par.paragraph_format.space_after = Pt(2)
        par.paragraph_format.space_before = Pt(2)
        r = par.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for n, row in enumerate(rows):
        cells = t.add_row().cells
        for i, val in enumerate(row):
            if n % 2 == 1:
                shade(cells[i], "F6F7F9")
            par = cells[i].paragraphs[0]
            par.paragraph_format.space_after = Pt(2)
            par.paragraph_format.space_before = Pt(2)
            mono = val.startswith("`") and val.endswith("`")
            r = par.add_run(val.strip("`"))
            r.font.size = Pt(10)
            if mono:
                r.font.name = MONO
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return t


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def h1(t): doc.add_heading(t, level=1)
def h2(t): doc.add_heading(t, level=2)
def h3(t): doc.add_heading(t, level=3)


# ===========================================================================
#  COVER
# ===========================================================================

p()
p("SPORTSONE", size=27, bold=True, colour=RED, space_after=2,
  align=WD_ALIGN_PARAGRAPH.CENTER)
p("The Publishing Tool", size=21, colour=INK, space_after=4,
  align=WD_ALIGN_PARAGRAPH.CENTER)
p("Writing, placing and publishing a story from your own laptop",
  size=12.5, italic=True, colour=GREY, align=WD_ALIGN_PARAGRAPH.CENTER,
  space_after=22)

p("Written for journalists, for Windows 10.", size=12.5, bold=True)
p("There is no code in this guide. If you can fill in a form and click a "
  "button, you can publish on SportsOne. You will not open VS Code, you will "
  "not write Markdown, you will not touch GitHub, and you will not type a "
  "single command except during the one-off setup in section 2.")

p("Keep this open the first two or three times you publish. After that you "
  "will not need it.")

callout("The one-minute version",
        "Double-click Start-Publishing-Tool.bat. Your browser opens. Type the "
        "headline, the sub-headline and the story. Add the photograph. Choose "
        "the sport. Choose where on the site it goes and in which position. "
        "Look at the preview on the right — that is the real website. Click "
        "Publish, then Publish to SportsOne. The story is live in two or "
        "three minutes.")

h2("What is in this guide")
table(
    ["Section", "", "What it answers"],
    [["1", "What the tool is", "What it does, and what it deliberately does not do."],
     ["2", "Setting up, once", "The three programs, and connecting to GitHub."],
     ["3", "Starting and stopping", "The black window, and what it means."],
     ["4", "The screen", "What each half of it is for."],
     ["5", "Writing the story", "Headline, sub-headline, body. Typing or from a file."],
     ["6", "The photograph", "One picture, any size. The tool does the rest."],
     ["7", "Filing it", "Sport, section, date and the web address."],
     ["8", "Where it appears", "Placement and position — the important one."],
     ["9", "The preview", "Three views of the real site."],
     ["10", "Edit and preview again", "Going round the loop."],
     ["11", "Save draft", "Stopping half way and coming back."],
     ["12", "Publishing", "The confirmation screen and what happens next."],
     ["13", "Live scores", "Choosing which matches lead the strip."],
     ["14", "Changing a published story", "Corrections and taking a story down."],
     ["15", "When something looks wrong", "The handful of things that go wrong."],
     ["16", "The checklist", "One page. Print it."],
     ["A", "Every place on the site", "All twelve slots and what each holds."],
     ["B", "Where the tool puts things", "For the record. You never need it."]],
    widths=[0.6, 2.3, 4.1])

page_break()

# ===========================================================================
h1("1 · What the tool is")

p("SportsOne is built by a program called Hugo. Hugo turns a folder of text "
  "files into the website readers see. That has not changed and is not going "
  "to change.")

p("What has changed is that you no longer have to write those text files "
  "yourself. The tool is a form. You fill it in, and it writes the files "
  "exactly the way the website expects them.")

rich(("The preview is not a drawing of the website. It ", {}),
     ("is", {"bold": True, "italic": True}),
     (" the website.", {"bold": True}))
p("This is the part worth understanding, because it is what makes the tool "
  "trustworthy. When you look at the right-hand side of the screen, you are "
  "looking at SportsOne, built by Hugo, on your laptop, from the same "
  "templates, the same stylesheet and the same fonts that build the live "
  "site. Nothing has been redrawn or approximated. If it looks right in the "
  "preview it will look right to a reader, because it is the same page.")

h2("What it does")
bullets([
    ("Writes the story.", "Headline, sub-headline, body, photograph, sport, section, tags, byline."),
    ("Places the story.", "Which part of the site it appears in, and in which position."),
    ("Shows you both.", "The story page, the front page, and the sport page, before anyone else sees them."),
    ("Publishes.", "One button. It files everything, sends it to GitHub, and the site rebuilds itself."),
    ("Pins live scores.", "Chooses which matches lead the strip on the front page."),
])

h2("What it deliberately does not do")
p("It is a publishing tool, not a newsroom system. There are no user "
  "accounts, no permissions, no approval chain, no analytics, no comments, "
  "no adverts, no subscribers and no database. Everything it knows lives in "
  "the project folder, in the same files the website has always used.")

h2("The Inbox still works")
p("The older way of publishing — dropping a text file and a photograph into "
  "the inbox folder, or uploading them on github.com — has not been removed "
  "and still does exactly what it always did. It is described in the other "
  "guide, Publishing-Guide.docx. Use whichever suits the moment. The tool is "
  "better at the desk; the inbox is better from a press box on a phone.")

page_break()

# ===========================================================================
h1("2 · Setting up, once")

p("This section is the only place in the guide where you type anything. You "
  "do it once, on this laptop, and then never again. Budget twenty minutes.")

h2("2.1 · The three programs")

p("The tool needs three things on the computer. All three are free, and all "
  "three install with one line each.")

table(
    ["What", "What it is for", "Type this"],
    [["Python", "Runs the tool itself.", "`winget install Python.Python.3.12`"],
     ["Hugo", "Builds SportsOne, and draws every preview.", "`winget install Hugo.Hugo.Extended`"],
     ["Git", "Sends the finished story to GitHub.", "`winget install Git.Git`"]],
    widths=[1.0, 3.0, 3.0])

p("To type them:", space_after=4)
steps([
    "Click the Start button.",
    'Type the words  command prompt  and press Enter.',
    "A black window opens. Paste one of the lines above into it and press "
    "Enter. Wait for it to finish.",
    "Do the same for the other two.",
    "Close the black window when all three are done.",
])

callout("Close the window afterwards, and open a new one",
        "Windows only notices a newly installed program in windows that are "
        "opened afterwards. If you install something and then immediately try "
        "to use it in the same window, it will say it cannot be found. Close "
        "the window, open a new one, and it will be there.")

h3("Checking they are really there")
p("Open a new command prompt and type these three lines, one at a time. Each "
  "should print a version number rather than an error.")
code(["python --version",
      "hugo version",
      "git --version"])

h2("2.2 · Connecting the folder to GitHub")

p("The tool writes your story into the project folder on this laptop. To get "
  "it onto sportsone.world it hands the story to Git, which sends it to "
  "GitHub, which rebuilds the site. So the folder has to know which "
  "repository on GitHub it belongs to.")

rich(("If somebody already set this laptop up — if you have ever published "
      "from it, or opened the project in VS Code and used ", {}),
     ("Publish everything", {"bold": True}),
     (" — then this is already done and you can skip to section 3. The tool "
      "tells you either way the moment it starts: look at the top right of "
      "the screen for a green ", {}),
     ("connected to GitHub", {"bold": True}), (" badge.", {}))

p("If it is not connected, open a command prompt in the project folder and "
  "run these, replacing the address with your own repository's:", space_after=4)
code(["cd C:\\dev\\sportsone-world",
      "",
      "git init -b main",
      "git add .",
      'git commit -m "First commit"',
      "git remote add origin https://github.com/YOURNAME/sportsone-world.git",
      "git push -u origin main"])

p("If GitHub asks for a password, it does not want your account password — "
  "it wants a Personal Access Token. The simplest way round this is to "
  "install GitHub's own helper, which handles it for you:", space_after=4)
code(["winget install GitHub.cli", "gh auth login"])

callout("The tool never sees your password",
        "No password, token or key is ever typed into the tool, stored by it, "
        "or sent to your browser. When you press Publish it asks Git to do "
        "the sending, and Git uses the credentials Windows already has. If "
        "Git cannot sign in, the tool says so plainly and publishes nothing.",
        fill="EAF3EA", accent=GREEN)

page_break()

# ===========================================================================
h1("3 · Starting and stopping the tool")

h2("Starting it")
steps([
    "Open the sportsone-world folder.",
    "Double-click  Start-Publishing-Tool.bat",
    "A black window opens and works for a few seconds.",
    "Your browser opens on its own, at an address beginning localhost.",
])

figure("fig-tool-window.png",
       "Figure 1 — the black window. Leave it open. It is the tool running.",
       width=6.4)

p("The two lines worth reading in that window are the address the tool is "
  "open at, and whether publishing to GitHub is set up.")

callout("Leave the black window open",
        "That window IS the tool. Closing it stops the tool and the preview, "
        "and the browser tab will stop working. Minimise it if it is in the "
        "way. Nothing you have saved is lost when it closes — the story is "
        "already written into the project — but you will have to start it "
        "again to carry on.")

h2("If the browser does not open by itself")
p("Open Google Chrome and type the address from the black window into the "
  "bar at the top:")
code(["localhost:1314"])

h2("Stopping it")
p("Close the black window, or click on it and press Ctrl and C together. "
  "The browser tab can be closed at any time; it does not stop anything.")

h2("If it says a program is missing")
p("The window will name which one and give you the line to install it. That "
  "is section 2.1 again. Install it, close the window, and double-click the "
  "file a second time.")

page_break()

# ===========================================================================
h1("4 · The screen")

figure("fig-tool-open.png", "Figure 2 — the tool as it opens.")

p("The screen is in two halves and they never move.")

table(
    ["Side", "What it is"],
    [["Left", "The form. Four numbered steps, from the headline at the top to "
              "where the story appears at the bottom, then Save draft and "
              "Publish."],
     ["Right", "The real SportsOne website, on your laptop. It changes about "
               "a second after you stop typing."]],
    widths=[0.9, 6.1])

p("Along the very top there are three views:")
bullets([
    ("Write a story", "the form and the preview. Where you will spend all your time."),
    ("All stories", "everything already on the site, and where each one is placed. This is how you edit something you published earlier."),
    ("Live scores", "which matches lead the strip on the front page."),
])

p("At the top right is a badge saying whether publishing is set up. Green "
  "means the tool can send stories to the website. Red means it can still "
  "write and preview them, but not publish — see section 2.2.")

page_break()

# ===========================================================================
h1("5 · Writing the story")

figure("fig-tool-written.png",
       "Figure 3 — a headline, a sub-headline and a story. The preview has "
       "not been opened yet; it fills in on its own.")

h2("The three boxes")

table(
    ["Box", "What it is", "Where the reader sees it"],
    [["Headline", "The title of the story.", "The story page, every card, the front page, Google."],
     ["Sub-headline", "One or two sentences saying what happened.",
      "Printed under the headline on the story page, under the headline on "
      "every card, and as the description in Google."],
     ["The story", "The words.", "The story page."]],
    widths=[1.2, 2.6, 3.2])

callout("The sub-headline is worth the thirty seconds",
        "It is the single most-read sentence you write. It appears under the "
        "headline on the article, under the headline on every card across the "
        "site, and it is what Google prints beneath the link. A story without "
        "one still publishes, and the tool will warn you, but readers see a "
        "gap where the sentence should be.")

h2("Writing the story itself")
p("Plain sentences, with a blank line between paragraphs. That is all you "
  "need. Three extras are worth knowing, and there are buttons for all "
  "three above the box:")

table(
    ["Button", "What it gives you", "What it types"],
    [["H", "A sub-heading inside the story", "`## `"],
     ["B", "Bold words", "`**like this**`"],
     ["•", "A bullet list, one line per bullet", "`- `"],
     ["“", "A quotation, set apart from the story", "`> `"]],
    widths=[0.8, 3.3, 2.9])

p("Select some words first and the button wraps them. Otherwise it starts a "
  "new line for you.")

h2("Loading a story from a text file")
rich(("If the story is already written in Notepad or Word, click ", {}),
     ("Load a .txt file", {"bold": True}),
     (" above the story box and choose it. The tool reads it exactly the way "
      "the inbox does: the first line becomes the headline, the next "
      "paragraph becomes the sub-headline, and the rest becomes the story.", {}))

p("If the file has settings lines at the top — Headline:, Sport:, Photo "
  "source: and so on, as described in the other guide — those are read too "
  "and the matching boxes are filled in for you.")

callout("Word documents do not work; plain text does",
        "In Word use File ▸ Save As and choose Plain Text (.txt). Word's own "
        ".docx format cannot be read, by the tool or by the website.")

page_break()

# ===========================================================================
h1("6 · The photograph")

figure("fig-tool-photo.png",
       "Figure 4 — the picture filed, and the line underneath saying what "
       "the tool did with it.")

rich(("Click ", {}), ("Choose a picture", {"bold": True}),
     (" and pick the photograph. One landscape picture, as large as you have. "
      "That is the whole brief.", {}))

p("You never crop anything, never resize anything and never save a second "
  "copy. The moment you choose it, the tool files it at the three sizes the "
  "website serves — one for the story page, one for the big rotating panels, "
  "one for the small cards — and tells you what it did. The website then "
  "cuts whichever it needs into whatever shape each slot on the page wants.")

h2("The rules")
table(
    ["", "What to send", "Why"],
    [["Size", "2400 pixels across or more",
      "Anything under 1600 looks soft on a large screen, and the tool says so."],
     ["Shape", "Landscape — wider than it is tall",
      "Every slot on the site is landscape or square. A portrait picture "
      "loses its top and bottom, and the tool warns you."],
     ["Format", "JPG or PNG", "Both are turned into a fast, compressed JPG."],
     ["Composition", "Keep the action near the middle",
      "Every crop is taken from the centre. Keep the subject inside the "
      "middle 55% and every shape on the site works."],
     ["File size", "Do not worry about it",
      "Send the camera file. A 12MB original is fine."]],
    widths=[1.0, 2.2, 3.8])

h2("The three lines underneath")
table(
    ["Box", "What it is for"],
    [["What is in the picture",
      "A plain description, for readers who cannot see it. Always worth "
      "filling in. If you leave it blank the tool warns you."],
     ["Caption", "The line printed under the photograph on the story page."],
     ["Agency", "Who the picture came from — Getty Images, Reuters, AP. One "
                "or two words. Never a web address; if you paste a link in, "
                "the website prints nothing rather than printing the link."]],
    widths=[1.9, 5.1])

h2("A story with no photograph")
p("It still publishes. The site shows its own grey placeholder and the tool "
  "warns you before you publish, so it is a decision rather than an "
  "accident.")

page_break()

# ===========================================================================
h1("7 · Filing it")

p("Step 3 on the form is the metadata — the handful of settings that decide "
  "which pages the story turns up on.")

table(
    ["Box", "What it does", "If you leave it"],
    [["Sport", "Puts the story on that sport's page, and in that sport's "
               "block on the front page.", "It files under Other Sports."],
     ["Published", "The date and time on the story.", "Now, which is almost always right."],
     ["Section", "A second label — Premier League, Analysis, Match Reports. "
                 "Its own page builds itself.", "Just the sport."],
     ["Tags", "Comma separated. Each tag gets its own page.", "No tags."],
     ["Byline", "Who wrote it.", "SportsOne Desk."],
     ["Web address", "Hidden under 'Web address'. Choose the address yourself.",
      "One is made from the headline."]],
    widths=[1.2, 3.5, 2.3])

callout("Never set the date in the future",
        "SportsOne is built with future stories switched off. A story dated "
        "even ten minutes from now builds to nothing at all — the address "
        "returns a 'page not found' and stays that way until somebody "
        "rebuilds the site after that time. It is the easiest way there is to "
        "publish silence. The tool refuses to publish a future-dated story "
        "and tells you why, but the simplest rule is to leave the date alone.",
        fill="FDECEC", accent=RED)

page_break()

# ===========================================================================
h1("8 · Where it appears")

p("This is the part of the tool that matters most, and it is the part worth "
  "reading twice.")

h2("Every story is already on the site")
p("You do not have to place a story anywhere. Every story you publish is in "
  "Latest News and on its sport's page automatically, newest first, from the "
  "moment it goes out. Step 4 is only for putting a story somewhere "
  "prominent.")

h2("Placement and position are two different things")

table(
    ["", "The question it answers", "Example"],
    [["Placement", "Which part of the site?", "Homepage → Spotlight"],
     ["Position", "Where inside it?", "Position 2 — second of the five"]],
    widths=[1.2, 3.1, 2.7])

rich(("Click ", {}), ("+ Choose a place on the site", {"bold": True}),
     (". You get two dropdowns: the place on the left, the position on the "
      "right. Choose both.", {}))

figure("fig-tool-order.png",
       "Figure 5 — Spotlight, position 2. Underneath, how that slot will "
       "read once this story is in it.", width=6.0)

h2("Reading the running order")
p("Under the two dropdowns the tool shows the slot as it will read once your "
  "story is in it. Your story is the line in red. The stories above and "
  "below it are the ones already there, in the order a reader will meet "
  "them. Change the position and the list rearranges itself immediately.")

p("This is the whole point: you are making the editorial decision by looking "
  "at the running order, not by guessing and checking afterwards.")

h2("What happens to the story at the bottom")
p("Every slot holds a fixed number of stories. Spotlight holds five. If it "
  "is already full and you put a sixth in at position 2, the story that was "
  "fifth drops out of the slot. The tool draws a line through it and says so "
  "in a sentence underneath before you commit to anything.")

p("Nothing is deleted. A story pushed out of a slot goes back to being an "
  "ordinary story — still on the site, still in Latest News, still on its "
  "sport page, just no longer in that prominent position.")

callout("Pushing a story out cannot be undone from the tool",
        "If you take the fifth story out of Spotlight and later want it back, "
        "you have to put it back yourself: All stories ▸ Edit ▸ choose "
        "Spotlight and a position. The tool always names what it is about to "
        "push out, so you can change your mind before you publish rather "
        "than afterwards.")

h2("More than one place at once")
rich(("Click ", {}), ("+ Choose a place on the site", {"bold": True}),
     (" again to add a second placement. A big story can be in Spotlight and "
      "at the top of its sport page at the same time. Each one gets its own "
      "position.", {}))

p("The one thing the site will not do is show the same story twice in the "
  "same run of blocks on the front page. If a story is in Spotlight, the "
  "blocks below skip over it rather than repeating it. That is the website "
  "protecting you and it needs no thought from you.")

h2("A slot the desk has left short")
p("If a slot has room for five and only three have been chosen, the website "
  "fills the last two with the newest stories not already on the page. That "
  "is why the front page is never half empty, and why a story can appear on "
  "it without anybody choosing it.")

page_break()

# ===========================================================================
h1("9 · The preview")

p("The right-hand side is the real website. Along the top of it are tabs, "
  "and which tabs you get depends on what you have chosen.")

table(
    ["Tab", "What it shows"],
    [["The story", "Your article page exactly as a reader will meet it."],
     ["Front page", "The whole front page, with your story in the slot you chose."],
     ["<Sport> page", "That sport's page, with your story where you put it."]],
    widths=[1.6, 5.4])

h2("The story")
figure("fig-tool-preview-article.png",
       "Figure 6 — the article page. Headline, sub-headline, byline, share "
       "row, photograph, caption and credit — the real thing.")

h2("The front page, with your story found for you")
p("On the front page and the sport pages the tool draws a red outline round "
  "your story and flags it, so you never have to hunt for it in a rotating "
  "carousel. It scrolls it into view for you as well.")

figure("fig-tool-highlight.png",
       "Figure 7 — Spotlight, position 2, outlined in red and labelled.",
       width=6.6)

h2("The sport page")
figure("fig-tool-preview-sport.png",
       "Figure 8 — the Football page, with the story in place at the top of "
       "it. The same five stories run the sport's block on the front page.")

h2("Checking it on a phone")
p("The dropdown at the top right of the preview switches between Desktop, "
  "Tablet and Phone. Most readers are on a phone, so it is worth a look "
  "before you publish — particularly at whether the crop of your photograph "
  "still works when it goes tall.")

page_break()

# ===========================================================================
h1("10 · Edit, preview, edit again")

p("There is no separate 'edit mode' and nothing to save before you look. "
  "Type, stop typing, and about a second later the preview catches up. Go "
  "round that loop as many times as you like.")

p("The word underneath the buttons at the bottom of the form tells you where "
  "you are: 'saving…' while it works, then 'saved'.")

callout("Saved does not mean published",
        "Everything you type is written into the project on this laptop "
        "within a second or so, and until you press Publish it is marked as a "
        "draft. Nobody but you can see it. The website does not build drafts, "
        "so a half-finished story cannot reach a reader by accident.",
        fill="EAF3EA", accent=GREEN)

# ===========================================================================
h1("11 · Save draft")

rich(("The ", {}), ("Save draft", {"bold": True}),
     (" button does what the tool is doing anyway, but tells you it has done "
      "it. Use it when you are about to stop for the day.", {}))

p("To come back to a draft:", space_after=4)
steps([
    "Start the tool again.",
    "Click  All stories  along the top.",
    "Find the story — it has an orange Draft badge.",
    "Click  Edit.",
])
figure("fig-tool-stories.png",
       "Figure 9 — All stories. Drafts carry an orange badge; the red badges "
       "show where a story is placed and in which position.")

p("Everything comes back: the words, the photograph, the sport and the "
  "placement you had chosen.")

page_break()

# ===========================================================================
h1("12 · Publishing")

rich(("When the story reads right and it is in the right place, click ", {}),
     ("Publish…", {"bold": True}), (" at the bottom of the form.", {}))

figure("fig-tool-confirm.png",
       "Figure 10 — the confirmation. Everything the tool is about to do, on "
       "one screen.")

p("Read the five lines. They are the whole decision: the headline, the "
  "sport, where it is going, which position, and the photograph. If any of "
  "it is wrong, click Back.")

h2("What stops a story going out")
p("Before it publishes anything the tool checks the story. Two kinds of "
  "message can appear on the confirmation screen:")

table(
    ["", "What it means", "What happens"],
    [["A red ✕", "Something is missing or wrong — no headline, no words, no "
                 "sport, a date in the future, a photograph that has gone "
                 "missing.",
      "The Publish button is switched off until you fix it."],
     ["An orange !", "Worth a look — no sub-headline, no description on the "
                     "picture, a very short story, a portrait photograph.",
      "You can publish anyway. It is a nudge, not a rule."]],
    widths=[0.9, 3.4, 2.7])

callout("It never publishes half a story",
        "If anything fails — a check, the website failing to build, or GitHub "
        "being unreachable — the tool stops and tells you what happened in "
        "plain English. It does not send some of the files and leave the rest.",
        fill="EAF3EA", accent=GREEN)

h2("Then press Publish to SportsOne")
figure("fig-tool-published.png",
       "Figure 11 — published. The address the story will have is a link.")

p("In the two seconds after you press it, the tool writes the story, files "
  "the photograph, updates the running order of whichever slot you chose, "
  "checks the website still builds, and hands the whole lot to GitHub in a "
  "single change.")

h2("What happens next, and how long it takes")
table(
    ["Step", "How long"],
    [["The tool writes everything and sends it to GitHub", "a few seconds"],
     ["GitHub rebuilds the whole website", "about one minute"],
     ["The new pages reach readers", "one to two minutes after that"],
     ["Total, from pressing the button to a reader seeing it", "two to three minutes"]],
    widths=[5.0, 2.0])

p("You do not have to wait or watch. Once the tool says it has been sent, "
  "the rest happens on its own.")

page_break()

# ===========================================================================
h1("13 · Live scores")

figure("fig-tool-scores.png",
       "Figure 12 — the matches currently in the feed. Tick the ones to lead "
       "the strip.")

p("The scores on SportsOne refresh on their own every fifteen minutes and "
  "need no attention. The one editorial decision is which matches lead the "
  "strip on the front page.")

steps([
    "Click  Live scores  along the top.",
    "Tick the matches you want at the front of the strip.",
    "Click  Save pinned matches.",
])

p("Your ticks survive every refresh for as long as the match is still in the "
  "feed. Tick nothing and the strip fills itself with whatever is live, "
  "which is a perfectly good default and what it does most of the time.")

# ===========================================================================
h1("14 · Changing a story you have already published")

h2("Correcting the words, or the picture, or the placement")
steps([
    "Click  All stories.",
    "Find the story and click  Edit.",
    "Change whatever needs changing, and watch the preview.",
    "Click  Publish… and then  Publish to SportsOne.",
])
p("The correction is live in two or three minutes at the same web address. "
  "Readers who already have the link keep it.")

callout("Edit the story — never write it again",
        "If you write the same story a second time from scratch, you get a "
        "SECOND story at a slightly different address, and anyone who shared "
        "the first link keeps seeing the old one. Always go through All "
        "stories ▸ Edit.")

h2("Taking a story off the front page")
p("Edit it, remove the placement with the × beside it, and publish. The "
  "story stays on the site and in Latest News; it just stops being "
  "prominent. The slot fills the gap on its own.")

h2("Taking a story down altogether")
rich(("In ", {}), ("All stories", {"bold": True}),
     (" each story has a ", {}), ("Remove", {"bold": True}),
     (" button beside Edit. It takes two clicks: the first turns the button "
      "red and asks 'Really remove?', the second does it. The story is taken "
      "off the site and out of any slot it was in.", {}))

p("Then publish anything — even a small correction to another story — and the "
  "removal goes out with it. If you have nothing else to publish, ask whoever "
  "maintains the site to send the change up.")

callout("Remove cannot be undone from the tool",
        "There is no waste basket. Removing a story deletes its file. If you "
        "only want it off the front page, edit it and take the placement away "
        "with the × instead — that leaves the story on the site.",
        fill="FDECEC", accent=RED)

h3("Clearing out the sample stories")
p("The site ships with example articles so that the front page has something "
  "in it. When you are ready to run only your own journalism, remove them the "
  "same way, a few at a time. Nothing breaks as you go: a slot that loses a "
  "story fills the gap with the newest one that is not already on the page.")

page_break()

# ===========================================================================
h1("15 · When something looks wrong")

table(
    ["What you see", "What it means", "What to do"],
    [["The badge at the top right says publishing is not set up",
      "The folder is not connected to GitHub.",
      "Section 2.2. Until then you can write and preview but not publish."],
     ["The preview is blank or will not load",
      "Hugo has stopped.",
      "Close the black window, double-click the .bat file again."],
     ["The preview has no styling — plain text on white",
      "The preview server is not answering.",
      "Same fix: close the black window and start it again."],
     ["The Publish button is greyed out",
      "There is a red ✕ on the confirmation screen.",
      "Read it. It names exactly what is missing."],
     ["'That date and time is in the future'",
      "The date is ahead of now, and the site does not build future stories.",
      "Set the date to now. Section 7."],
     ["The story published but is not on the front page",
      "No placement was chosen, or it was pushed out by a later story.",
      "All stories ▸ Edit ▸ choose a place and a position."],
     ["'The story was saved but could not be sent to GitHub'",
      "No internet, or Git cannot sign in.",
      "Nothing is lost. Check the connection and press Publish again."],
     ["Two copies of the same story",
      "It was written twice instead of edited.",
      "Section 14."],
     ["The black window closed instantly",
      "A program is missing.",
      "Open the .bat file again and read what it names. Section 2.1."]],
    widths=[2.0, 2.3, 2.7])

page_break()

# ===========================================================================
h1("16 · The checklist")

p("Print this page and keep it by the desk.", italic=True, colour=GREY)

h2("Before you press Publish")
for line in [
        "The headline reads the way you want it on the front page.",
        "The sub-headline is filled in — one or two sentences.",
        "The story has a blank line between each paragraph.",
        "The photograph is landscape and at least 1600 pixels across.",
        "'What is in the picture' is filled in.",
        "The agency is named, in one or two words.",
        "The sport is right.",
        "The date says today, not a date in the future.",
        "You have read the story back in the preview.",
        "If it belongs somewhere prominent, the placement AND the position "
        "are set.",
        "You have looked at the running order and you are happy with what it "
        "pushes out.",
        "You have looked at the front page tab and seen it in place.",
        "You have had one look at it on Phone."]:
    rich(("☐   ", {"size": 12}), (line, {}), space_after=3, indent=0.12)

h2("After you publish")
for line in [
        "The tool said 'Published' and gave you the address.",
        "Two or three minutes later, the address opens on sportsone.world.",
        "The front page shows it where you put it."]:
    rich(("☐   ", {"size": 12}), (line, {}), space_after=3, indent=0.12)

page_break()

# ===========================================================================
h1("Appendix A · Every place on the site")

p("These are the twelve slots the tool offers. They are not invented for the "
  "tool — each one is a real list the website already reads, and 'holds' is "
  "the number that part of the page actually shows.")

h2("The front page")
table(
    ["Slot", "Holds", "Where it is"],
    [["Spotlight", "5", "The rotating stories at the very top of the front page."],
     ["Top Stories — the big panel", "4", "The large rotating panel on the left of Top Stories."],
     ["Top Stories — the four beside it", "4", "The four stories stacked down the right."],
     ["Editor's Picks", "6", "Six stories, two to a row, beside More Headlines."]],
    widths=[2.5, 0.7, 3.8])

h2("Each sport — Cricket, Football, Tennis and Other Sports")
table(
    ["Slot", "Holds", "Where it is"],
    [["<Sport> — the rotating five", "5",
      "The carousel at the top of that sport's page, AND that sport's block "
      "on the front page. Choosing it once does both."],
     ["<Sport> — the two underneath", "2",
      "The two fixed stories directly below that carousel."]],
    widths=[2.5, 0.7, 3.8])

p("More Headlines, and the Latest News feed, are not in the list because "
  "nobody chooses them: they fill themselves with the newest stories that "
  "are not already somewhere else on the page.")

# ===========================================================================
h1("Appendix B · Where the tool puts things")

p("For the record. You never need this to publish, but it is here so that "
  "nothing the tool does is a mystery.")

table(
    ["What you did", "What the tool wrote"],
    [["Wrote a story about football",
      "`content/posts/football/your-headline.md`"],
     ["Added a photograph",
      "`static/images/photos/your-headline.jpg` — plus -panel and -card copies"],
     ["Chose Homepage → Spotlight, position 2",
      "`data/homepage.yaml`  — your address added as the 2nd line under spotlight:"],
     ["Chose Cricket → the rotating five",
      "`data/sports.yaml`  — under cricket: carousel:"],
     ["Pinned a live match",
      "`data/scores.yaml`  — under featured_matches:"],
     ["Pressed Publish",
      "One commit in Git containing exactly those files, pushed to GitHub"]],
    widths=[2.6, 4.4])

p("These are the same files the website has always used, in the same shape, "
  "with every plain-English note in them left exactly where it was. Anyone "
  "who has edited them by hand before can still do so, and the tool will "
  "read what they wrote.")

p()
p("SportsOne · The Publishing Tool", size=9.5, colour=GREY,
  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
p("Rebuild this document with:  python3 scripts/make-tool-guide.py",
  size=9.5, colour=GREY, align=WD_ALIGN_PARAGRAPH.CENTER, mono=True)

doc.save(OUT)
print(f"Wrote {OUT.relative_to(ROOT)}")
