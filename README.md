# vISIon: The ISI Magazine, website

The public website for *vISIon: The ISI Magazine*, published by the International Statistical Institute.

It is a plain static site: HTML, one stylesheet, one small script. No build step, no framework, no dependencies. Anyone on the editorial board who can edit a text file can update it, and GitHub Pages serves it for free.

---

## Contents

```
.
├── index.html              Homepage: cover-style hero, current issue, sections
├── issues.html             Archive of every published issue
├── board.html              Editorial board
├── submit.html             How to pitch an article
├── about.html              Mission, origin story, policies
├── 404.html                Not-found page (uses absolute paths, see below)
├── articles/
│   ├── index.html          Every article, newest issue first
│   └── <slug>.html         One landing page per article, 14 so far
├── css/style.css           The whole design system
├── js/main.js              Mobile menu and copyright year
├── assets/                 Logo, cover background, wave and dots motifs, favicon
│   └── covers/             Cover thumbnails, one per issue
├── issues/                 The issue PDFs
├── tools/
│   ├── articles.json       Metadata for every article
│   └── build_articles.py   Regenerates articles/ from articles.json
└── .nojekyll               Tells GitHub Pages to serve the files as they are
```

---

## Setting up the GitHub organisation and Pages

**1. Create the organisation.** On GitHub, *Your organizations* → *New organization* → Free plan. Something like `isi-vision` or `vISIon-ISI`.

**2. Create the repository**, named `vISIon`, and make it **public**. The site will then live at:

```
https://<organisation>.github.io/vISIon/
```

**3. Upload these files.** Drag the unzipped folder into the repository's web uploader, or:

```bash
git clone https://github.com/<organisation>/vISIon.git
cd vISIon
# copy the contents of this folder in, then
git add .
git commit -m "Launch the vISIon website"
git push
```

**4. Turn on Pages.** Repository → *Settings* → *Pages* → Source: *Deploy from a branch*, branch `main`, folder `/ (root)`. Save. The site is live in a minute or two.

**5. Invite the board.** Organisation → *People* → *Invite member*. Give board members the **Write** role on the repository so they can edit pages and open pull requests. Keep **Admin** for yourself and one other person.

**6. A custom domain.** Worth doing, and it removes the sub-path entirely. Add a file named `CNAME` at the repository root containing one line, for example `vision.isi-web.org`, ask whoever manages the `isi-web.org` DNS to add a CNAME record pointing that name at `<organisation>.github.io`, then tick *Enforce HTTPS* in the Pages settings. Afterwards, open `404.html` and replace every `/vISIon/` with `/`.

### One caveat about the name

GitHub Pages URLs are case-sensitive in the path. A repository named `vISIon` is served at `/vISIon/`, and a visitor who types `/vision/` in lower case will get a 404. Every link inside the site is relative, so this only affects people typing the URL by hand or copying it from a talk slide. Two ways out, either now or later:

- Register the custom domain in step 6. This is the clean answer, and `vision.isi-web.org` reads better on a slide than any `github.io` address.
- Or name the repository `<organisation>.github.io` instead, which serves the site from the domain root with no path at all.

Both are reversible. Nothing in these files hard-codes the path except the three links in `404.html`, which carry a comment saying so.

---

## Publishing a new issue

**1. Add the PDF** to `issues/`, on the same naming pattern:

```
issues/vISIon-Vol2-No1-Oct-2026.pdf
```

**2. Add the cover thumbnail.** Export page 1 as a JPEG about 1000 px wide, into `assets/covers/vol2-no1.jpg`. With `poppler-utils` installed:

```bash
pdftoppm -jpeg -r 120 -f 1 -l 1 -singlefile \
  issues/vISIon-Vol2-No1-Oct-2026.pdf assets/covers/vol2-no1
```

**3. Add the articles** to `tools/articles.json`: a new entry in `issues`, at the top of the list, and one entry per article in `articles`. Then regenerate the landing pages:

```bash
python3 tools/build_articles.py
```

That rewrites `articles/` and prints how many files it wrote. Commit the results.

**4. Update `index.html` and `issues.html`.** The homepage carries the current issue by hand: the hero badge month and year, the `hero-strip` teasers, the cover path, the heading, the tagline, the highlights and the PDF link. In `issues.html`, copy an existing `<article class="issue-card">` block and paste it above the others. Search both files for the previous issue's PDF filename and replace every occurrence, since the nav bar and footer link to it too.

### The `articles.json` fields

| Field | What it does |
|---|---|
| `slug` | The filename and URL of the landing page. Lower case, hyphens, no accents. |
| `issue` | Must match an `id` in the `issues` list. |
| `section` | Featured article, Teaching, Official statistics, Software, Interview, Country spotlight. |
| `pages` | The printed page range, shown to the reader, e.g. `2–7`. |
| `start_page` | The printed number of the article's first page. Used for the deep link. |
| `page_offset` | Set once per issue. PDF page = printed page + offset. Currently 2, because the cover and inside cover come before printed page 1. |
| `summary` | The standfirst. Two to four sentences of plain prose. |
| `points` | Three to five bullets on what the article covers. |
| `quote` | One pull-quote. Optional. |
| `keywords` | Comma-separated, used for search engines. |

The summaries currently on the site were written for the web rather than copied from the print abstracts, because an abstract written for a PDF reads oddly as a page introduction. If you would rather run the published abstracts verbatim, paste them into `summary` and regenerate.

Each landing page deep-links into the PDF at the article's opening page, using `#page=N`. This works in Chrome, Edge, Firefox and Safari's built-in viewers.

---

## Editing conventions

- **Colours** are defined once, as custom properties at the top of `css/style.css`. Change them there, never in the page files. They match the print edition: `--isi-blue #0000AF`, `--isi-azure #28CBFF`, `--isi-orange #E65738`, `--isi-flame #FF6E1E`, `--isi-turq #7FEBD7`.
- **Type** is Source Sans 3 for display and Source Serif 4 for body text, loaded from Google Fonts. These are the closest web equivalents to the Source Sans Pro and Libertinus Serif used in the LaTeX edition.
- **British spelling** throughout, to match the magazine.
- Keep PDFs under about 5 MB. The two current issues were compressed before being committed. GitHub blocks files above 100 MB and warns above 50 MB.

---

## Checking a change before it goes live

Serve the folder locally, which also lets you test `404.html` and the article pages:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

For a safer workflow with the board, ask members to open a pull request rather than committing to `main`. You review, then merge, and Pages redeploys automatically.

---

## Licence and credit

Issue PDFs and their contents are © the International Statistical Institute and the respective authors. The site design uses the ISI brand palette and marks with the ISI's permission.
