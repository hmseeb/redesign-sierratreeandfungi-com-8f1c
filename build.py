#!/usr/bin/env python3
"""
Static site generator for sierratreeandfungi.com (redesign).

Reads the scraped source pages in .git/gsb-source-pages/*.md and renders them
into the new design as static HTML. Content text is reproduced verbatim;
only the layout, navigation and styling are new.

Usage:  python3 build.py
"""

import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, ".git", "gsb-source-pages")

PHONE = "(530) 391-6100"
TEL = "tel:+15303916100"
SMS = "sms:+15303916100"
EMAIL = "Christopher@SierraTreeandFungi.com"
GOOGLE_REVIEWS = "https://maps.app.goo.gl/3TdDXWFtDpuNy1Bm7"
FORM_ACTION = "https://vision.leadrai.com/api/forms/44d385b010bfd8e65586d9b94e017664"

# --------------------------------------------------------------------------
# Pages: source file -> (path, <title>)
# --------------------------------------------------------------------------
PAGES = [
    ("01.md", "services", "Consulting Arborist Services | Sierra Tree and Fungi"),
    ("02.md", "consulting-arborist-services", "Consulting Arborist, El Dorado County, CA | Sierra Tree and Fungi"),
    ("03.md", "arborist-reports", "Arborist Reports and When You Need One | Sierra Tree and Fungi"),
    ("04.md", "ceqa-arborist-reports-sacramento", "Arborist Reports for Development Projects | Sierra Tree and Fungi"),
    ("05.md", "tree-inventory", "Tree Inventory and Tree Survey Services | Sierra Tree and Fungi"),
    ("06.md", "oak-resource-management-plan-el-dorado-county", "Oak Technical Report, El Dorado County CA | Sierra Tree and Fungi"),
    ("07.md", "oak-tree-removal-permit-el-dorado-county", "El Dorado County Oak Tree Removal Permit | Sierra Tree and Fungi"),
    ("08.md", "protected-trees-in-california", "Protected Trees in California, Explained | Sierra Tree and Fungi"),
    ("09.md", "tree-risk-assessment", "Tree Risk Assessment, TRAQ Qualified | Sierra Tree and Fungi"),
    ("10.md", "tree-health-assessment", "Tree Health Assessment and Tree Doctor | Sierra Tree and Fungi"),
    ("11.md", "how-to-tell-if-a-tree-is-dead-or-dying", "How to Tell if a Tree Is Dead or Dying | Sierra Tree and Fungi"),
    ("12.md", "tree-fungus-treatment", "Fungus on Trees: Removal and Treatment | Sierra Tree and Fungi"),
    ("13.md", "fungal-pathology-reports", "Fungal Pathology and Lab Reports | Sierra Tree and Fungi"),
    ("14.md", "armillaria-root-rot", "Armillaria Root Rot in California | Sierra Tree and Fungi"),
    ("15.md", "oak-disease-sacramento", "Oak Tree Disease Identification | Sierra Tree and Fungi"),
    ("16.md", "oak-galls", "Oak Galls and Gall Wasps, Explained | Sierra Tree and Fungi"),
    ("17.md", "mediterranean-oak-borer", "The Mediterranean Oak Borer in California | Sierra Tree and Fungi"),
    ("18.md", "mistletoe-in-trees", "Mistletoe in Trees, and When to Remove It | Sierra Tree and Fungi"),
    ("19.md", "redwood-tree-care", "Redwood Tree Care and Summer Water | Sierra Tree and Fungi"),
    ("20.md", "tree-bark-and-sap-symptoms", "Tree Oozing Sap or Peeling Bark? | Sierra Tree and Fungi"),
    ("21.md", "plant-health-care", "Plant Health Care Services for Trees | Sierra Tree and Fungi"),
    ("22.md", "root-collar-excavation", "Girdling Roots and Root Collar Excavation | Sierra Tree and Fungi"),
    ("23.md", "defensible-space-el-dorado-county", "Defensible Space, El Dorado County | Sierra Tree and Fungi"),
    ("24.md", "tree-roots-damaging-foundation", "Tree Roots Damaging a Foundation? Before You Cut | Sierra Tree and Fungi"),
    ("25.md", "new-homeowner-tree-assessment", "New Homeowner Tree Assessment, El Dorado | Sierra Tree and Fungi"),
]

EXISTING = {"/" + slug for _, slug, _ in PAGES}

# Short nav labels for every real page
LABELS = {
    "/services": "All Services",
    "/consulting-arborist-services": "Consulting Arborist Services",
    "/arborist-reports": "Arborist Reports",
    "/ceqa-arborist-reports-sacramento": "CEQA Arborist Reports",
    "/tree-inventory": "Tree Inventory and Survey",
    "/oak-resource-management-plan-el-dorado-county": "Oak Technical Report",
    "/oak-tree-removal-permit-el-dorado-county": "Oak Tree Removal Permit",
    "/protected-trees-in-california": "Protected Trees in California",
    "/tree-risk-assessment": "Tree Risk Assessment",
    "/tree-health-assessment": "Tree Health Assessment",
    "/how-to-tell-if-a-tree-is-dead-or-dying": "Dead or Dying Tree",
    "/tree-fungus-treatment": "Treating Fungi on Trees",
    "/fungal-pathology-reports": "Fungal Pathology Reports",
    "/armillaria-root-rot": "Armillaria Root Rot",
    "/oak-disease-sacramento": "Oak Disease, Sacramento Area",
    "/oak-galls": "Oak Galls and Gall Wasps",
    "/mediterranean-oak-borer": "Mediterranean Oak Borer",
    "/mistletoe-in-trees": "Mistletoe in Trees",
    "/redwood-tree-care": "Redwood Tree Care",
    "/tree-bark-and-sap-symptoms": "Bark and Sap Symptoms",
    "/plant-health-care": "Plant Health Care",
    "/root-collar-excavation": "Root Collar Excavation",
    "/defensible-space-el-dorado-county": "Wildfire Defensible Space",
    "/tree-roots-damaging-foundation": "Tree Roots and Property Damage",
    "/new-homeowner-tree-assessment": "New Homeowner Tree Assessment",
}

NAV_GROUPS = [
    ("Consulting & assessments", [
        "/consulting-arborist-services",
        "/tree-risk-assessment",
        "/tree-health-assessment",
        "/how-to-tell-if-a-tree-is-dead-or-dying",
        "/new-homeowner-tree-assessment",
    ]),
    ("Reports & permitting", [
        "/arborist-reports",
        "/ceqa-arborist-reports-sacramento",
        "/oak-resource-management-plan-el-dorado-county",
        "/oak-tree-removal-permit-el-dorado-county",
        "/protected-trees-in-california",
        "/tree-inventory",
    ]),
    ("Fungi & diagnosis", [
        "/fungal-pathology-reports",
        "/tree-fungus-treatment",
        "/armillaria-root-rot",
        "/oak-disease-sacramento",
        "/oak-galls",
        "/mediterranean-oak-borer",
        "/mistletoe-in-trees",
        "/tree-bark-and-sap-symptoms",
    ]),
    ("Care & property", [
        "/plant-health-care",
        "/root-collar-excavation",
        "/redwood-tree-care",
        "/defensible-space-el-dorado-county",
        "/tree-roots-damaging-foundation",
    ]),
]

FOOTER_SERVICES = [
    "/services", "/arborist-reports", "/tree-risk-assessment", "/tree-health-assessment",
    "/how-to-tell-if-a-tree-is-dead-or-dying", "/oak-resource-management-plan-el-dorado-county",
    "/ceqa-arborist-reports-sacramento", "/tree-inventory", "/plant-health-care",
]
FOOTER_FUNGI = [
    "/fungal-pathology-reports", "/tree-fungus-treatment", "/armillaria-root-rot",
    "/oak-disease-sacramento", "/oak-galls", "/mediterranean-oak-borer",
    "/mistletoe-in-trees", "/tree-bark-and-sap-symptoms", "/redwood-tree-care",
]
FOOTER_MORE = [
    "/consulting-arborist-services", "/root-collar-excavation", "/defensible-space-el-dorado-county",
    "/tree-roots-damaging-foundation", "/new-homeowner-tree-assessment",
    "/oak-tree-removal-permit-el-dorado-county", "/protected-trees-in-california",
]

SERVICE_OPTIONS = [
    "Arborist report", "Tree risk assessment", "Tree health assessment",
    "Oak Technical Report or oak permit", "Fungal pathology or lab diagnosis",
    "Plant health care", "Tree inventory or development project",
    "Wildfire defensible space", "New homeowner tree assessment", "Something else",
]

# Map a page slug to the best matching select option, for prefill.
SERVICE_FOR_PAGE = {
    "arborist-reports": "Arborist report",
    "ceqa-arborist-reports-sacramento": "Tree inventory or development project",
    "tree-inventory": "Tree inventory or development project",
    "oak-resource-management-plan-el-dorado-county": "Oak Technical Report or oak permit",
    "oak-tree-removal-permit-el-dorado-county": "Oak Technical Report or oak permit",
    "protected-trees-in-california": "Oak Technical Report or oak permit",
    "tree-risk-assessment": "Tree risk assessment",
    "tree-health-assessment": "Tree health assessment",
    "how-to-tell-if-a-tree-is-dead-or-dying": "Tree health assessment",
    "tree-fungus-treatment": "Fungal pathology or lab diagnosis",
    "fungal-pathology-reports": "Fungal pathology or lab diagnosis",
    "armillaria-root-rot": "Fungal pathology or lab diagnosis",
    "oak-disease-sacramento": "Fungal pathology or lab diagnosis",
    "oak-galls": "Tree health assessment",
    "mediterranean-oak-borer": "Tree health assessment",
    "mistletoe-in-trees": "Tree health assessment",
    "redwood-tree-care": "Plant health care",
    "tree-bark-and-sap-symptoms": "Tree health assessment",
    "plant-health-care": "Plant health care",
    "root-collar-excavation": "Plant health care",
    "defensible-space-el-dorado-county": "Wildfire defensible space",
    "tree-roots-damaging-foundation": "Tree risk assessment",
    "new-homeowner-tree-assessment": "New homeowner tree assessment",
}

# --------------------------------------------------------------------------
# Images kept from the source site (local copies)
# --------------------------------------------------------------------------
PINE_SRCSET = ("/images/source/01-image.webp 640w, /images/source/02-image.webp 750w, "
               "/images/source/03-image.webp 828w, /images/source/04-image.webp 1080w, "
               "/images/source/05-image.webp 1200w")
PINE_FALLBACK = "/images/source/05-image.webp"
LAET_SRCSET = ("/images/source/24-image.webp 384w, /images/source/25-image.webp 640w, "
               "/images/source/26-image.webp 750w, /images/source/27-image.webp 828w, "
               "/images/source/28-image.webp 1080w, /images/source/29-image.jpg 1200w")
LAET_FALLBACK = "/images/source/29-image.jpg"
BADGE_SM_SRCSET = ("/images/source/10-image.webp 48w, /images/source/11-image.webp 64w, "
                   "/images/source/12-image.webp 96w, /images/source/13-image.webp 128w")
BADGE_LG_SRCSET = ("/images/source/12-image.webp 96w, /images/source/13-image.webp 128w, "
                   "/images/source/14-image.webp 256w")

# Body images in the scraped pages that we have a local copy of.
BODY_IMAGE_MAP = {
    "Laetiporus.jpg": (LAET_SRCSET, LAET_FALLBACK, "(min-width: 1000px) 640px, 100vw"),
}

# --------------------------------------------------------------------------
# SVG bits
# --------------------------------------------------------------------------
LOGO_SVG = """<svg class="brand-mark" viewBox="0 0 48 48" role="img" aria-label="Sierra Tree and Fungi mark" focusable="false">
<circle cx="24" cy="24" r="23" fill="#123524"/>
<path d="M24 7l7.5 11.5h-4.2L34 29H14l6.7-10.5h-4.2z" fill="#8db8a0"/>
<rect x="22.4" y="28" width="3.2" height="9" rx="1.2" fill="#8db8a0"/>
<path d="M12 36.5c0-3.6 2.9-6.5 6.5-6.5s6.5 2.9 6.5 6.5z" fill="#c8871f"/>
<rect x="17.2" y="36.2" width="2.6" height="5" rx="1.1" fill="#c8871f"/>
</svg>"""

ICONS = {
    "arrow": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true" focusable="false"><path d="M2 8h11M9 4l4 4-4 4"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
    "sms": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9.9 9.9 0 0 1-3.6-.7L3 21l1.8-4.9A8.2 8.2 0 0 1 3.6 11.5 8.4 8.4 0 0 1 12 3.1h.5A8.4 8.4 0 0 1 21 11.5z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2.5 6 9.5 7 9.5-7"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "check": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M2.5 8.5l3.5 3.5 7.5-8"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="m12 2.6 2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.5l-5.9 3.1 1.2-6.5L2.5 9.5l6.6-.9z"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><path d="M12 7v5.5l3.5 2"/></svg>',
}


def esc(text):
    return html.escape(text, quote=True)


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:64] or "section"


# --------------------------------------------------------------------------
# Link handling
# --------------------------------------------------------------------------
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


def resolve_href(href):
    """Return a usable href, or None when the target does not exist here."""
    href = href.strip()
    if href.startswith(("http://", "https://", "tel:", "sms:", "mailto:", "#")):
        if "sierratreeandfungi.com" in href:
            return None
        return href
    if href == "/":
        return "/"
    if href in ("/consultation", "/contact", "/consultation/", "/contact/"):
        return "#consult"
    clean = "/" + href.strip("/").split("?")[0].split("#")[0]
    if clean in EXISTING:
        return clean + "/"
    return None


def inline(text, keep_text_when_unlinked=True):
    """Escape a line of scraped text and convert its markdown links."""
    out = []
    pos = 0
    for m in LINK_RE.finditer(text):
        out.append(esc(text[pos:m.start()]))
        label, href = m.group(1), m.group(2)
        target = resolve_href(href)
        if target:
            ext = target.startswith("http")
            attrs = ' target="_blank" rel="noopener"' if ext else ""
            out.append('<a href="%s"%s>%s</a>' % (esc(target), attrs, esc(label)))
        elif keep_text_when_unlinked:
            out.append(esc(label))
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def only_links(line):
    """True when a line is nothing but a run of markdown links."""
    stripped = line.strip()
    if not stripped.startswith("["):
        return False
    return LINK_RE.sub("", stripped).strip() == ""


# --------------------------------------------------------------------------
# Source parsing
# --------------------------------------------------------------------------
IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
LI_RE = re.compile(r"^\s{2,}\*\s+(.*)$")
CRUMB_RE = re.compile(r"^\s{2,}\d+\.\s+(.*)$")


def read_source(filename):
    with open(os.path.join(SRC, filename), "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    # body starts after the scraped header block (ends with the Book Consultation line)
    start = 0
    for i, line in enumerate(lines[:20]):
        if line.startswith("[Book Consultation]"):
            start = i + 1
            break
    # body ends where the scraped footer begins (the logo line) or at the CTA block
    end = len(lines)
    for i in range(len(lines) - 1, start, -1):
        if "Sierra Tree and Fungi logo" in lines[i]:
            end = i
            break
    body = lines[start:end]
    for i, line in enumerate(body):
        if line.strip() == "## Ask a Tree or Mushroom Question":
            body = body[:i]
            break
    return body


def parse_page(body):
    """Split a scraped body into head metadata plus content blocks."""
    data = {"eyebrow": "", "h1": "", "crumbs": [], "blocks": []}
    i = 0
    while i < len(body) and not body[i].strip():
        i += 1
    if i < len(body) and not body[i].startswith("#"):
        data["eyebrow"] = body[i].strip()
        i += 1
    while i < len(body) and not body[i].startswith("# "):
        i += 1
    if i < len(body):
        data["h1"] = body[i][2:].strip()
        i += 1
    # breadcrumbs
    while i < len(body):
        line = body[i]
        if not line.strip():
            i += 1
            if data["crumbs"]:
                break
            continue
        m = CRUMB_RE.match(line)
        if not m:
            break
        data["crumbs"].append(m.group(1).strip().rstrip("/").strip())
        i += 1

    blocks = data["blocks"]
    while i < len(body):
        raw = body[i]
        line = raw.strip()
        if not line:
            i += 1
            continue

        m = IMG_RE.match(line)
        if m:
            blocks.append(("image", (m.group(1), m.group(2))))
            i += 1
            continue

        if line.startswith("### "):
            blocks.append(("h3", line[4:].strip()))
            i += 1
            continue
        if line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
            i += 1
            continue
        if line.startswith("> "):
            blocks.append(("quote", line[2:].strip()))
            i += 1
            continue

        if LI_RE.match(raw):
            items = []
            while i < len(body):
                lm = LI_RE.match(body[i])
                if lm:
                    items.append(lm.group(1).strip())
                    i += 1
                elif not body[i].strip():
                    # a blank line inside the list block: look ahead
                    j = i
                    while j < len(body) and not body[j].strip():
                        j += 1
                    if j < len(body) and LI_RE.match(body[j]):
                        i = j
                        continue
                    break
                else:
                    break
            blocks.append(("ul", items))
            continue

        if line == "Related":
            links = []
            j = i + 1
            while j < len(body) and not body[j].strip():
                j += 1
            if j < len(body) and only_links(body[j]):
                links = LINK_RE.findall(body[j].strip())
                i = j + 1
            else:
                i += 1
            if links:
                blocks.append(("related", links))
            continue

        if only_links(line):
            blocks.append(("linkrow", LINK_RE.findall(line)))
            i += 1
            continue

        blocks.append(("p", line))
        i += 1
    return data


# --------------------------------------------------------------------------
# Rendering content blocks
# --------------------------------------------------------------------------
def render_image(alt, url):
    key = None
    for name in BODY_IMAGE_MAP:
        if re.search(re.escape(name).replace(r"\ ", "%2520"), url, re.I) or name.lower() in url.lower():
            key = name
            break
        enc = name.replace(" ", "%2520")
        if enc.lower() in url.lower():
            key = name
            break
    if not key:
        return ""  # the original file is not available in this repo
    srcset, fallback, sizes = BODY_IMAGE_MAP[key]
    return (
        '<figure>\n'
        '  <img src="%s" srcset="%s" sizes="%s" alt="%s" decoding="async" width="1200" height="1600">\n'
        '  <figcaption>%s</figcaption>\n'
        '</figure>' % (esc(fallback), esc(srcset), esc(sizes), esc(alt), esc(alt))
    )


def render_list(items):
    out = ['<ul>']
    for item in items:
        m = re.match(r"^\[([^\]]*)\]\(([^)\s]+)\)(.*)$", item)
        if m and m.group(3).strip():
            label, href, note = m.group(1), m.group(2), m.group(3).strip()
            target = resolve_href(href)
            if target:
                ext = target.startswith("http")
                attrs = ' target="_blank" rel="noopener"' if ext else ""
                head = '<a href="%s"%s>%s</a>' % (esc(target), attrs, esc(label))
            else:
                head = "<strong>%s</strong>" % esc(label)
            out.append('  <li>%s<span class="li-note">%s</span></li>' % (head, inline(note)))
        else:
            out.append('  <li>%s</li>' % inline(item))
    out.append('</ul>')
    return "\n".join(out)


def render_chips(links):
    chips = []
    for label, href in links:
        target = resolve_href(href)
        if not target or target.startswith("http"):
            continue
        chips.append('    <li><a class="chip" href="%s">%s</a></li>' % (esc(target), esc(label)))
    if not chips:
        return ""
    return '<ul class="chip-row">\n%s\n  </ul>' % "\n".join(chips)


def render_linkrow(links):
    """A standalone run of links in the body: render as chips (internal only)."""
    chips = render_chips(links)
    if not chips:
        return ""
    return '<div class="related" style="margin-top:1.6rem;border:0;padding-top:0">%s</div>' % chips


def render_blocks(blocks):
    """Return (article_html, faq_items, related_links)."""
    html_out = []
    faq = []
    related = []
    i = 0
    first_para_done = False

    while i < len(blocks):
        kind, value = blocks[i]

        if kind == "h2" and value.strip().lower() == "frequently asked questions":
            i += 1
            while i < len(blocks):
                k2, v2 = blocks[i]
                if k2 == "h3":
                    answer = []
                    i += 1
                    while i < len(blocks) and blocks[i][0] in ("p", "ul", "quote"):
                        k3, v3 = blocks[i]
                        if k3 == "p":
                            answer.append("<p>%s</p>" % inline(v3))
                        elif k3 == "ul":
                            answer.append(render_list(v3))
                        else:
                            answer.append("<blockquote><p>%s</p></blockquote>" % inline(v3))
                        i += 1
                    faq.append((v2, "\n".join(answer)))
                elif k2 in ("p",) and not faq:
                    i += 1
                else:
                    break
            continue

        if kind == "related":
            trailing = all(b[0] in ("related",) for b in blocks[i + 1:])
            if trailing:
                related.extend(value)
            else:
                chips = render_chips(value)
                if chips:
                    html_out.append('<div class="inline-related"><p class="inline-related-label">Related</p>%s</div>' % chips)
            i += 1
            continue

        if kind == "h2":
            html_out.append('<h2 id="%s">%s</h2>' % (slugify(value), esc(value)))
        elif kind == "h3":
            html_out.append("<h3>%s</h3>" % esc(value))
        elif kind == "p":
            cls = ' class="lead"' if not first_para_done else ""
            html_out.append("<p%s>%s</p>" % (cls, inline(value)))
            first_para_done = True
        elif kind == "ul":
            is_sources = any(
                h[0] == "h2" and "source" in h[1].lower()
                for h in [b for b in blocks[max(0, i - 2):i] if b[0] == "h2"]
            )
            lst = render_list(value)
            if is_sources:
                lst = lst.replace("<ul>", '<ul class="source-list">', 1)
            html_out.append(lst)
        elif kind == "quote":
            html_out.append("<blockquote><p>%s</p></blockquote>" % inline(value))
        elif kind == "image":
            fig = render_image(value[0], value[1])
            if fig:
                html_out.append(fig)
        elif kind == "linkrow":
            row = render_linkrow(value)
            if row:
                html_out.append(row)
        i += 1

    return "\n".join(html_out), faq, related


def render_faq(faq):
    if not faq:
        return "", ""
    items = ['<h2 id="frequently-asked-questions">Frequently Asked Questions</h2>',
             '<div class="faq">']
    for question, answer in faq:
        items.append('  <details>\n    <summary>%s</summary>\n    <div class="faq-body">%s</div>\n  </details>'
                     % (esc(question), answer))
    items.append("</div>")

    # FAQPage structured data
    import json
    entities = [{
        "@type": "Question",
        "name": q,
        "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", " ", a).replace("&amp;", "&").strip()},
    } for q, a in faq]
    schema = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities},
                        ensure_ascii=False)
    return "\n".join(items), schema


# --------------------------------------------------------------------------
# Shared chrome
# --------------------------------------------------------------------------
def nav_links(paths):
    return "\n".join('      <li><a href="%s/">%s</a></li>' % (p, esc(LABELS[p])) for p in paths)


def header_html(active=""):
    cols = []
    for title, paths in NAV_GROUPS:
        cols.append('    <div>\n      <h4>%s</h4>\n      <ul>\n%s\n      </ul>\n    </div>'
                    % (esc(title), nav_links(paths)))
    mega = "\n".join(cols)

    mobile_groups = []
    for title, paths in NAV_GROUPS:
        mobile_groups.append('    <h4>%s</h4>\n    <ul>\n%s\n    </ul>' % (esc(title), nav_links(paths)))
    mobile = "\n".join(mobile_groups)

    return """<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap head-inner">
    <a class="brand" href="/" aria-label="Sierra Tree and Fungi, home">
      %(logo)s
      <span class="brand-text">
        <strong>Sierra Tree &amp; Fungi</strong>
        <span>Consulting Arborist</span>
      </span>
    </a>
    <nav class="nav" aria-label="Primary">
      <ul class="nav-list">
        <li class="has-sub">
          <button type="button" class="nav-link" aria-expanded="false" aria-controls="megaServices">
            Services <svg viewBox="0 0 12 8" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true" focusable="false"><path d="M1 1.5 6 6.5l5-5"/></svg>
          </button>
          <div class="mega" id="megaServices">
%(mega)s
            <div class="mega-foot">
              <p>Independent consulting practice: assessments, diagnosis and written reports. No removal crews, so the recommendation is about your trees.</p>
              <a class="btn btn--ghost btn--sm" href="/services/">All services %(arrow)s</a>
            </div>
          </div>
        </li>
        <li><a class="nav-link" href="/services/">Services A&ndash;Z</a></li>
        <li><a class="nav-link" href="/#areas">Service Areas</a></li>
        <li><a class="nav-link" href="/#reviews">Reviews</a></li>
        <li><a class="nav-link" href="/#consult">Contact</a></li>
      </ul>
      <span class="nav-cta">
        <a class="btn btn--ghost btn--sm" href="%(tel)s">%(phone)s</a>
        <a class="btn btn--primary btn--sm" href="/#consult">Book Consultation</a>
      </span>
    </nav>
    <button class="burger" type="button" aria-expanded="false" aria-controls="mobileNav" aria-label="Menu"><span></span></button>
  </div>
</header>
<div class="mobile-nav" id="mobileNav">
  <div class="btn-row">
    <a class="btn btn--primary btn--sm" href="/#consult">Book Consultation</a>
    <a class="btn btn--ghost btn--sm" href="%(tel)s">Call %(phone)s</a>
    <a class="btn btn--ghost btn--sm" href="%(sms)s">Text a photo</a>
  </div>
  <h4>Browse</h4>
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/services/">All Services</a></li>
    <li><a href="/#areas">Service Areas</a></li>
    <li><a href="/#reviews">Reviews</a></li>
    <li><a href="/#consult">Contact</a></li>
  </ul>
%(mobile)s
</div>""" % {
        "logo": LOGO_SVG, "mega": mega, "mobile": mobile, "arrow": ICONS["arrow"],
        "tel": TEL, "sms": SMS, "phone": PHONE,
    }


def consult_html(page_name, service_hint=None, heading="Ask a Tree or Mushroom Question",
                 intro=None):
    if intro is None:
        intro = ("A full site assessment with a written report starts at $500, and the site visit on its own "
                 "is $250 for up to one hour on site. Not sure which you need? Ask me a tree or mushroom "
                 "question free, fifteen minutes, no obligation.")
    options = []
    for opt in SERVICE_OPTIONS:
        selected = " selected" if service_hint == opt else ""
        options.append('            <option value="%s"%s>%s</option>' % (esc(opt), selected, esc(opt)))
    options_html = "\n".join(options)

    return """<section class="section consult" id="consult">
  <div class="wrap">
    <div class="consult-grid">
      <div class="reveal">
        <p class="eyebrow">Request a Consultation</p>
        <h2>%(heading)s</h2>
        <p>%(intro)s</p>
        <div class="btn-row">
          <a class="btn" href="%(tel)s">%(phone_icon)s Call %(phone)s</a>
          <a class="btn btn--ghost" href="%(sms)s">%(sms_icon)s Text a Photo of Your Tree</a>
        </div>
        <ul class="contact-list">
          <li>%(phone_icon)s<span><span class="k">Phone and text</span><a href="%(tel)s">%(phone)s</a></span></li>
          <li>%(mail_icon)s<span><span class="k">Email</span><a href="mailto:%(email)s">%(email)s</a></span></li>
          <li>%(pin_icon)s<span><span class="k">Based in</span><span class="v">Placerville, California</span></span></li>
          <li>%(clock_icon)s<span><span class="k">Service area</span><span class="v">El Dorado, Sacramento, Placer and Amador counties</span></span></li>
        </ul>
        <p style="margin-top:1.4rem"><a class="link-arrow" href="/review">Leave us a review %(arrow)s</a></p>
      </div>

      <div class="form-card reveal">
        <form method="POST" action="%(action)s" data-leadr novalidate>
          <div class="form-status" role="status" aria-live="polite"></div>
          <input type="hidden" name="_form" value="%(form_name)s">
          <input type="hidden" name="_page" value="">
          <input type="text" name="_gotcha" tabindex="-1" autocomplete="off" style="display:none">
          <div class="form-grid">
            <div class="field">
              <label for="f-name-%(uid)s">Your name</label>
              <input id="f-name-%(uid)s" type="text" name="name" autocomplete="name" required>
            </div>
            <div class="field">
              <label for="f-phone-%(uid)s">Phone</label>
              <input id="f-phone-%(uid)s" type="tel" name="phone" autocomplete="tel" required>
            </div>
            <div class="field field--full">
              <label for="f-email-%(uid)s">Email</label>
              <input id="f-email-%(uid)s" type="email" name="email" autocomplete="email" required>
            </div>
            <div class="field field--full">
              <label for="f-addr-%(uid)s">Property address or city</label>
              <input id="f-addr-%(uid)s" type="text" name="Property address" autocomplete="street-address">
            </div>
            <div class="field field--full">
              <label for="f-svc-%(uid)s">Service needed</label>
              <select id="f-svc-%(uid)s" name="Service needed">
                <option value="">Not sure yet</option>
%(options)s
              </select>
            </div>
            <div class="field field--full">
              <label for="f-msg-%(uid)s">What are you seeing on the tree?</label>
              <textarea id="f-msg-%(uid)s" name="message" placeholder="Species if you know it, what changed, how close it is to the house, and any deadline such as a permit or escrow date."></textarea>
            </div>
          </div>
          <div class="form-foot">
            <button class="btn btn--primary" type="submit">Send my request %(arrow)s</button>
            <small>Or text a photo of your tree to <a href="%(sms)s">%(phone)s</a>.</small>
          </div>
        </form>
      </div>
    </div>
  </div>
</section>""" % {
        "heading": esc(heading), "intro": intro, "tel": TEL, "sms": SMS, "phone": PHONE,
        "email": EMAIL, "action": FORM_ACTION, "form_name": esc(page_name),
        "options": options_html, "uid": slugify(page_name),
        "phone_icon": ICONS["phone"], "sms_icon": ICONS["sms"], "mail_icon": ICONS["mail"],
        "pin_icon": ICONS["pin"], "clock_icon": ICONS["clock"], "arrow": ICONS["arrow"],
    }


def footer_html():
    def col(title, paths):
        return '      <div>\n        <h2>%s</h2>\n        <ul>\n%s\n        </ul>\n      </div>' % (
            esc(title),
            "\n".join('          <li><a href="%s/">%s</a></li>' % (p, esc(LABELS[p])) for p in paths),
        )

    return """<footer class="site-foot">
  <div class="wrap">
    <div class="foot-top">
      <div class="foot-about">
        <a class="brand" href="/">
          %(logo)s
          <span class="brand-text"><strong>Sierra Tree &amp; Fungi</strong><span>Consulting Arborist</span></span>
        </a>
        <p>Consulting Arborist Serving El Dorado, Sacramento, Placer and Amador Counties, California</p>
        <ul class="foot-contact">
          <li>%(pin)s<span>Placerville, CA</span></li>
          <li>%(phone_icon)s<a href="%(tel)s">%(phone)s</a></li>
          <li>%(mail)s<a href="mailto:%(email)s">%(email)s</a></li>
        </ul>
        <a class="foot-review" href="/review">%(star)s Leave us a review</a>
      </div>
%(c1)s
%(c2)s
%(c3)s
    </div>
    <div class="foot-bottom">
      <p>Disclosure: I also own <a href="https://www.norcaltreeconnect.com" target="_blank" rel="noopener">www.norcaltreeconnect.com</a>, a regional tree service directory. It is a separate business and takes no part in my assessments or reports.</p>
      <p>&copy; 2026 Sierra Tree and Fungi &middot; ISA Board Certified Master Arborist WE-14385B &middot; <a href="/review">Leave us a review</a></p>
    </div>
  </div>
</footer>
<div class="callbar">
  <a class="c1" href="%(tel)s">%(phone_icon)s Call now</a>
  <a class="c2" href="%(sms)s">%(sms_icon)s Text a photo</a>
</div>""" % {
        "logo": LOGO_SVG, "pin": ICONS["pin"], "phone_icon": ICONS["phone"], "mail": ICONS["mail"],
        "sms_icon": ICONS["sms"], "star": ICONS["star"], "tel": TEL, "sms": SMS,
        "phone": PHONE, "email": EMAIL,
        "c1": col("Services", FOOTER_SERVICES),
        "c2": col("Fungi & tree health", FOOTER_FUNGI),
        "c3": col("More", FOOTER_MORE),
    }


def document(title, description, canonical, body, extra_schema="", body_attr=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(description)s">
<link rel="canonical" href="%(canonical)s">
<meta name="theme-color" content="#123524">
<meta name="author" content="Christopher Hodge, ISA Board Certified Master Arborist">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Sierra Tree and Fungi">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(description)s">
<meta property="og:url" content="%(canonical)s">
<meta property="og:image" content="/images/source/05-image.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/favicon.svg">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body%(body_attr)s>
%(body)s
<script src="/assets/js/site.js" defer></script>
%(schema)s
</body>
</html>
""" % {
        "title": esc(title), "description": esc(description), "canonical": esc(canonical),
        "body": body, "schema": extra_schema, "body_attr": body_attr,
    }


LOCAL_BUSINESS_SCHEMA = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "Sierra Tree and Fungi",
  "description": "Independent consulting arborist practice of Christopher Hodge, ISA Board Certified Master Arborist (WE-14385B) and TRAQ qualified tree risk assessor, providing arborist reports, tree risk assessments, fungal pathology reports, Oak Technical Reports and plant health care.",
  "url": "https://sierratreeandfungi.com/",
  "telephone": "+1-530-391-6100",
  "email": "Christopher@SierraTreeandFungi.com",
  "image": "https://sierratreeandfungi.com/images/source/05-image.webp",
  "address": {"@type": "PostalAddress", "addressLocality": "Placerville", "addressRegion": "CA", "addressCountry": "US"},
  "areaServed": [
    {"@type": "AdministrativeArea", "name": "El Dorado County, California"},
    {"@type": "AdministrativeArea", "name": "Sacramento County, California"},
    {"@type": "AdministrativeArea", "name": "Placer County, California"},
    {"@type": "AdministrativeArea", "name": "Amador County, California"}
  ],
  "founder": {"@type": "Person", "name": "Christopher Hodge", "jobTitle": "ISA Board Certified Master Arborist WE-14385B"},
  "priceRange": "$250 - $500+"
}
</script>"""


def breadcrumb_schema(label, path):
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://sierratreeandfungi.com/"},
            {"@type": "ListItem", "position": 2, "name": "Services", "item": "https://sierratreeandfungi.com/services/"},
            {"@type": "ListItem", "position": 3, "name": label, "item": "https://sierratreeandfungi.com%s/" % path},
        ],
    }
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(data, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------------
# Home page
# --------------------------------------------------------------------------
HOME_SERVICES = [
    ("Phase 01, Documentation", "Arborist Reports", "/arborist-reports",
     "Permit ready arborist reports written to ISA best management practices: what a county reviewer, an HOA, "
     "an insurer, or a buyer needs in order to rely on the finding."),
    ("Phase 02, Risk", "Tree Risk Assessments", "/tree-risk-assessment",
     "TRAQ qualified tree risk assessments with a documented rating, for a tree near people or structures where "
     "somebody needs a defensible answer rather than an impression."),
    ("Phase 03, Diagnosis", "Tree Health Assessments", "/tree-health-assessment",
     "Diagnosis of a declining tree from the roots up: what is wrong, why, and what to do about it, with a written "
     "finding and a plant health care plan you can act on."),
    ("Phase 04, Permits", "Oak Technical Reports", "/oak-resource-management-plan-el-dorado-county",
     "Need an Oak Technical Report for an El Dorado County building permit that affects native oaks? I prepare the "
     "permit ready report the county requires, and I know what its reviewers look for."),
    ("Phase 05, Laboratory", "Fungal Pathology Reports", "/fungal-pathology-reports",
     "Identification and assessment of wood decay fungi and pathogens affecting tree structure and health. Lab "
     "informed fungal pathology reports document the organism, the risk it poses, and management options."),
    ("Phase 06, Stewardship", "Plant Health Care", "/plant-health-care",
     "Ongoing care after the diagnosis: fixing the water, soil, and root collar problems behind most decline first, "
     "and treating only where a treatment fits what I found. No removal crews, and no work sold that the tree does "
     "not need."),
]

COUNTIES = [
    ("El Dorado County", "Placerville, El Dorado Hills, Cameron Park, Shingle Springs, Camino and Pollock Pines"),
    ("Sacramento County", "Folsom, Sacramento and the surrounding valley communities"),
    ("Placer County", "Roseville, Rocklin, Auburn and Granite Bay"),
    ("Amador County", "The oak woodland and foothill communities east of the valley"),
]

CITIES = ["Placerville", "El Dorado Hills", "Cameron Park", "Shingle Springs", "Folsom",
          "Roseville", "Rocklin", "Auburn", "Granite Bay"]

REVIEWS = [
    ("L Joyce", "Google review",
     ["Arborist Christopher Hodge responded to my initial text promptly. He requested photos of the pine tree we "
      "were concerned about, made a preliminary analysis, and came to our property the same day to do a visual "
      "check and take measurements. His insights were helpful and encouraging, and the report he sent us was very "
      "professional and clear. I'm glad I found his website and consulted him."]),
    ("John Brace", "Google review",
     ["Christopher was amazing! We are trying to save a valley oak tree in our neighbors yard and we needed an ISA "
      "certified arborist to write a report. Christopher is not just an ISA board certified arborist, but a Master "
      "ISA certified arborist at that. I think I read that there’s only about 2% of all ISA arborist that "
      "achieve this level. His knowledge really showed and even though he was not able to go onto the neighbors "
      "property to do a full tree assessment, he did everything he could from my side and spent quite a lot of "
      "time with me in my yard taking photos and going over the entire tree to evaluate its health and what needs "
      "to be done to save the tree. The report that he wrote was very detailed and thorough. Thank you Christopher!"]),
]


def build_home():
    svc_cards = []
    for phase, name, path, text in HOME_SERVICES:
        svc_cards.append("""      <a class="svc reveal" href="%(path)s/">
        <p class="phase">%(phase)s</p>
        <h3>%(name)s</h3>
        <p>%(text)s</p>
        <span class="more">Learn more about %(name)s %(arrow)s</span>
      </a>""" % {"path": path, "phase": esc(phase), "name": esc(name), "text": esc(text),
                 "arrow": ICONS["arrow"]})

    areas = "\n".join(
        '      <div class="area reveal"><b>%s</b><span>%s</span></div>' % (esc(n), esc(d))
        for n, d in COUNTIES)
    cities = "\n".join('        <li class="chip">%s arborist</li>' % esc(c) for c in CITIES)

    quotes = []
    for author, source, paras in REVIEWS:
        body = "\n".join("            <p>&ldquo;%s&rdquo;</p>" % esc(p) for p in paras)
        quotes.append("""      <figure class="quote reveal">
        <div class="stars" aria-label="Five star review">%(stars)s</div>
        <blockquote>
%(body)s
        </blockquote>
        <footer><b>%(author)s</b> &middot; %(source)s &middot; <a class="link-arrow" href="%(g)s" target="_blank" rel="noopener">Read reviews on Google %(arrow)s</a></footer>
      </figure>""" % {"stars": ICONS["star"] * 5, "body": body, "author": esc(author),
                      "source": esc(source), "g": GOOGLE_REVIEWS, "arrow": ICONS["arrow"]})

    body = """%(header)s
<main id="main">

  <section class="hero">
    <div class="hero-media">
      <img src="%(pine_src)s" srcset="%(pine)s" sizes="100vw"
           alt="Sugar pine in the Sierra Nevada forest above El Dorado County, California"
           width="1200" height="1600" decoding="async" fetchpriority="high">
    </div>
    <div class="wrap">
      <div class="hero-inner">
        <span class="cred-pill">
          <img src="/images/source/13-image.webp" srcset="%(badge_sm)s" sizes="34px"
               alt="ISA Board Certified Master Arborist badge" width="128" height="224" decoding="async">
          ISA Board Certified Master Arborist &middot; TRAQ Qualified
        </span>
        <h1>Consulting Arborist Serving El Dorado County, Sacramento County, Placer County and Northern California</h1>
        <p class="lede">Board Certified Master Arborist providing arborist reports, tree risk assessments, fungal
          pathology reports, Oak Technical Reports, and plant health care.</p>
        <p class="lede lede--sm">I have no removal crews and no financial incentive to recommend unnecessary work,
          just documented, conflict free advice from an ISA Board Certified Master Arborist with TRAQ qualification.</p>
        <div class="hero-ctas">
          <a class="btn btn--primary" href="#consult">Request a Consultation %(arrow)s</a>
          <a class="btn btn--light" href="/consulting-arborist-services/">Consulting Services</a>
          <a class="btn btn--light" href="%(sms)s">%(sms_icon)s Text a Photo of Your Tree</a>
        </div>
        <p class="hero-note">Or text a photo of your tree to <a href="%(sms)s">%(phone)s</a></p>
      </div>
      <dl class="hero-strip">
        <div><dt>Credential</dt><dd>ISA BCMA WE-14385B</dd></div>
        <div><dt>Risk work</dt><dd>TRAQ qualified assessor</dd></div>
        <div><dt>Specialty</dt><dd>Field &amp; lab mycology</dd></div>
        <div><dt>Based in</dt><dd>Placerville, California</dd></div>
      </dl>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="intro-grid">
        <div class="reveal">
          <p class="eyebrow">Sustainable stewardship through scientific observation</p>
          <p class="big">Sierra Tree and Fungi is the independent consulting practice of Christopher Hodge, an ISA
            Board Certified Master Arborist (WE-14385B), the highest credential the International Society of
            Arboriculture offers, and a TRAQ qualified tree risk assessor serving El Dorado, Sacramento, Placer, and
            Amador counties, California.</p>
          <p>A consulting arborist diagnoses and documents trees but does no removal work, so the advice is conflict
            free. I provide tree risk assessments, arborist reports, plant health care, and Oak Technical Reports, and
            I help property owners make informed decisions, preserve the trees they value, and steward their land.</p>
          <div class="stat"><b>15+</b><span>Years of field observation</span></div>
        </div>
        <aside class="intro-aside reveal">
          <img src="/images/source/14-image.webp" srcset="%(badge_lg)s" sizes="132px"
               alt="ISA Board Certified Master Arborist credential badge held by Christopher Hodge"
               width="256" height="448" decoding="async">
          <ul>
            <li>%(check)s<span>ISA Board Certified Master Arborist, WE-14385B</span></li>
            <li>%(check)s<span>ISA Tree Risk Assessment Qualified (TRAQ)</span></li>
            <li>%(check)s<span>Fifteen years of fungal taxonomy and forest ecology</span></li>
            <li>%(check)s<span>No removal crews, so no stake in the outcome</span></li>
            <li>%(check)s<span>Every engagement ends in a written finding</span></li>
          </ul>
          <div class="btn-row" style="margin-top:1.3rem">
            <a class="btn btn--sm" href="/consulting-arborist-services/">How consulting works</a>
          </div>
        </aside>
      </div>
    </div>
  </section>

  <section class="section section--paper2" id="services">
    <div class="wrap">
      <div class="sec-head sec-head--split">
        <div>
          <p class="eyebrow">Scientific Services</p>
          <h2>Master Level Tree Care</h2>
        </div>
        <p>I work with large landowners managing landscape health, property owners evaluating tree failure risk, and
          tree care professionals who need help diagnosing fungal diseases. Every engagement ends in a written,
          science based assessment you can act on. The trees I work on are the ones that grow here: valley oak, blue
          oak, interior live oak, and California black oak through the foothills, and ponderosa pine, gray pine, sugar
          pine, incense cedar, and Douglas fir above them.</p>
      </div>
      <div class="svc-grid">
%(cards)s
      </div>
      <div class="btn-row" style="margin-top:2rem">
        <a class="btn" href="/services/">Browse all services %(arrow)s</a>
        <a class="btn btn--ghost" href="/arborist-reports/">See what a report includes</a>
      </div>
    </div>
  </section>

  <section class="section" id="areas">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">Service Area</p>
        <h2>Counties I Serve</h2>
        <p>Independent consulting arborist work throughout the Sierra Nevada foothills and the greater Sacramento
          region, with most site visits inside an hour of Placerville.</p>
      </div>
      <div class="area-grid">
%(areas)s
      </div>
      <p class="eyebrow" style="margin-top:.5rem">Cities and communities</p>
      <ul class="chip-row">
%(cities)s
      </ul>
    </div>
  </section>

  <section class="section section--dark">
    <div class="wrap">
      <div class="split">
        <div class="split-media reveal">
          <img src="%(laet_src)s" srcset="%(laet)s" sizes="(min-width: 900px) 560px, 100vw"
               alt="Laetiporus shelf fungi fruiting from a tree trunk, a brown rot decay organism identified in fungal pathology work"
               width="1200" height="1600" decoding="async">
        </div>
        <div class="reveal">
          <p class="eyebrow eyebrow--light">The Underground Network</p>
          <blockquote class="pullquote">&ldquo;Fungi are the drivers of so many positive and negative outcomes in
            tree health and viability.&rdquo;<cite>Christopher Hodge, ISA Board Certified Master Arborist</cite></blockquote>
          <h2>Why &ldquo;And Fungi&rdquo;?</h2>
          <p>Why have fungi in my business name? Fungi are the drivers of so many positive and negative outcomes in
            tree health and viability. I have spent over fifteen years exploring forests studying fungal diversity and
            working as a consultant for an agricultural amendments company on mycorrhizal species. Being a consultant
            arborist who has spent almost all my life in El Dorado County, California, I have been able to monitor
            individual trees for decades and watch how they respond to different wood decay fungi, weather patterns,
            shifts in land use, and fire. I have spent countless hours searching for spores with a microscope, reading
            research papers, and talking to a wide variety of experts who have spent their lives in the forest to
            grasp how we can keep our trees, forests, and ecosystems healthy.</p>
          <div class="btn-row" style="margin-top:1.6rem">
            <a class="btn btn--primary" href="/fungal-pathology-reports/">See Fungal Pathology Reports</a>
            <a class="btn btn--light" href="/oak-disease-sacramento/">Oak Tree Disease Identification</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--white">
    <div class="wrap">
      <div class="sec-head">
        <h2>Unbiased, Science First Stewardship</h2>
      </div>
      <div class="value-grid">
        <article class="value reveal">
          <h3>Conflict Free Advice</h3>
          <p>I have no removal crews and no financial incentive to recommend unnecessary work, just documented,
            conflict free advice from an ISA Board Certified Master Arborist with TRAQ qualification.</p>
        </article>
        <article class="value reveal">
          <h3>Tailored, Science Based Solutions</h3>
          <p>I work with large landowners managing landscape health, property owners evaluating tree failure risk, and
            tree care professionals who need help diagnosing fungal diseases. Every engagement ends in a written,
            science based assessment you can act on. The trees I work on are the ones that grow here: valley oak, blue
            oak, interior live oak, and California black oak through the foothills, and ponderosa pine, gray pine,
            sugar pine, incense cedar, and Douglas fir above them.</p>
        </article>
      </div>
    </div>
  </section>

  <section class="section section--paper2" id="reviews">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">From Clients</p>
        <h2>What the report was like</h2>
      </div>
      <div class="quote-grid">
%(quotes)s
      </div>
      <div class="review-links">
        <a class="link-arrow" href="%(google)s" target="_blank" rel="noopener">Read reviews on Google %(arrow)s</a>
        <a class="link-arrow" href="/review">Leave us a review %(arrow)s</a>
      </div>
    </div>
  </section>

  <section class="section--tight section">
    <div class="wrap">
      <div class="cta-band reveal">
        <div>
          <p class="eyebrow eyebrow--light">Fees</p>
          <h2>Ask a Tree or Mushroom Question</h2>
          <p>A full site assessment with a written report starts at $500, and the site visit on its own is $250 for up
            to one hour on site. Not sure which you need? Ask me a tree or mushroom question free, fifteen minutes, no
            obligation.</p>
          <div class="btn-row" style="margin-top:1.6rem">
            <a class="btn btn--primary" href="#consult">Request a Consultation</a>
            <a class="btn btn--light" href="%(tel)s">%(phone_icon)s %(phone)s</a>
          </div>
        </div>
        <ul class="price-list">
          <li><b>$500+</b><span>Site assessment with a written report you can act on or submit</span></li>
          <li><b>$250</b><span>Site visit on its own, up to one hour on site</span></li>
          <li><b>Free</b><span>Fifteen minute tree or mushroom question, no obligation</span></li>
        </ul>
      </div>
    </div>
  </section>

%(consult)s
</main>
%(footer)s""" % {
        "header": header_html(), "pine": PINE_SRCSET, "pine_src": PINE_FALLBACK,
        "badge_sm": BADGE_SM_SRCSET, "badge_lg": BADGE_LG_SRCSET,
        "laet": LAET_SRCSET, "laet_src": LAET_FALLBACK, "cards": "\n".join(svc_cards),
        "areas": areas, "cities": cities, "quotes": "\n".join(quotes),
        "consult": consult_html(
            "Contact", None,
            heading="Tell me what you are seeing",
            intro="Call or text (530) 391-6100, or send the form below with a few details about the tree. "
                  "Photos help: a shot of the whole tree, the base of the trunk, and anything unusual on the "
                  "bark or in the canopy is usually enough for me to tell you what service you need."),
        "footer": footer_html(),
        "arrow": ICONS["arrow"], "sms_icon": ICONS["sms"], "phone_icon": ICONS["phone"],
        "check": ICONS["check"], "sms": SMS, "tel": TEL, "phone": PHONE, "google": GOOGLE_REVIEWS,
    }

    description = ("Independent consulting arborist in Placerville, California. ISA Board Certified Master Arborist "
                   "and TRAQ qualified: arborist reports, tree risk assessments, fungal pathology reports, Oak "
                   "Technical Reports and plant health care across El Dorado, Sacramento, Placer and Amador counties.")
    write("index.html", document(
        "Consulting Arborist, El Dorado County and Sacramento | Sierra Tree and Fungi",
        description, "https://sierratreeandfungi.com/", body, LOCAL_BUSINESS_SCHEMA))


# --------------------------------------------------------------------------
# Inner pages
# --------------------------------------------------------------------------
def build_page(filename, slug, title):
    body_lines = read_source(filename)
    data = parse_page(body_lines)
    article, faq, related = render_blocks(data["blocks"])
    faq_html, faq_schema = render_faq(faq)

    # Breadcrumbs: link Home and Services, current page is plain text
    crumbs = []
    for idx, crumb in enumerate(data["crumbs"]):
        m = LINK_RE.fullmatch(crumb.strip())
        if m:
            target = resolve_href(m.group(2))
            if target:
                crumbs.append('<li><a href="%s">%s</a></li>' % (esc(target), esc(m.group(1))))
            else:
                crumbs.append("<li>%s</li>" % esc(m.group(1)))
        else:
            crumbs.append('<li aria-current="page">%s</li>' % esc(re.sub(LINK_RE, r"\1", crumb)))
    if not crumbs:
        crumbs = ['<li><a href="/">Home</a></li>', '<li aria-current="page">%s</li>' % esc(data["h1"])]

    # lede = first paragraph of the article, pulled up into the hero
    lede = ""
    m = re.match(r'^<p class="lead">(.*?)</p>\n?', article, re.S)
    if m:
        lede = m.group(1)
        article = article[m.end():]

    related_block = ""
    chips = render_chips(related)
    if chips:
        related_block = """
      <nav class="related" aria-label="Related pages">
        <h2>Related pages</h2>
        %s
      </nav>""" % chips

    service_hint = SERVICE_FOR_PAGE.get(slug)
    page_label = LABELS.get("/" + slug, data["h1"])

    body = """%(header)s
<main id="main">
  <section class="page-hero">
    <div class="wrap">
      <ol class="crumbs">%(crumbs)s</ol>
      <p class="eyebrow eyebrow--light">%(eyebrow)s</p>
      <h1>%(h1)s</h1>
      %(lede)s
      <div class="btn-row">
        <a class="btn btn--primary" href="#consult">Request a Consultation %(arrow)s</a>
        <a class="btn btn--light" href="%(tel)s">%(phone_icon)s %(phone)s</a>
        <a class="btn btn--light" href="%(sms)s">%(sms_icon)s Text a photo</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="doc">
        <aside class="toc" id="pageToc" hidden>
          <h2>On this page</h2>
        </aside>
        <article class="prose">
%(article)s
%(faq)s
%(related)s
        </article>
      </div>
    </div>
  </section>

%(consult)s
</main>
%(footer)s""" % {
        "header": header_html(slug),
        "crumbs": "".join(crumbs),
        "eyebrow": esc(data["eyebrow"] or "Consulting Arborist"),
        "h1": esc(data["h1"]),
        "lede": '<p class="lede">%s</p>' % lede if lede else "",
        "article": article,
        "faq": faq_html,
        "related": related_block,
        "consult": consult_html(page_label, service_hint),
        "footer": footer_html(),
        "arrow": ICONS["arrow"], "tel": TEL, "sms": SMS, "phone": PHONE,
        "phone_icon": ICONS["phone"], "sms_icon": ICONS["sms"],
    }

    description = re.sub(r"<[^>]+>", "", lede or data["h1"])
    description = re.sub(r"\s+", " ", html.unescape(description)).strip()
    if len(description) > 185:
        description = description[:182].rsplit(" ", 1)[0] + "…"

    schema = breadcrumb_schema(page_label, "/" + slug)
    if faq_schema:
        schema += "\n<script type=\"application/ld+json\">\n%s\n</script>" % faq_schema

    write(os.path.join(slug, "index.html"),
          document(title, description, "https://sierratreeandfungi.com/%s/" % slug, body, schema,
                   body_attr=' data-service="%s"' % esc(service_hint) if service_hint else ""))


# --------------------------------------------------------------------------
def write(relpath, content):
    full = os.path.join(ROOT, relpath)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    print("  wrote %s (%d KB)" % (relpath, len(content) // 1024))


def build_extras():
    urls = ["https://sierratreeandfungi.com/"] + \
           ["https://sierratreeandfungi.com/%s/" % slug for _, slug, _ in PAGES]
    entries = "\n".join(
        "  <url><loc>%s</loc><changefreq>monthly</changefreq><priority>%s</priority></url>"
        % (u, "1.0" if u.endswith(".com/") else "0.8") for u in urls)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % entries)
    write("robots.txt",
          "User-agent: *\nAllow: /\n\nSitemap: https://sierratreeandfungi.com/sitemap.xml\n")

    not_found = """%(header)s
<main id="main">
  <section class="page-hero">
    <div class="wrap">
      <ol class="crumbs"><li><a href="/">Home</a></li><li aria-current="page">Page not found</li></ol>
      <p class="eyebrow eyebrow--light">404</p>
      <h1>That page is not here</h1>
      <p class="lede">The page you were looking for has moved or never existed. Start from the services below, or
        call or text %(phone)s and describe the tree.</p>
      <div class="btn-row">
        <a class="btn btn--primary" href="/services/">All services %(arrow)s</a>
        <a class="btn btn--light" href="%(tel)s">%(phone_icon)s %(phone)s</a>
      </div>
    </div>
  </section>
%(consult)s
</main>
%(footer)s""" % {"header": header_html(), "consult": consult_html(
            "Contact", None,
            heading="Tell me what you are seeing",
            intro="Call or text (530) 391-6100, or send the form below with a few details about the tree. "
                  "Photos help: a shot of the whole tree, the base of the trunk, and anything unusual on the "
                  "bark or in the canopy is usually enough for me to tell you what service you need."),
        "footer": footer_html(),
                 "arrow": ICONS["arrow"], "tel": TEL, "phone": PHONE, "phone_icon": ICONS["phone"]}
    write("404.html", document("Page not found | Sierra Tree and Fungi",
                               "That page is not here. Browse consulting arborist services or call (530) 391-6100.",
                               "https://sierratreeandfungi.com/404.html", not_found))


def main():
    if not os.path.isdir(SRC):
        sys.exit("Source pages not found at %s" % SRC)
    print("Building Sierra Tree & Fungi…")
    build_home()
    for filename, slug, title in PAGES:
        build_page(filename, slug, title)
    build_extras()
    print("Done: %d pages." % (len(PAGES) + 2))


if __name__ == "__main__":
    main()
