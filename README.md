# Sierra Tree and Fungi

Static website for **Sierra Tree and Fungi**, the independent consulting arborist practice of
Christopher Hodge, ISA Board Certified Master Arborist (WE-14385B), TRAQ qualified, Placerville,
California.

## Stack

Vanilla HTML, CSS and JavaScript. No build dependencies, no frameworks, no external APIs.
Deploy by serving the repository root as a static site.

```
index.html                     Home page
404.html                       Not found page
<page-slug>/index.html         One directory per content page (25 content pages)
assets/css/site.css            Design system and all page styles
assets/js/site.js              Navigation, table of contents, reveal, form handling
images/source/                 Photography kept from the previous site
favicon.svg                    Site icon
sitemap.xml, robots.txt        Crawling
build.py                       Generator that produced the content pages
```

## Regenerating the content pages

`build.py` renders the page HTML from the scraped source content and the shared layout
(header, mega menu, article template, consultation form, footer). Run it from the repo root:

```bash
python3 build.py
```

It rewrites `index.html`, `404.html`, `sitemap.xml`, `robots.txt` and every `<slug>/index.html`.
Edit the templates in `build.py` (or the CSS/JS directly) rather than hand editing generated HTML.

## Forms

Every form posts to LeadrVision at
`https://vision.leadrai.com/api/forms/44d385b010bfd8e65586d9b94e017664`.

* Plain HTML POST works without JavaScript; the visitor returns with `?submitted=1` and sees the
  confirmation message.
* With JavaScript the same payload is sent with `fetch()` as JSON and confirmed inline.
* Hidden fields: `_form` (form name), `_page` (set to `window.location.href` on load and included
  in the JSON body) and the `_gotcha` honeypot.

## Local preview

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/>.
