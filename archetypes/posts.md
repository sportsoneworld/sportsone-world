---
# ---------------------------------------------------------------------------
#  SportsOne article
#  Fill this in, write the story below the dashes, set draft to false, save,
#  then commit and push. The website rebuilds and publishes itself.
#  Full guide: docs/Publishing-Guide.docx (start here)
#               docs/02-publishing-and-managing-articles.md (the long version)
# ---------------------------------------------------------------------------

title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
lastmod: {{ .Date }}
draft: true

# One or two sentences. Used on cards, on the homepage and in Google results.
summary: ""

# Optional. Only needed if you want the search-engine description to differ
# from the summary above.
description: ""

# ---------------------------------------------------------------------------
#  Picture
#  Put the file in static/images/photos/ then write the path WITHOUT the word
#  static.  static/images/photos/my-photo.jpg  ->  "/images/photos/my-photo.jpg"
#
#  Send one landscape photograph, 1600px across or more. The site crops it to
#  every shape it needs, always from the centre, so keep the action in the
#  middle of the frame. See docs/Publishing-Guide.docx.
# ---------------------------------------------------------------------------
image: ""
imageAlt: ""          # describe the picture for screen readers — always fill this in
imageCaption: ""      # optional caption printed under the picture
thumbnail: ""         # optional different picture for the small cards

# The one short line printed under the picture: the agency it came from and
# nothing else. "Getty Images", "Reuters", "AP". Never a web address, never a
# licence code, and it is never a link.
imageSource: ""

# The full attribution. Kept for the /credits/ page, not printed under the
# picture. Leave these out for a photograph the desk took itself.
imageCredit: ""       # the photographer
imageCreditURL: ""    # where it came from
imageLicense: ""      # "CC BY 2.0", "Public domain" …
imageLicenseURL: ""

# ---------------------------------------------------------------------------
#  Filing
#  The first category is the one shown on cards and in the breadcrumb.
#  Any new value here automatically creates its own page and navigation entry.
# ---------------------------------------------------------------------------
categories: ["Football"]
tags: []

author: "SportsOne Desk"
authorRole: ""

# ---------------------------------------------------------------------------
#  Where the story appears
#
#  Every story is in the Latest feed, on its sport's page and on the page for
#  each of its categories and tags, without any setting at all.
#
#  The front page is chosen in data/homepage.yaml — Spotlight, the Top Stories
#  panel, the four beside it, and Editor's Picks. Add the slug there, or write
#  a "Front page:" line when importing from inbox/ and it is done for you.
#  What leads each sport is chosen in data/sports.yaml, the same way.
#
#  `weight` below pins a story to the top of the blocks that fill themselves —
#  1 first, 2 second, and so on. 0 means "no pin, newest first".
# ---------------------------------------------------------------------------
weight: 0
toc: false            # show an "In this article" contents box

# ---------------------------------------------------------------------------
#  Optional match details
#
#  These are NOT printed on the page. They are given to Google and the other
#  search engines as structured data, so a match report can be shown as a
#  result about that fixture. To print a scoreline in the story itself, use
#  the shortcode instead, wherever you want it to appear:
#
#    {{</* scoreline home="Arsenal" homeScore="3" away="Liverpool"
#                   awayScore="1" caption="Premier League · Emirates" */>}}
# ---------------------------------------------------------------------------
# match:
#   competition: "Premier Division · Matchday 24"
#   venue: "Riverside Stadium"
#   status: "Full time"
#   home: { name: "Team A", score: "3" }
#   away: { name: "Team B", score: "1" }
---

Write the story here in plain Markdown.

## A sub-heading

A paragraph. **Bold**, *italic* and [links](https://example.com) all work.

![Describe the picture](/images/another-photo.jpg "Caption printed under the picture")

> A quote from a player or manager.

- A bullet point
- Another bullet point
