#!/usr/bin/env python3
"""
Build the article landing pages for the vISIon website.

Usage:  python3 tools/build_articles.py

Reads tools/articles.json and writes:
    articles/<slug>.html      one landing page per published article
    articles/index.html       searchable index of everything, newest first

Articles marked  "draft": true  are listed on the index (so the issue's
contents look complete) but get no landing page, and their entry links
straight into the PDF instead. Fill in authors, summary and points, remove
the draft flag, and re-run this script to publish the page.

The generated files are committed to the repository. GitHub Pages serves them
directly: this script is a convenience for the editors, not a build step the
site depends on.
"""

import json
import pathlib
import html
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "articles.json"
OUT = ROOT / "articles"

# Fonts are self-hosted and declared in css/style.css, so no third-party
# request is made and no visitor IP leaves the site.
FONTS = ('<link rel="preload" href="../assets/fonts/source-serif-4-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
         '<link rel="preload" href="../assets/fonts/source-sans-3-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>')

LATEST_PDF = ""


def esc(t):
    return html.escape(str(t), quote=False)


def attr(t):
    return html.escape(str(t), quote=True)


def header(current):
    items = [
        ("../index.html", "Home", "home"),
        ("../issues.html", "Issues", "issues"),
        ("index.html", "Articles", "articles"),
        ("../board.html", "Editorial board", "board"),
        ("../submit.html", "Submit", "submit"),
        ("../about.html", "About", "about"),
    ]
    links = "\n      ".join(
        '<a href="{}"{}>{}</a>'.format(h, ' aria-current="page"' if k == current else "", l)
        for h, l, k in items)
    return f"""<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="../index.html">
      <img class="brand-logo" src="../assets/isi-mark.png" alt="International Statistical Institute">
      <span class="brand-name">vISIon</span>
    </a>
    <button class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="site-nav">
      <span></span><span></span><span></span>
    </button>
    <nav class="site-nav" id="site-nav">
      {links}
      <a class="btn btn-orange btn-sm nav-cta" href="../issues/{LATEST_PDF}">Read the latest issue</a>
    </nav>
  </div>
</header>"""


FOOTER = """<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <p class="footer-wordmark">vISIon</p>
        <p class="footer-tag">Statistical Science for a Better World</p>
        <p class="footer-text">The magazine of the International Statistical Institute. Published twice a year, free to read.</p>
      </div>
      <div>
        <h4>Magazine</h4>
        <a href="../issues.html">Issues</a>
        <a href="index.html">Articles</a>
        <a href="../board.html">Editorial board</a>
        <a href="../submit.html">Submit an article</a>
        <a href="../about.html">About</a>
        <a href="../contact.html">Contact</a>
      </div>
      <div>
        <h4>The ISI</h4>
        <a href="https://isi-web.org">Website</a>
        <a href="https://isi-web.org/scientific-journals">Journals</a>
        <a href="https://isi-portal.odoo.com/become-a-member">Become a member</a>
      </div>
    </div>
    <div class="container footer-bottom">
      <p>&copy; <span data-year>2026</span> International Statistical Institute. All rights reserved. vISIon is not a peer-reviewed journal.</p>
    </div>
  </div>
</footer>

<script src="../js/main.js"></script>
</body>
</html>
"""


def author_line(authors):
    names = [a["name"] for a in authors]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return " and ".join(names)
    if len(names) > 4:
        return names[0] + " and " + str(len(names) - 1) + " others"
    return ", ".join(names[:-1]) + " and " + names[-1]


def pdf_link(art, issue, prefix="../"):
    return "{}issues/{}#page={}".format(prefix, issue["pdf"], art["start_page"] + issue["page_offset"])


def article_page(art, issue, prev_art, next_art):
    authors_html = "\n        ".join(
        '<div class="author"><p class="name">{}</p><p class="affil">{}</p></div>'.format(
            esc(a["name"]), esc(a["affil"])) for a in art["authors"])

    points_html = "\n        ".join("<li>{}</li>".format(esc(p)) for p in art["points"])

    quote_html = ""
    if art.get("quote"):
        quote_html = ('<blockquote class="pull" style="color:var(--isi-blue); border-color:var(--isi-orange)">'
                      '&ldquo;{}&rdquo;</blockquote>'.format(esc(art["quote"])))

    pager = []
    if prev_art:
        pager.append('<a class="pager-link prev" href="{}.html"><span>Previous in this issue</span>'
                     '<strong>{}</strong></a>'.format(prev_art["slug"], esc(prev_art["title"])))
    else:
        pager.append("<span></span>")
    if next_art:
        pager.append('<a class="pager-link next" href="{}.html"><span>Next in this issue</span>'
                     '<strong>{}</strong></a>'.format(next_art["slug"], esc(next_art["title"])))
    else:
        pager.append("<span></span>")

    citation = "{}. \u201c{}.\u201d vISIon: The ISI Magazine {}, {}, pp. {}.".format(
        author_line(art["authors"]), art["title"], issue["volume"], issue["date"], art["pages"])

    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": art["title"],
        "alternativeHeadline": art["subtitle"],
        "author": [{"@type": "Person", "name": a["name"], "affiliation": a["affil"]} for a in art["authors"]],
        "isPartOf": {"@type": "PublicationIssue", "issueNumber": issue["volume"],
                     "isPartOf": {"@type": "Periodical", "name": "vISIon: The ISI Magazine"}},
        "publisher": {"@type": "Organization", "name": "International Statistical Institute"},
        "abstract": art["summary"],
        "keywords": art["keywords"],
        "pagination": art["pages"],
    }

    desc = art["summary"][:300].rsplit(" ", 1)[0] + "\u2026"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(art['title'])} &middot; vISIon: The ISI Magazine</title>
<meta name="description" content="{attr(desc)}">
<meta name="keywords" content="{attr(art['keywords'])}">
<link rel="icon" href="../assets/favicon.png" type="image/png">
{FONTS}
<link rel="stylesheet" href="../css/style.css">
<meta property="og:title" content="{attr(art['title'])}">
<meta property="og:description" content="{attr(desc)}">
<meta property="og:type" content="article">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>

{header('articles')}

<main>

  <article>

    <header class="page-hero">
      <div class="container">
        <p class="kicker" style="color:#28CBFF">{esc(art['section'])} &middot; {esc(issue['date'])} &middot; {esc(issue['volume'])}</p>
        <h1>{esc(art['title'])}</h1>
        <p>{esc(art['subtitle'])}</p>
      </div>
    </header>

    <section class="section">
      <div class="container prose">

        <p class="kicker">{'Author' if len(art['authors']) == 1 else 'Authors'}</p>
        <div class="authors">
        {authors_html}
        </div>

        <h2>In brief</h2>
        <p class="lead-serif">{esc(art['summary'])}</p>

        {quote_html}

        <h2>What the article covers</h2>
        <ul class="highlights">
        {points_html}
        </ul>

        <div class="read-box">
          <div>
            <p class="kicker" style="margin-bottom:.3rem">Read the article</p>
            <p style="margin:0">Pages {esc(art['pages'])} of {esc(issue['volume'])}, {esc(issue['date'])}. Free to read, no registration.</p>
          </div>
          <a class="btn btn-orange" href="{pdf_link(art, issue)}">Open at page {art['start_page']}</a>
        </div>

        <h2>How to cite</h2>
        <p class="note">{esc(citation)}</p>

      </div>
    </section>

    <nav class="section section-tint" aria-label="More from this issue">
      <div class="container prose">
        <div class="pager">
          {pager[0]}
          {pager[1]}
        </div>
        <div class="btn-row">
          <a class="btn btn-outline-blue btn-sm" href="index.html">All articles</a>
          <a class="btn btn-outline-blue btn-sm" href="../issues.html">All issues</a>
        </div>
      </div>
    </nav>

  </article>

</main>

{FOOTER}"""


INDEX_JS = """
(function () {
  'use strict';
  var search  = document.getElementById('article-search');
  var rows    = Array.prototype.slice.call(document.querySelectorAll('.index-row'));
  var chips   = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var count   = document.getElementById('result-count');
  var empty   = document.getElementById('no-results');
  var showAll = document.getElementById('show-all');
  var INITIAL = 6;
  var expanded = false;

  var filters = { issue: 'all', section: 'all' };

  // Deep link from the issues page, e.g. articles/index.html?issue=vol1-no2
  var params = new URLSearchParams(window.location.search);
  if (params.get('issue')) { filters.issue = params.get('issue'); }
  if (params.get('q') && search) { search.value = params.get('q'); }

  function matches(row, needle) {
    if (filters.issue !== 'all' && row.dataset.issue !== filters.issue) return false;
    if (filters.section !== 'all' && row.dataset.section !== filters.section) return false;
    if (!needle) return true;
    return row.dataset.search.indexOf(needle) !== -1;
  }

  function apply() {
    var needle = (search ? search.value : '').trim().toLowerCase();
    var browsing = !needle && filters.issue === 'all' && filters.section === 'all' && !expanded;
    var shown = 0, total = 0;

    rows.forEach(function (row) {
      var hit = matches(row, needle);
      if (hit) total++;
      var visible = hit && (!browsing || total <= INITIAL);
      row.classList.toggle('is-hidden', !visible);
      if (visible) shown++;
    });

    if (count) {
      count.textContent = total === 0
        ? 'No articles match.'
        : (shown < total ? 'Showing ' + shown + ' of ' + total + ' articles'
                         : total + (total === 1 ? ' article' : ' articles'));
    }
    if (empty) empty.hidden = total !== 0;
    if (showAll) showAll.hidden = !(browsing && total > INITIAL);
  }

  if (search) search.addEventListener('input', function () { expanded = false; apply(); });

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var group = chip.dataset.group;
      chips.filter(function (c) { return c.dataset.group === group; })
           .forEach(function (c) { c.setAttribute('aria-pressed', String(c === chip)); });
      filters[group] = chip.dataset.value;
      expanded = false;
      apply();
    });
  });

  if (showAll) {
    showAll.addEventListener('click', function () { expanded = true; apply(); });
  }

  // Reflect a deep-linked issue on the chips
  chips.forEach(function (c) {
    if (c.dataset.group === 'issue') {
      c.setAttribute('aria-pressed', String(c.dataset.value === filters.issue));
    }
  });

  apply();
})();
"""


def index_page(issues, articles, by_id):
    sections = []
    for a in articles:
        if a["section"] not in sections:
            sections.append(a["section"])

    issue_chips = '<button class="chip" data-group="issue" data-value="all" aria-pressed="true">All issues</button>\n            '
    issue_chips += "\n            ".join(
        '<button class="chip" data-group="issue" data-value="{}" aria-pressed="false">{}</button>'.format(
            i["id"], esc(i["date"])) for i in issues)

    section_chips = '<button class="chip" data-group="section" data-value="all" aria-pressed="true">All sections</button>\n            '
    section_chips += "\n            ".join(
        '<button class="chip" data-group="section" data-value="{}" aria-pressed="false">{}</button>'.format(
            attr(s), esc(s)) for s in sections)

    rows = []
    for a in articles:
        issue = by_id[a["issue"]]
        haystack = " ".join([a["title"], a["subtitle"], a["section"], a["keywords"],
                             issue["date"], issue["volume"],
                             " ".join(x["name"] for x in a["authors"])]).lower()

        if a.get("draft"):
            inner = f"""            <p class="index-section">{esc(a['section'])} &middot; pp. {esc(a['pages'])}</p>
            <h3>{esc(a['title'])}</h3>
            <p class="index-sub">{esc(a['subtitle'])}</p>
            <p class="index-issue">{esc(issue['date'])} &middot; {esc(issue['volume'])}</p>
            <p class="draft-note">Opens the PDF. Summary page coming soon.</p>"""
            href = pdf_link(a, issue)
        else:
            inner = f"""            <p class="index-section">{esc(a['section'])} &middot; pp. {esc(a['pages'])}</p>
            <h3>{esc(a['title'])}</h3>
            <p class="index-sub">{esc(a['subtitle'])}</p>
            <p class="index-authors">{esc(author_line(a['authors']))}</p>
            <p class="index-issue">{esc(issue['date'])} &middot; {esc(issue['volume'])}</p>"""
            href = a["slug"] + ".html"

        rows.append(f"""        <li class="index-row" data-issue="{attr(a['issue'])}" data-section="{attr(a['section'])}" data-search="{attr(haystack)}">
          <a href="{href}">
{inner}
          </a>
        </li>""")

    rows_html = "\n".join(rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Articles &middot; vISIon: The ISI Magazine</title>
<meta name="description" content="Search every article published in vISIon, the magazine of the International Statistical Institute.">
<link rel="icon" href="../assets/favicon.png" type="image/png">
{FONTS}
<link rel="stylesheet" href="../css/style.css">
</head>
<body>

{header('articles')}

<main>

  <section class="page-hero">
    <div class="container">
      <p class="kicker" style="color:#28CBFF">Index</p>
      <h1>Articles</h1>
      <p>Search by title, author, section or subject. Every article links to its summary, and from there into the issue.</p>
    </div>
  </section>

  <section class="section">
    <div class="container">

      <div class="filters">
        <div class="search-field">
          <label for="article-search">Search</label>
          <input type="search" id="article-search" placeholder="wildfires, Auerbach, R package, literacy&hellip;" autocomplete="off">
        </div>
        <div>
          <span class="chip-group-label" id="issue-label">Issue</span>
          <div class="chip-group" role="group" aria-labelledby="issue-label">
            {issue_chips}
          </div>
        </div>
        <div>
          <span class="chip-group-label" id="section-label">Section</span>
          <div class="chip-group" role="group" aria-labelledby="section-label">
            {section_chips}
          </div>
        </div>
      </div>

      <p class="result-count" id="result-count" aria-live="polite">Latest articles</p>

      <ul class="index-list">
{rows_html}
      </ul>

      <p class="no-results" id="no-results" hidden>Nothing matches that search. Try an author's surname, or clear the filters.</p>

      <div class="btn-row show-all">
        <button class="btn btn-outline-blue" id="show-all" type="button" hidden>Show all articles</button>
      </div>

    </div>
  </section>

</main>

{FOOTER.replace('<script src="../js/main.js"></script>', '<script src="../js/main.js"></script>\n<script>' + INDEX_JS + '</script>')}"""


def main():
    global LATEST_PDF

    data = json.loads(DATA.read_text(encoding="utf-8"))
    issues = data["issues"]
    LATEST_PDF = issues[0]["pdf"]
    by_id = {i["id"]: i for i in issues}

    order = {i["id"]: n for n, i in enumerate(issues)}
    articles = sorted(data["articles"], key=lambda a: (order[a["issue"]], a["start_page"]))

    OUT.mkdir(exist_ok=True)
    built, skipped = 0, []

    for issue in issues:
        live = [a for a in articles if a["issue"] == issue["id"] and not a.get("draft")]
        for n, art in enumerate(live):
            for field in ("summary", "points", "authors"):
                if not art.get(field):
                    print(f"  ! {art['slug']}: '{field}' is empty. Fill it in, or set \"draft\": true.")
                    return 1
            page = article_page(art, issue, live[n - 1] if n else None,
                                live[n + 1] if n < len(live) - 1 else None)
            (OUT / f"{art['slug']}.html").write_text(page, encoding="utf-8")
            built += 1

    skipped = [a["slug"] for a in articles if a.get("draft")]

    (OUT / "index.html").write_text(index_page(issues, articles, by_id), encoding="utf-8")

    print(f"Built {built} article pages, plus the index.")
    if skipped:
        print("Drafts, listed on the index but with no page yet:")
        for s in skipped:
            print(f"  - {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
