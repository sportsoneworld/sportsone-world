---
# ---------------------------------------------------------------------------
#  SportsOne article
#  Fill this in, write the story below the dashes, set draft to false, save,
#  then commit and push. The website rebuilds and publishes itself.
#  Full guide: docs/02-publishing-and-managing-articles.md
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
#  Put the file in static/images/ then write the path WITHOUT the word static.
#  static/images/my-photo.jpg  ->  image: "/images/my-photo.jpg"
# ---------------------------------------------------------------------------
image: ""
imageAlt: ""          # describe the picture for screen readers — always fill this in
imageCaption: ""      # optional caption printed under the picture
thumbnail: ""         # optional different picture for the small cards

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
#  Where the story appears on the homepage
#    hero          the big rotating banner at the very top (max 5 stories)
#    top-stories   the compact strip directly under the banner
#    spotlight     the large feature block
#    editors-picks the Editor's Picks row
#    latest        the main Latest News feed  <- the normal choice
# ---------------------------------------------------------------------------
placement: "latest"

featured: false       # eligible to fill the hero / picks automatically
breaking: false       # shows the red BREAKING strip at the top of every page
weight: 0             # 1, 2, 3 ... pins this story to the top of its block
toc: false            # show an "In this article" contents box

# ---------------------------------------------------------------------------
#  Optional match details — prints a scoreline under the headline
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
