# The Inbox

**Put your stories in this folder. That is the whole job.**

Each story is two files with the **same name**:

```
Article-1.md      the words
Article-1.jpg     the picture

Article-2.txt     the words
Article-2.png     the picture
```

The name itself does not matter — `Article-1`, `city-united`, `Monday match
report`, anything. What matters is that the text file and the picture are
called the same thing. That is how the website knows which picture belongs to
which story.

Text files can be `.md` or `.txt`. Pictures can be `.jpg`, `.jpeg`, `.png` or
`.webp`.

---

## What goes in the text file

Nothing complicated. This is a complete, working article:

```
Six wickets before lunch and a Test that lasted two days

England were bowled out twice inside two sessions on a pitch that never
settled.

The first innings lasted 27 overs. The second lasted 24.
```

First line is the headline. The next paragraph becomes the summary that shows
on the front page. Everything after that is the story.

To say more — which sport it belongs to, where it should appear, who took the
picture — put a few lines at the top, then **one blank line**, then the story:

```
Headline: Riverside hold on for a first win of the season
Sport: Football
Section: Premier League
Summary: Two goals in four minutes either side of the interval.
Photo caption: Ellis celebrates the opening goal.
Photo source: Getty Images
Front page: Top stories
Order: 1

Riverside had not won since the opening weekend...
```

Every one of those lines is optional. Use the ones you need and leave the rest
out.

| Line | What it does |
|------|--------------|
| `Headline:` | The title. Without it, the first line of the file is used |
| `Summary:` | The sentence under the headline on cards and in Google |
| `Sport:` | `Cricket`, `Football`, `Tennis` — anything else files under Other Sports |
| `Section:` | A second label, e.g. `Premier League`, `Analysis`, `Match Reports` |
| `Tags:` | Comma separated, e.g. `Ashes, England, Day two` |
| `Photo caption:` | The line printed under the picture |
| `Photo description:` | What is in the picture, for readers who cannot see it |
| `Photo source:` | The agency: `Getty Images`, `Reuters`, `AP` |
| `Author:` and `Role:` | The byline |
| `Front page:` | `Spotlight`, `Top stories`, `Beside top`, `Editor's picks`, or leave out |
| `Order:` | `1` puts it first in that slot, `2` second, and so on |
| `Slug:` | Choose the web address yourself instead of letting it be made from the headline |
| `Date:` | `2026-08-28`. Leave out for "now" |
| `Hold: yes` | Import it but keep it unpublished until you are ready |

---

## The picture

One landscape photograph per story, **2400 pixels across or more**.

You do not need to crop it to a particular shape. The website crops it
automatically — the same photograph is shown as a wide banner on the front
page, a 16:9 picture on the story and a tall portrait on a phone. Because of
that, **keep the important part of the picture near the middle**, and the crop
will never cut the wrong thing off.

The import files every picture at three sizes for you — one for the story
page, one for the front-page banners and one for the small cards — and serves
the right one to each. Send the biggest version you have; you never see or
name the other two.

---

## What happens next

Once your files are in this folder, they are turned into real articles — the
pictures resized and filed, the stories written into the site, and the front
page updated if you asked for it.

* **On Windows:** double-click `Import-Articles.bat` in the main folder.
* **On GitHub:** it happens on its own, within about a minute of you uploading
  the files. See `docs/Publishing-Guide.docx`.

Either way this folder is emptied afterwards, and anything that needed your
attention is reported back to you in plain English.

A picture with no matching story, or a story with no matching picture, is
never thrown away — it is left here and mentioned in the report.
