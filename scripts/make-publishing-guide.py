#!/usr/bin/env python3
"""
=============================================================================
 BUILD  docs/Publishing-Guide.docx

     python3 scripts/make-publishing-guide.py

 The guide the newsroom actually reads. Everything in it is written here, so
 the Word file is never edited by hand — change the words below and run this
 again, and the whole document is rebuilt, screenshots and all.

 The pictures come from docs/images/. To refresh them after a design change,
 re-run the figure scripts that made them (see docs/images/README.md).

 Needs:  pip install python-docx
=============================================================================
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor
except ImportError:
    sys.exit("This needs python-docx.  Run:  pip install python-docx")

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "docs" / "images"
OUT = ROOT / "docs" / "Publishing-Guide.docx"

INK = RGBColor(0x11, 0x14, 0x1A)
GREY = RGBColor(0x5A, 0x62, 0x70)
RED = RGBColor(0xC8, 0x1E, 0x2B)
GREEN = RGBColor(0x14, 0x6B, 0x43)
BODY = "Calibri"
MONO = "Consolas"

doc = Document()

# --- page and base styles ---------------------------------------------------
for s in doc.sections:
    s.top_margin = s.bottom_margin = Inches(0.8)
    s.left_margin = s.right_margin = Inches(0.85)
CONTENT_W = 7.0   # inches of usable width

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


# --- small helpers ----------------------------------------------------------
def shade(cell, hexcolour):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), hexcolour)
    cell._tc.get_or_add_tcPr().append(el)


def no_borders(table):
    tbl = table._tbl
    pr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "none")
        e.set(qn("w:sz"), "0")
        borders.append(e)
    pr.append(borders)


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
    """rich(("plain ", {}), ("bold", {'bold': True}))"""
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
    """A block of exactly what to type."""
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
for _ in range(3):
    doc.add_paragraph()
par = doc.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = par.add_run("SPORTSONE"); r.bold = True; r.font.size = Pt(15)
r.font.color.rgb = RED
par.paragraph_format.space_after = Pt(4)

par = doc.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = par.add_run("The Publishing Guide"); r.bold = True; r.font.size = Pt(40)
par.paragraph_format.space_after = Pt(10)

par = doc.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = par.add_run("Putting a story on sportsone.world, start to finish")
r.font.size = Pt(15); r.font.color.rgb = GREY
par.paragraph_format.space_after = Pt(34)

t = doc.add_table(rows=1, cols=1)
c = t.cell(0, 0)
shade(c, "F4F5F7")
par = c.paragraphs[0]
par.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = par.add_run("Written for journalists.")
r.bold = True; r.font.size = Pt(13)
par2 = c.add_paragraph(); par2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = par2.add_run(
    "There is no code in this guide and nothing to learn by heart. If you can "
    "save a file and drag it into a folder, you can publish on SportsOne.")
r2.font.size = Pt(11.5)
par3 = c.add_paragraph(); par3.alignment = WD_ALIGN_PARAGRAPH.CENTER
r3 = par3.add_run(
    "Words like Hugo, Git, GitHub, Markdown, repository, commit, build and "
    "deploy appear nowhere except where you have to click a button with that "
    "name on it — and then the guide shows you the button.")
r3.font.size = Pt(11.5); r3.font.color.rgb = GREY

doc.add_paragraph()
par = doc.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = par.add_run("Keep this open the first three or four times. After that you "
                "will not need it.")
r.italic = True; r.font.size = Pt(11); r.font.color.rgb = GREY

page_break()

# ===========================================================================
h1("What is in this guide")
p("Read sections 1 to 6 before you publish anything. The rest you can look up "
  "when you need it.")

table(["", "Section", "What it answers"],
      [["1", "Getting a story onto the site",
        "The two ways to do it. Pick one and stay with it."],
       ["2", "The folder, and the one rule",
        "How the website knows which picture belongs to which story."],
       ["3", "What goes in the text file",
        "The headline, the summary, the sport, the caption, the credit."],
       ["4", "The picture",
        "How big, what shape, and why you never have to crop anything."],
       ["5", "What the import tells you",
        "Reading the report, and the two or three things it might ask of you."],
       ["6", "Where your story goes after you publish",
        "Every page it appears on, and how long it takes."],
       ["7", "The front page, and how to get on it",
        "Every slot, what it holds, and the line you type to claim one."],
       ["8", "Deciding which story is first",
        "Editorial priority, and putting a premium story at the top."],
       ["9", "The sport pages", "What leads Cricket, Football, Tennis and Other Sports."],
       ["10", "Changing a story you have already published",
        "Corrections, new pictures, and taking something down."],
       ["11", "The pages that are not stories",
        "About, Contact, the footer and the toolbar."],
       ["12", "The article page, part by part",
        "Which line in your file becomes which part of the page."],
       ["13", "Picture credits", "The rule, and what to type."],
       ["14", "When something looks wrong", "The handful of things that go wrong, and the fix."],
       ["15", "The checklist", "One page. Print it."],
       ["", "Appendix", "Every line you can put at the top of a text file."]],
      widths=[0.4, 2.5, 4.1])

callout("The one-minute version",
        "Write the story in Word, Notepad or anything else, and save it as a "
        "plain text file. Save the photograph next to it with exactly the same "
        "name. Put both in the inbox folder. Run the import, or upload them to "
        "the inbox on github.com. Two or three minutes later the story is live.")

page_break()

# ===========================================================================
h1("1 · Getting a story onto the site")
p("There are two routes and they do exactly the same thing. Route A runs on "
  "the newsroom laptop. Route B runs in a web browser and needs nothing "
  "installed at all — you can do it from a phone in a press box.")
figure("fig-routes.png", "Figure 1 — the two routes. They produce identical results.")

h2("Route A · on the newsroom laptop")
steps([
    "Open the sportsone-world folder, then open the folder inside it called inbox.",
    "Drag your text file and your photograph into it. Both files, together.",
    "Go back up one folder and double-click Import-Articles.bat. A black window "
    "opens, works for a few seconds, and prints a report. Read the last part of "
    "it. (If you work in VS Code, the same thing is Terminal ▸ Run Task ▸ "
    "\"6 · Import from the Inbox\". To see what it would do without it doing "
    "anything, run \"7 · Rehearse the Inbox import\" first.)",
    "Press a key to close that window.",
    "Double-click Edit-Website.bat and wait for your browser to open. Read your "
    "story back. Nobody else can see this — it is only on your machine.",
    "Publish. In VS Code that is Terminal ▸ Run Task ▸ \"3 · Publish everything\", "
    "and it asks you for one line describing what you changed. Two or three "
    "minutes later the stories are on sportsone.world.",
])
callout("Nothing is lost if you get it wrong",
        "The import never overwrites an existing story and never deletes a "
        "picture. If it cannot use one of your files it leaves it in the inbox "
        "and tells you why.", fill="EAF6EF", accent=GREEN)

h2("Route B · on github.com, from any browser")
steps([
    "Sign in at github.com and open the SportsOne project.",
    "Click the folder called inbox.",
    "Click the Add file button, then Upload files.",
    "Drag your text file and your photograph onto the page.",
    "Scroll down and click the green Commit changes button.",
])
p("That is the whole job. Everything after that happens on its own: the picture "
  "is resized, the story is filed, the front page is updated if you asked for it, "
  "and the site republishes itself. Give it about three minutes.")
rich(("To see what happened, click the ", {}),
     ("Actions", {"bold": True}),
     (" tab at the top of the page and open the newest run called ", {}),
     ("Import from the Inbox", {"bold": True}),
     (". It prints the same plain-English report as Route A.", {}))

page_break()

# ===========================================================================
h1("2 · The folder, and the one rule")
p("A story is two files. A text file with the words in it, and a photograph. "
  "They must have the same name. That is the only thing that connects them, and "
  "it is the only rule in this guide you have to remember.")
figure("fig-inbox.png", "Figure 2 — six files, three stories.")

h2("What counts as the same name")
bullets([
    ("The ending does not matter.", "Article-1.md and Article-1.png are a pair. "
     "So are Article-1.txt and Article-1.jpeg."),
    ("Capital letters do not matter.", "Article 1.MD finds article-1.jpg."),
    ("Spaces and dashes do not matter.", "City v United.txt finds city-united.jpg."),
    ("Everything else does matter.", "Article-1.md and Article-01.png are two "
     "different things and will not pair up."),
])
h2("Which file types work")
table(["For the words", "For the picture"],
      [[".md   ·   .txt   ·   .markdown", ".jpg   ·   .jpeg   ·   .png   ·   .webp"]],
      widths=[3.0, 4.0])
p("If you write in Word, use File ▸ Save As and choose Plain Text (.txt). Word's "
  "own .docx format is not read by the website.", size=11, colour=GREY)

h2("A story with no picture")
p("It still publishes. The site shows its own placeholder image and the report "
  "tells you which story is missing a photograph, so you can add one later.")

h2("A picture with no story")
p("It is left in the inbox, untouched, and named in the report. Usually this "
  "means the two files were spelled slightly differently.")

page_break()

# ===========================================================================
h1("3 · What goes in the text file")
p("At its simplest, nothing special at all. This is a complete, working article:")
code(["Six wickets before lunch and a Test that lasted two days",
      "",
      "England were bowled out twice inside two sessions on a pitch",
      "that never settled.",
      "",
      "The first innings lasted 27 overs. The second lasted 24. Nobody",
      "reached thirty in either of them."])
bullets([
    "The first line is the headline.",
    "The next paragraph becomes the summary — the sentence readers see on cards "
    "and in Google.",
    "Everything after that is the story.",
])

h2("Saying more")
p("To choose the sport, the caption, the credit or a place on the front page, "
  "put a few lines at the top, then ONE BLANK LINE, then the story:")
code(["Headline: Riverside hold on for a first win of the season",
      "Sport: Football",
      "Section: Premier League",
      "Summary: Two goals in four minutes either side of the interval.",
      "Photo caption: Ellis celebrates the opening goal.",
      "Photo description: Ellis runs towards the corner flag, arms out.",
      "Photo source: Getty Images",
      "Front page: Top stories",
      "Order: 1",
      "",
      "Riverside had not won since the opening weekend. They led inside",
      "three minutes and did not have a shot on target after that.",
      "",
      "## The goals",
      "",
      "Ellis turned in at the near post from a corner."])
callout("The blank line matters",
        "Without a blank line between the last of those lines and the first "
        "line of your story, the website cannot tell where the settings stop "
        "and the journalism starts.")

h2("The lines you will use most")
table(["Type this", "What it does", "If you leave it out"],
      [["`Headline:`", "The title of the story",
        "The first line of the file is used"],
       ["`Summary:`", "The sentence under the headline, on cards and in Google",
        "The first paragraph is used"],
       ["`Sport:`", "Cricket, Football or Tennis",
        "It files under Other Sports"],
       ["`Section:`", "A second label — Premier League, Analysis, Match Reports",
        "Just the sport"],
       ["`Photo caption:`", "The line printed under the picture", "No caption"],
       ["`Photo description:`",
        "What is in the picture, for readers who cannot see it", "The headline is used"],
       ["`Photo source:`", "The agency: Getty Images, Reuters, AP", "No credit line"],
       ["`Front page:`", "Spotlight, Top stories, Beside top, Editor's picks",
        "Latest news only"],
       ["`Order:`", "1 puts it first in that slot, 2 second", "It goes in first"],
       ["`Author:` `Role:`", "The byline", "SportsOne Desk"],
       ["`Tags:`", "Comma separated: Ashes, England, Day two", "No tags"],
       ["`Hold: yes`", "Import it but keep it off the site until you are ready",
        "It publishes"]],
      widths=[1.75, 3.35, 1.9])
p("The full list, including the ones you will rarely need, is in the Appendix.",
  size=11, colour=GREY)

h2("Writing the story itself")
p("Plain sentences and blank lines between paragraphs are all you need. Three "
  "extras are worth knowing:")
table(["To get", "Type"],
      [["A sub-heading", "`## The goals`"],
       ["Bold", "`**seventy minutes**`"],
       ["A bullet list", "`- one line per bullet, each starting with a dash`"]],
      widths=[2.4, 4.6])

page_break()

# ===========================================================================
h1("4 · The picture")
p("One landscape photograph per story, as big as you have. That is the whole "
  "brief. You never crop anything, you never resize anything and you never "
  "save a second copy — the website does all three, every time, for every "
  "place the picture appears.")
figure("fig-crops.jpg",
       "Figure 3 — the same photograph, cut automatically to five different shapes.")

h2("The rules")
table(["", "What to send", "Why"],
      [["Size", "2400 pixels across or more",
        "Anything under 1600 goes soft on a large screen and the import says so. "
        "There is no upper limit — send the camera file."],
       ["Shape", "Landscape — wider than it is tall",
        "Every slot on the site is landscape or square. A portrait picture loses "
        "its top and bottom."],
       ["Format", "JPEG or PNG",
        "Both are converted to a fast, compressed JPEG on the way in."],
       ["Composition", "Keep the action near the middle",
        "Every crop is taken from the centre. The green box in Figure 3 is what "
        "always survives."],
       ["File size", "Do not worry about it",
        "A 12 MB camera file is filed at three sizes — one for the story page, "
        "one for the front-page banners and one for the small cards — and the "
        "right one is served to each. You never see or name the other two."]],
      widths=[1.1, 2.3, 3.6])

h2("Which shape each part of the site uses")
p("You do not have to supply any of these. They are here so you know what the "
  "crop will do to your photograph.")
table(["Where on the site", "Shape it is cut to", "What that means for you"],
      [["Front-page Spotlight banner", "21 : 9 on a wide screen",
        "Very wide. Anything near the top or bottom edge is lost."],
       ["Front-page Spotlight, on a phone", "4 : 5",
        "Tall. The left and right edges are lost instead."],
       ["Top Stories, the big panel", "1 : 1 on a laptop",
        "Square."],
       ["A sport carousel", "16 : 10, or 21 : 9 on a wide screen",
        "Wide."],
       ["The picture on the story itself", "16 : 9",
        "The standard news shape."],
       ["Cards in the feeds", "16 : 9", "Same again, smaller."],
       ["Headline lists", "1 : 1 thumbnail", "Square, and small."]],
      widths=[2.3, 2.0, 2.7])
callout("If you remember one thing about pictures",
        "Keep the subject in the middle 55% of the frame. Then every crop on "
        "the site works, on every device, without you thinking about it again.",
        fill="EAF6EF", accent=GREEN)

h2("More than one picture in a story")
p("The picture that shares the file's name is the main one, at the top. To put "
  "another one part-way through the story, put that file in the inbox too, with "
  "any name you like, and write this line in the story where you want it:")
code(["![What is in the picture](/images/photos/second-picture.jpg \"The caption\")"])
p("This is the one piece of punctuation in the guide worth copying and pasting "
  "rather than typing.", size=11, colour=GREY)

page_break()

# ===========================================================================
h1("5 · What the import tells you")
p("Whichever route you took, you get the same report. It has three parts: what "
  "it found, what it did with each story, and a short list of anything that "
  "needs you. Read the last part first.")
figure("fig-report.png", "Figure 4 — a real import of three stories.")

h2("The four lines under each story")
table(["Line", "What it is telling you"],
      [["`picture`", "The size of the photograph you sent, the size it was "
        "saved at, and its new name."],
       ["`article`", "Where the story now lives in the project."],
       ["`address`", "The web address it will have. Copy this if you need to "
        "send someone a link."],
       ["`frontpage`", "Which slot it went into, in which position, and which "
        "story it pushed out of that slot."]],
      widths=[1.3, 5.7])

h2("The things to look at")
p("This list is the only part that ever needs a decision from you. There are "
  "four messages it can print.")
table(["What it says", "What to do"],
      [["The picture is only 900px across",
        "The story is published and looks fine on a phone, but only one size was "
        "filed. Ask for a larger copy when you can, then replace it — see "
        "section 10."],
       ["It is a portrait picture",
        "It is published, but cropped top and bottom. Check the story page "
        "before you leave."],
       ["No picture with a matching name",
        "The story is live with a placeholder. Almost always a spelling "
        "difference between the two file names."],
       ["A picture with no article of the same name",
        "Left in the inbox. Same cause, other way round."]],
      widths=[2.7, 4.3])
callout("Nothing in that list stops a story going out",
        "Every one of them is published first and flagged second. The site is "
        "never left half-finished because one photograph was small.",
        fill="EAF6EF", accent=GREEN)

page_break()

# ===========================================================================
h1("6 · Where your story goes after you publish")
p("A common worry is that a story has been uploaded but has not appeared. It "
  "almost always has — in more places than you expected. This is what happens "
  "to it.")
figure("fig-journey.png", "Figure 5 — from your folder to the live site.")

h2("How long it takes")
table(["Step", "How long"],
      [["The import reads your files and writes the story", "a few seconds"],
       ["The whole site is rebuilt — all 254 pages", "about one minute"],
       ["The new pages reach readers", "one to two minutes after that"],
       ["Total, from pressing go to a reader seeing it", "two to three minutes"]],
      widths=[4.6, 2.4])

h2("Finding your story")
bullets([
    ("Its own address", "printed in the import report, next to the word address."),
    ("The Latest feed", "every story is there, newest first, whatever else you "
     "did or did not set."),
    ("Its sport's page", "from the Sport: line. No Sport: line means Other Sports."),
    ("Search", "the magnifying glass in the toolbar finds it within the same few minutes."),
])

h2("Two reasons a story might not be visible")
table(["What you see", "Why"],
      [["Nothing at all, anywhere",
        "You wrote Hold: yes in the text file. Remove that line and publish "
        "again."],
       ["It is in Latest but not on the front page",
        "You did not ask for a slot, or the slot you asked for was already "
        "full of stories set to a higher position. See section 8."]],
      widths=[2.6, 4.4])

page_break()

# ===========================================================================
h1("7 · The front page, and how to get on it")
p("The front page has four slots you can put a story into, plus a set of blocks "
  "that fill themselves. Type one line in the text file to claim a slot.")
figure("fig-map.png", "Figure 6 — every slot on the front page and the line that claims it.")
figure("fig-home-top.jpg", "Figure 7 — the top of the front page.")
figure("fig-home-picks.jpg", "Figure 8 — Editor's Picks and More Headlines.")
figure("fig-home-sport.jpg", "Figure 9 — the sport blocks, further down.")

h2("What happens when a slot is full")
p("Every slot holds a fixed number of stories. Claiming a place in a full slot "
  "pushes the last one out — it is not deleted, it simply goes back to being a "
  "normal story in the feeds. The report always names what was pushed out.")

h2("What happens when a slot is short")
p("If the desk has only named three stories in a slot that holds five, the "
  "website fills the other two with the newest stories that are not already "
  "somewhere on the page. That is why the front page is never half empty, and "
  "why a story can appear on it without anybody asking.")

h2("A story never appears twice")
p("The slots are filled top to bottom, and each one skips anything already "
  "placed above it. You cannot accidentally run the same story in Spotlight and "
  "in Editor's Picks.")

page_break()

# ===========================================================================
h1("8 · Deciding which story is first")
rich(("Two lines control editorial priority. ", {}),
     ("Front page:", {"bold": True, "mono": True}),
     (" chooses which slot. ", {}),
     ("Order:", {"bold": True, "mono": True}),
     (" chooses the position inside it. Order: 1 means first, and everything "
      "already in the slot moves down one place.", {}))
figure("fig-order.png", "Figure 10 — a new story taking the top of the Spotlight banner.")

h2("Putting a premium story at the top of the site")
p("The biggest position on SportsOne is the first Spotlight story. To take it, "
  "write two lines:")
code(["Front page: Spotlight", "Order: 1"])
p("The story that was first becomes second, and whatever was fifth drops out of "
  "the banner. Nothing else on the site changes.")

h2("Ordering a run of stories")
p("On a big day you can set the whole running order at once. Give each story a "
  "different Order:, and import them together:")
table(["Story", "Front page:", "Order:", "Where it lands"],
      [["The result", "Spotlight", "1", "The lead of the whole site"],
       ["The reaction", "Spotlight", "2", "Second in the banner"],
       ["The analysis", "Top stories", "1", "Leads the Top Stories panel"],
       ["The gallery", "Editor's picks", "1", "First of the six picks"],
       ["Everything else", "— leave it out —", "—", "Latest news, newest first"]],
      widths=[1.7, 1.7, 0.8, 2.8])

h2("Taking a story off the front page")
p("Publish a newer story into the same slot. The old one is pushed down and, "
  "once the slot is full again, out. You never have to remove anything by hand.")

page_break()

# ===========================================================================
h1("9 · The sport pages")
p("Cricket, Football, Tennis and Other Sports each have their own page, and each "
  "one is led by five rotating stories and two fixed ones underneath. The same "
  "five also run that sport's block on the front page, so a sport's top stories "
  "are chosen once and are the same wherever a reader meets them.")

h2("How a story reaches a sport page")
rich(("The ", {}), ("Sport:", {"mono": True, "bold": True}),
     (" line, and nothing else. Every story with ", {}),
     ("Sport: Cricket", {"mono": True}),
     (" is on the Cricket page, newest first, ten to a page, for as long as the "
      "site exists.", {}))

h2("Choosing what leads a sport")
p("The five rotating stories and the two beneath them are the desk's choice, "
  "and they are set for the sport rather than for one story. Ask whoever "
  "maintains the site to change them, or make the change yourself in the "
  "sport's settings file — it is a list of story addresses, one per line, in "
  "the order you want them.")
callout("Sections and tags need no setting up",
        "Write Section: Premier League on a story and the Premier League page "
        "builds itself, appears in the Football menu, and gets its own RSS feed. "
        "Write it on a second story and both are there. Nothing else to do.",
        fill="EAF6EF", accent=GREEN)

page_break()

# ===========================================================================
h1("10 · Changing a story you have already published")
h2("Correcting the words")
steps([
    "Find the story's file. The import report gave you its location — for "
    "example content/posts/football/riverside-hold-on.md.",
    "Open it in any text editor, or on github.com click the file and then the "
    "pencil icon.",
    "Change what you need. Leave everything above the second row of dashes "
    "alone unless you meant to change it.",
    "Save, and publish as usual. The correction is live in two or three minutes "
    "at the same web address.",
])
callout("Do not re-import a corrected story",
        "Putting the same story in the inbox a second time creates a SECOND "
        "story at a slightly different address, and readers who shared the "
        "first link keep seeing the old one. Edit the file that is already "
        "there instead.")

h2("Replacing the picture")
p("Save the new photograph over the old one, keeping exactly the same file name, "
  "in static/images/photos/. The story picks it up on the next publish. Nothing "
  "in the story file changes.")

h2("Changing a caption or a credit")
rich(("Open the story file and edit the ", {}),
     ("imageCaption", {"mono": True}), (" or ", {}),
     ("imageSource", {"mono": True}),
     (" line near the top. Those are the same two things you wrote as ", {}),
     ("Photo caption:", {"mono": True}), (" and ", {}),
     ("Photo source:", {"mono": True}), (" in the inbox.", {}))

h2("Taking a story down")
rich(("Add one line under the title: ", {}),
     ("draft: true", {"mono": True, "bold": True}),
     (". Publish. The page disappears from the site and from every feed and "
      "search result, and the file is still there if you want it back — change "
      "that line to ", {}),
     ("draft: false", {"mono": True}), (" and publish again.", {}))

page_break()

# ===========================================================================
h1("11 · The pages that are not stories")
table(["To change", "Open this file", "Notes"],
      [["The About page", "`content/about.md`",
        "Everything under the dashes is the page. Write normally."],
       ["Contact, Terms, Privacy, Accessibility",
        "`content/contact.md` and the others beside it", "Same again."],
       ["The paragraph in the footer", "`hugo.toml`",
        "Find the line beginning about = and change the words between the quotes."],
       ["The toolbar and the menus", "`data/navigation.yaml`",
        "One file drives the toolbar, the drop-downs, the phone menu and all "
        "three footer columns, so they can never disagree."],
       ["What leads each sport", "`data/sports.yaml`",
        "Five rotating stories and two fixed ones per sport."],
       ["What leads the front page", "`data/homepage.yaml`",
        "The same thing for Spotlight, Top Stories and Editor's Picks. The "
        "import edits this for you when you write a Front page: line."],
       ["The videos on a sport page", "`data/videos.yaml`",
        "Three per sport. Paste the part of a YouTube address after watch?v=."],
       ["Which matches lead the scores strip", "`data/scores.yaml`",
        "The scores themselves refresh on their own every fifteen minutes."]],
      widths=[2.0, 2.2, 2.8])
callout("These files are lists, not code",
        "Every one of them is commented in plain English at the top, and a "
        "mistake in one is ignored rather than published — a misspelt story "
        "address is simply skipped and the gap fills itself.")

page_break()

# ===========================================================================
h1("12 · The article page, part by part")
p("Every part of a story page comes from a line you wrote. This is which is which.")
figure("fig-article.jpg", "Figure 11 — a published story, labelled.")

h2("Two things that are on this page and nowhere else")
bullets([
    ("The share icons.", "Facebook, X, WhatsApp, Reddit and a copy-link button, "
     "directly above the main photograph. They are on story pages only — never "
     "on the front page, a sport page or a card, because there is nothing to "
     "share until a reader has chosen a story."),
    ("The byline.", "It appears once, at the top. There is no second byline at "
     "the foot and no reading-time badge."),
])

page_break()

# ===========================================================================
h1("13 · Picture credits")
p("The line under a photograph names the agency the picture came from and "
  "nothing else. It is one or two words, it is not a link, and it never shows a "
  "web address.")
table(["You write", "The reader sees"],
      [["`Photo source: Getty Images`", "Photo via Getty Images"],
       ["`Photo source: Reuters`", "Photo via Reuters"],
       ["`Photo source: AP`", "Photo via AP"],
       ["`Photo source: © Getty`", "© Getty"],
       ["— nothing —", "no line at all"]],
      widths=[3.5, 3.5])

h2("The rules")
bullets([
    "One or two words. Getty Images, Reuters, AP, AFP, PA, Action Images.",
    "Never a web address, and never the words http or https. If you paste a "
    "link in by mistake the website prints nothing rather than printing the link.",
    "No licence codes on the page. Anything like CC BY 2.0 belongs on the Image "
    "Credits page, not under the photograph.",
    "A photograph the desk took itself needs no credit. Leave the line out and "
    "no line is printed.",
])

h2("Where the full attribution lives")
p("Photographer, licence and the original source are all kept, and all listed "
  "on the Image Credits page, which is linked from the footer of every page on "
  "the site. Only what is printed under the photograph has been shortened.")

page_break()

# ===========================================================================
h1("14 · When something looks wrong")
table(["What you see", "What it means", "What to do"],
      [["The story is not on the site at all",
        "Hold: yes is still in the file, or the publish has not finished",
        "Wait three minutes. Then check the file for Hold: yes or draft: true."],
       ["The picture is the grey placeholder",
        "The two file names did not match",
        "Rename the photograph to match the text file exactly and put it in "
        "the inbox again."],
       ["The picture is cut off at the top",
        "It was a portrait photograph, or the subject was near an edge",
        "Send a landscape version with the action nearer the middle."],
       ["The headline is the file name",
        "The file had settings lines at the top but no Headline: line, and the "
        "first line was one of those settings",
        "Add a Headline: line."],
       ["Half the story is missing",
        "There was no blank line between the settings and the story",
        "Add one blank line and import again."],
       ["Two copies of the same story",
        "It was imported twice",
        "Add draft: true to the copy you do not want, and publish."],
       ["The import window closed instantly",
        "It could not start",
        "Read section 1 again — the window stays open and waits for a key "
        "press when it has worked."],
       ["A red cross on the Actions tab",
        "The publish failed",
        "Click the run. The last red line names the file and the line number. "
        "It is almost always a stray quotation mark in a settings line."]],
      widths=[2.0, 2.5, 2.5])

page_break()

# ===========================================================================
h1("15 · The checklist")
p("Print this page and keep it by the desk.", colour=GREY)

h2("Before you put anything in the inbox")
for line in [
    "The text file and the photograph have exactly the same name.",
    "The photograph is landscape and at least 1600 pixels across — 2400 is better.",
    "The action in the photograph is near the middle.",
    "The first line is the headline, or there is a Headline: line.",
    "There is a blank line between the settings and the story.",
    "Sport: says Cricket, Football or Tennis if it is one of those.",
    "Photo source: names the agency, in one or two words.",
    "Photo caption: and Photo description: are both filled in.",
    "If it belongs on the front page, Front page: says which slot.",
]:
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(5)
    r = par.add_run("☐   ")
    r.font.size = Pt(13)
    r.font.name = "Segoe UI Symbol"
    r2 = par.add_run(line)
    r2.font.size = Pt(11.5)

h2("After the import")
for line in [
    "The report says the right number of stories.",
    "The things to look at list is empty, or you know why it is not.",
    "You have opened the story in the preview and read it back.",
    "The photograph is not cut off in a way that matters.",
    "The front page line went where you expected.",
]:
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(5)
    r = par.add_run("☐   ")
    r.font.size = Pt(13)
    r.font.name = "Segoe UI Symbol"
    r2 = par.add_run(line)
    r2.font.size = Pt(11.5)

page_break()

# ===========================================================================
h1("Appendix · every line you can write")
p("All of these go at the top of the text file, above the blank line. Every one "
  "is optional.")
table(["Line", "What it does"],
      [["`Headline:`", "The title. Without it, the first line of the file is used."],
       ["`Summary:`", "One or two sentences. Used on cards, on the front page and in Google."],
       ["`Sport:`", "Cricket, Football, Tennis. Anything else files under Other Sports."],
       ["`Section:`", "A second label — Premier League, Analysis, Match Reports, "
        "Transfer Mania. Its page is built automatically."],
       ["`Tags:`", "Comma separated. Each tag gets its own page."],
       ["`Author:`", "The byline. Defaults to SportsOne Desk."],
       ["`Role:`", "Printed after the byline — Senior cricket writer."],
       ["`Photo caption:`", "The line printed under the picture."],
       ["`Photo description:`", "What is in the picture, for readers using a "
        "screen reader. Always worth filling in."],
       ["`Photo source:`", "The agency. One or two words."],
       ["`Photo credit:`", "The photographer's name. Kept for the Image Credits "
        "page; not printed under the picture."],
       ["`Front page:`", "Spotlight · Top stories · Beside top · Editor's picks. "
        "Leave it out for the Latest feed only."],
       ["`Order:`", "1, 2, 3 … the position inside the slot you asked for."],
       ["`Date:`", "2026-08-28. Leave it out for now. A date in the future keeps "
        "the story hidden until then."],
       ["`Slug:`", "Choose the web address yourself instead of having one made "
        "from the headline."],
       ["`Hold: yes`", "Import it but keep it off the site until you remove the line."]],
      widths=[1.8, 5.2])

doc.add_paragraph()
par = doc.add_paragraph()
par.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = par.add_run("SportsOne · The Publishing Guide")
r.font.size = Pt(10); r.font.color.rgb = GREY
par2 = doc.add_paragraph()
par2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = par2.add_run("Rebuild this document with:  python3 scripts/make-publishing-guide.py")
r2.font.size = Pt(9.5); r2.font.color.rgb = GREY
r2.font.name = MONO

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUT)
print(f"Written {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB)")
