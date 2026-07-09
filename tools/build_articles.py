#!/usr/bin/env python3
"""
Build the article landing pages for the vISIon website.

Usage:  python3 tools/build_articles.py

Reads tools/articles.json and writes:
    articles/<slug>.html      one landing page per article
    articles/index.html       an index of every article, newest issue first

The generated files are committed to the repository. GitHub Pages serves them
directly: this script is a convenience for the editors, not a build step that
the site depends on. Re-run it after editing articles.json, then commit.
"""

import json
import pathlib
import html
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "articles.json"
OUT = ROOT / "articles"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,400;0,600;0,700;0,900;1,700'
         '&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">')


def esc(text):
    return html.escape(str(text), quote=False)


def header(current, latest_pdf):
    """Site header. `current` marks the active nav item."""
    items = [
        ("../index.html", "Home", "home"),
        ("../issues.html", "Issues", "issues"),
        ("index.html", "Articles", "articles"),
        ("../board.html", "Editorial board", "board"),
        ("../submit.html", "Submit", "submit"),
        ("../about.html", "About", "about"),
    ]
    links = "\n      ".join(
        '<a href="{}"{}>{}</a>'.format(
            href, ' aria-current="page"' if key == current else "", label)
        for href, label, key in items)
    return f"""<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="../index.html">
      <img class="brand-logo" src="../assets/logo.png" alt="International Statistical Institute">
      <span class="brand-name">vISIon</span>
    </a>
    <button class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="site-nav">
      <span></span><span></span><span></span>
    </button>
    <nav class="site-nav" id="site-nav">
      {links}
      <a class="btn btn-orange btn-sm nav-cta" href="../issues/{latest_pdf}">Read the latest issue</a>
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
      </div>
      <div>
        <h4>The ISI</h4>
        <a href="https://isi-web.org">isi-web.org</a>
        <a href="https://isi-portal.odoo.com/become-a-member">Become a member</a>
        <a href="https://www.isi-next.org/conferences/isi-wsc2027/">World Statistics Congress 2027</a>
        <a href="mailto:manuele.leonelli@ie.edu">Contact the editor</a>
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
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return " and ".join(names)
    if len(names) > 4:
        return names[0] + " and " + str(len(names) - 1) + " others"
    return ", ".join(names[:-1]) + " and " + names[-1]


def article_page(art, issue, prev_art, next_art):
    pdf_page = art["start_page"] + issue["page_offset"]
    pdf_link = "../issues/{}#page={}".format(issue["pdf"], pdf_page)

    authors_html = "\n        ".join(
        '<div class="author"><p class="name">{}</p><p class="affil">{}</p></div>'.format(
            esc(a["name"]), esc(a["affil"]))
        for a in art["authors"])

    points_html = "\n        ".join(
        "<li>{}</li>".format(esc(p)) for p in art["points"])

    quote_html = ""
    if art.get("quote"):
        quote_html = ('<blockquote class="pull" style="color:var(--isi-blue); border-color:var(--isi-orange)">'
                      '&ldquo;{}&rdquo;</blockquote>'.format(esc(art["quote"])))

    pager = []
    if prev_art:
        pager.append('<a class="pager-link prev" href="{}.html"><span>Previous in this issue</span><strong>{}</strong></a>'
                     .format(prev_art["slug"], esc(prev_art["title"])))
    else:
        pager.append('<span></span>')
    if next_art:
        pager.append('<a class="pager-link next" href="{}.html"><span>Next in this issue</span><strong>{}</strong></a>'
                     .format(next_art["slug"], esc(next_art["title"])))
    else:
        pager.append('<span></span>')

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
<meta name="description" content="{html.escape(desc, quote=True)}">
<meta name="keywords" content="{html.escape(art['keywords'], quote=True)}">
<link rel="icon" href="../assets/favicon.png" type="image/png">
{FONTS}
<link rel="stylesheet" href="../css/style.css">
<meta property="og:title" content="{html.escape(art['title'], quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:type" content="article">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>

{header('articles', ISSUE_LATEST_PDF)}

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
          <a class="btn btn-orange" href="{pdf_link}">Open at page {art['start_page']}</a>
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


def index_page(issues, by_issue):
    blocks = []
    for issue in issues:
        arts = by_issue[issue["id"]]
        rows = "\n".join(
            f"""        <li class="index-row">
          <a href="{a['slug']}.html">
            <p class="index-section">{esc(a['section'])} &middot; pp. {esc(a['pages'])}</p>
            <h3>{esc(a['title'])}</h3>
            <p class="index-sub">{esc(a['subtitle'])}</p>
            <p class="index-authors">{esc(author_line(a['authors']))}</p>
          </a>
        </li>""" for a in arts)

        blocks.append(f"""    <section class="section{' section-tint' if issue is issues[1] else ''}">
      <div class="container">
        <p class="kicker">{esc(issue['date'])} &middot; {esc(issue['volume'])}</p>
        <h2 class="section-title">{esc(issue['theme'])}</h2>
        <p class="issue-card-theme" style="margin-top:1rem">{esc(issue['sdg'])}</p>
        <ul class="index-list">
{rows}
        </ul>
        <div class="btn-row">
          <a class="btn btn-blue btn-sm" href="../issues/{issue['pdf']}">Read the whole issue (PDF)</a>
        </div>
      </div>
    </section>""")

    body = "\n\n".join(blocks)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Articles &middot; vISIon: The ISI Magazine</title>
<meta name="description" content="Every article published in vISIon, the magazine of the International Statistical Institute, with summaries and direct links into each issue.">
<link rel="icon" href="../assets/favicon.png" type="image/png">
{FONTS}
<link rel="stylesheet" href="../css/style.css">
</head>
<body>

{header('articles', ISSUE_LATEST_PDF)}

<main>

  <section class="page-hero">
    <div class="container">
      <p class="kicker" style="color:#28CBFF">Index</p>
      <h1>Articles</h1>
      <p>Every piece vISIon has published, with a summary of each and a link straight to its opening page.</p>
    </div>
  </section>

{body}

</main>

{FOOTER}"""


def main():
    global ISSUE_LATEST_PDF

    data = json.loads(DATA.read_text(encoding="utf-8"))
    issues = data["issues"]
    ISSUE_LATEST_PDF = issues[0]["pdf"]

    by_id = {i["id"]: i for i in issues}
    by_issue = {i["id"]: [] for i in issues}
    for art in data["articles"]:
        by_issue[art["issue"]].append(art)

    OUT.mkdir(exist_ok=True)
    written = 0

    for issue_id, arts in by_issue.items():
        for n, art in enumerate(arts):
            prev_art = arts[n - 1] if n > 0 else None
            next_art = arts[n + 1] if n < len(arts) - 1 else None
            page = article_page(art, by_id[issue_id], prev_art, next_art)
            (OUT / f"{art['slug']}.html").write_text(page, encoding="utf-8")
            written += 1

    (OUT / "index.html").write_text(index_page(issues, by_issue), encoding="utf-8")
    written += 1

    print(f"Wrote {written} files to {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
