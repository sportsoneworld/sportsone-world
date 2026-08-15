# 6 · The design system

For whoever changes how the site looks. Everything below is defined once, in
`assets/css/01-tokens.css`, and used everywhere else by name. Change a token and
the whole site follows.

The governing principle, in order of priority:

**Editorial hierarchy › visual consistency › readability › performance ›
decorative effects.**

---

## Colour

The site ships in two skins and follows the reader's operating system. **Only
the token values change between them** — no component knows which skin it is in,
which is why there is one set of components rather than two.

| Token | Light | Dark | Used for |
|-------|-------|------|----------|
| `--c-red` | `#d8232a` | `#ef4146` | The sport in an eyebrow, accents, active states |
| `--c-red-strong` | `#d8232a` | `#d8232a` | Solid red panels: the LIVE button, chips. Fixed, because white sits on it in both skins |
| `--c-ink` | `#0d1117` | `#f2f5f9` | Headlines and body text |
| `--c-ink-strong` | `#0b1b3a` | `#ffffff` | Section titles, page titles, prose sub-headings |
| `--c-ink-2` | `#3d4654` | `#aab3c0` | Standfirsts and deks |
| `--c-muted` | `#6b7484` | `#8b94a3` | Dates, captions |
| `--c-line` | `#e2e5ea` | `#232b36` | Hairline rules |
| `--c-bg` | `#ffffff` | `#0b0e13` | The page |
| `--c-surface-2` | `#f5f6f8` | `#121821` | Footer, live-scores strip, code, table headers |
| `--c-surface-3` | `#e9ecf1` | `#1a212b` | Image placeholder, before a picture loads |

**Two traps to avoid when editing this.**

1. `--c-ink-strong` is a *text* colour that flips to white in dark. `--c-navy` is
   a *surface* that stays dark in both. They are not interchangeable — using
   `--c-navy` for a heading gives you an invisible heading in dark mode.
2. Anything with white text on it must use `--c-red-strong`, not `--c-red`. The
   lighter dark-mode red does not carry white text at AA.

**Contrast.** Every text/background pair on the site meets WCAG AA in both
skins. If you change a colour, re-check before shipping — see "Making a change
safely" at the end of this file.

**Deliberately absent:** decorative gradients, coloured shadows, and any colour
outside this list. The only gradient on the site is the legibility scrim over
carousel photographs, and that exists to make white text readable, not for
decoration. It is deliberately near-opaque through the whole text band so that a
bright photograph — a white sky behind a headline — still holds AA.

---

## Typography

Two faces doing three jobs. Never mixed up.

| Role | Family | Where |
|------|--------|-------|
| **Display** | Cambo (serif, 400) | Every headline, section title, page title, pull quote |
| **Interface** | Inter 400–900 | Navigation, eyebrows, buttons, dates, labels, captions |
| **Body** | Inter 400 | Standfirsts, deks, article body |
| **Wordmark** | Inter 800, `0.18em` tracking, uppercase | "SPORTSONE" in the masthead and footer |
| **Numerals** | Inter with `tabular-nums` | Scores, clocks, percentages, statistics |

**The rule that matters:** an editorial serif for anything that is a headline, a
neutral sans for anything you have to read for more than ten seconds or click.
Never set body text in the display face, and never set a headline in the sans.

**Cambo ships one weight.** Do not ask it for bold — the browser will synthesise
one and it looks poor at headline sizes. Presence comes from size, not weight.
That is why every heading rule in the project sets `font-weight: 400`.

### The scale

Every size is a token. Nothing on the site sets its own font-size at a
breakpoint; sizes scale fluidly with `clamp()` between a mobile and a desktop
value.

| Token | Mobile → Desktop | Used for |
|-------|------------------|----------|
| `--t-display-xl` | 38 → 68 px | Reserved for the largest editorial moments |
| `--t-display-l` | 31 → 50 px | Article headline |
| `--t-h1` | 27 → 42 px | Page titles, lead cards |
| `--t-h2` | 23 → 32 px | Article sub-headings |
| `--t-section` | 24 → 36 px | The serif capitals that head every block |
| `--t-h3` | 17 → 21 px | Card titles, panel titles |
| `--t-body-lg` | 17 → 19 px | Article body, standfirsts |
| `--t-body` | 16 px | Default |
| `--t-body-sm` | 15 px | Card excerpts, UI text |
| `--t-meta` | 13 px | The article byline, dates |
| `--t-caption` | 12 px | Image captions, small print |
| `--t-label` | 11 px | Eyebrows and chips, uppercase, wide tracking |
| — | 10 px | The image credit line. The only type on the site set below 12px, and the only place that size is allowed |
| `--t-score` | 20 → 28 px | Scores |
| `--t-nav` | 14 px | Navigation |

### Tabular numerals

Anywhere a number changes — a score, a clock, a percentage — the site uses
`font-variant-numeric: tabular-nums` via the `.t-num`, `.t-score` and
`.match__score` classes. Every digit occupies the same width, so `9 – 8`
becoming `10 – 8` shifts nothing on the page.

```text
89:42      2 - 1      125      98.4%
```

---

## Spacing

An eleven-step scale, `--sp-1` (4px) through `--sp-11` (80px). Nothing in the
project uses an arbitrary pixel value for spacing.

`--section-gap` controls the rhythm between major homepage blocks and grows with
the viewport: 40px on phones, 48px on tablets, 64px on large screens.

---

## Breakpoints

Five, mobile-first. Tokens change at these widths; individual components do not.

| Name | Width | What changes |
|------|-------|--------------|
| Small phone | <360px | Gutter 14px. The wordmark, LIVE button and menu button each give a little so the toolbar fits 320px. |
| Mobile | base | One column. Gutter 18px. Carousels 4:5. |
| Large phone | 600px | Two-column card grids. Carousels 3:2. |
| Tablet | 768px | Gutter 28px. Carousels 16:9. |
| Laptop | 1024px | The toolbar and its dropdowns replace the hamburger menu. Gutter 32px. Spotlight 21:9; the Top Stories panel becomes square with four story rows beside it; sport carousels 21:9. Article rail appears. |
| Desktop | 1280px | Rail 340px. Spotlight 12:5. |
| Large | 1600px | Gutter 40px. Rail 360px. Spotlight 5:2. |

Container widths: `--container-max` 1280px for editorial content,
`--container-wide` 1440px for the masthead and the front page,
`--container-read` 44rem (≈704px) for the article reading measure.

---

## Images and the fixed-frame rule

**No image on this site controls its own dimensions.** Every picture sits inside
a `.frame` element that owns the size via `aspect-ratio`, with the image itself
absolutely positioned at `object-fit: cover`.

```html
<div class="frame frame--wide">
  <img src="/images/anything.jpg" alt="…">
</div>
```

| Class | Ratio | Used for |
|-------|-------|----------|
| `.frame` | 16:9 | Default card |
| `.frame--wide` | 16:9 | Cards, article hero, in-body figures |
| `.frame--thumb` | 1:1 | Small lists |
| `.frame--portrait` | 4:5 | Portrait treatments |
| `.frame--banner` | 21:9 | Wide banners |

The consequence: a 4000 × 3000 photograph and an 800 × 800 one produce byte-for-byte
identical layout. There is no layout shift while images load, because the box
already has its size before the picture arrives.

The carousels are the strongest case. A `.cslide` carries
`aspect-ratio: var(--ratio-hero)` (or `--ratio-top` / `--ratio-sport`), so the
frame is decided entirely by the breakpoint — never by the photograph inside it.
Swap a picture, or let an editor swap the whole story, and not one pixel of the
page moves.

---

## Surfaces

Radii are 2–4px. Shadows are used twice on the whole site. Cards are separated
by rules and whitespace, not by boxes.

The recurring devices are:

* **Section head** — large serif capitals with a hairline running out to the
  right edge of the column (`.section-head` / `.section-title`)
* **Credit line** — where a category label would sit on a card, and directly
  under a photograph everywhere else. Categories are deliberately not printed
  above headlines: the navigation already says where the reader is, and the
  space is worth more to the photographer (`.credit`)
* **Panel** — a 2px top edge in `--c-ink-strong` (`.panel`)
* **Credit line** — 10px, muted, immediately beneath a photograph and above any
  caption. It still clears AA contrast in both skins, and its links still carry
  a 24px tap target, because "small" is a visual decision and not an excuse
* **Chip** — a solid red label in 11px uppercase (`.chip`, `.livetag`)
* **LIVE button** — the only solid red control in the toolbar (`.livebtn`)

---

## Components

| Class | What it is |
|-------|-----------|
| `.card` | Photograph above, eyebrow, headline, dek. No byline, ever |
| `.card--lead` | Same, larger headline — the first story on a listing page |
| `.card--feed` | Same, medium headline — Top Stories, sport blocks, news feeds |
| `.card--compact` | Same, smaller headline, no dek — dense grids |
| `.carousel` | Spotlight, Top Stories and every sport carousel. One implementation |
| `.cslide` | One slide: fixed-ratio photograph, scrim, eyebrow, headline, dek |
| `.headline-list` | Text-only headlines with a hairline between each |
| `.headline-list--ranked` | The same, numbered in red figures |
| `.scorestrip` | The horizontal Live Scores band on the front page |
| `.mcard` | One match, used by both the strip and the `/scores/` board |
| `.panel` | Sidebar box |
| `.tile` | Category tile on `/categories/` |
| `.credit` | The photographer and licence, 10px. Directly under a picture on an article; in place of a category label on a card; under the channel name on a video |
| `.board` | The scoreboard at /scores/ — rows grouped by competition, no cards |
| `.videogrid` / `.vcard` | Three clips at the foot of a sport page |
| `.pagination` | Small numerals under a feed, from page eleven of stories onward |
| `.prose` | The article body — sets the reading measure and all long-form styles |

---

## Accessibility commitments

These are requirements, not preferences. Do not remove them to gain a visual
effect.

* Every interactive element has a visible focus ring — 3px, brand blue, offset
  2px. `:focus-visible` only, so pointer users do not see it.
* A skip link to the main content is the first thing in the tab order.
* Touch targets are at least 44 × 44px.
* Every carousel: `aria-roledescription="carousel"`, per-slide labels, a polite
  live region announcing "Story 3 of 5", arrow-key support on the dots, pause on
  hover, swipe and focus, and **no auto-rotation at all** when the operating
  system requests reduced motion.
* No slide is marked hidden or untabbable in the HTML. The script adds that only
  once it has taken control, so with JavaScript off every story in a carousel is
  still reachable by keyboard.
* The dots and arrows stay hidden until the script has loaded. A control that
  would do nothing is never shown.
* The sports dropdowns open on hover **and** on keyboard focus, in CSS alone.
  The disclosure button keeps `aria-expanded` honest, Escape closes the menu and
  returns focus to the button.
* The mobile menu traps focus, closes on Escape and restores focus to the button
  that opened it.
* A card's photograph link is `aria-hidden` with `tabindex="-1"`: the headline
  beneath it is the real link, so a keyboard user tabs each story once, not
  twice.
* One `<h1>` per page — on the front page it is visually hidden, because the
  page's real headline is the masthead. Headings never skip a level.
* `prefers-reduced-motion: reduce` disables every animation and transition.
* Colour is never the only signal — the LIVE badge carries a label as well as a
  dot, and the eyebrow names the sport in words.

---

## Performance commitments

* One CSS request and one JavaScript request per page, both minified and
  content-hashed.
* Fonts self-hosted and preloaded; **zero** third-party requests site-wide.
* Below-the-fold images are `loading="lazy"`; the article hero and the first
  Spotlight slide are `fetchpriority="high"`.
* Fixed-ratio frames mean a Cumulative Layout Shift contribution of zero from
  images.
* No JavaScript is required for any content to be readable.

---

## Making a change safely

1. Change the **token**, not the component. If you find yourself writing a
   pixel value inside a component file, the design system is missing a token —
   add one.
2. Preview at 320px, 768px, 1024px and 1440px, **in both light and dark**,
   before publishing. Chrome's device toolbar (`Cmd/Ctrl + Shift + M`) does the
   widths; its Rendering panel has an "Emulate prefers-color-scheme" switch.
3. Check nothing overflows sideways: with the page open, run
   `document.documentElement.scrollWidth` in the browser console. It must equal
   `document.documentElement.clientWidth`.
4. Re-check colour contrast if you touched a colour —
   <https://webaim.org/resources/contrastchecker/>.
