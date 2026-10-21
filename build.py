"""Build the multi-page Delta Flood Ready site from the single source file.

Source: ~/Claude/Artifacts/delta-flood-ready-toolkit.html (all sections, styles, and script)
Outputs:
  - this folder: full HTML pages for GitHub Pages
  - ~/Claude/Artifacts/delta-flood-ready/: the same pages for the artifact (index without a document wrapper)
"""
import os
import re

HOME = os.path.expanduser('~')
SRC = os.path.join(HOME, 'Claude/Artifacts/delta-flood-ready-toolkit.html')
SITE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HOME, 'Claude/Artifacts/delta-flood-ready')

# file, section id, button label, page title
PAGES = [
    ('index.html', 'summary', 'Summary', 'Delta Flood Ready Toolkit'),
    ('flow.html', 'connect', 'Flow', 'How the Pieces Connect'),
    ('tools.html', 'tsp', 'Tools and places', 'Tools, Spaces, and Places'),
    ('brief.html', 'brief', 'Public brief', 'The Public Brief'),
    ('map.html', 'map', 'Map', 'The Delta Map'),
    ('website.html', 'website', 'Website', 'The Program Website'),
    ('library-corner.html', 'corner', 'Library corner', 'The Library Disaster Corner'),
]
FILE_OF = {sid: f for f, sid, _, _ in PAGES}

src = open(SRC).read()
style = src[src.index('<style>'):src.index('</style>') + len('</style>')]
script = src[src.index('<script>'):src.index('</script>') + len('</script>')]
header = src[src.index('  <header>'):src.index('  </header>') + len('  </header>')]
sections = {m.group(1): m.group(0) for m in re.finditer(r'  <section id="(\w+)">.*?\n  </section>', src, re.S)}

EXTRA_CSS = '''<style>
.jb[aria-current="page"]{background:var(--navy);color:var(--bg);border-color:var(--navy)}
.page-sec{margin-top:8px}
.crumb{font-size:.85rem;margin-bottom:10px}
.crumb a{color:var(--gray);text-decoration:none;font-weight:700}
.crumb a:hover{color:var(--navy)}
.foot{margin-top:40px}
</style>'''

RESET = ('<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
         'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>')

NOTE = ('<p class="note foot">These are illustrative mockups. Every flow, date, percentage, and map zone is invented '
        'for the design and is not a real forecast. Program names and web addresses are placeholders.</p>')


def nav(current):
    cur = ' aria-current="page"'
    links = '\n'.join(
        f'  <a class="jb" href="{f}"{cur if f == current else ""}>{label}</a>'
        for f, _, label, _ in PAGES)
    return f'<nav class="jump" aria-label="Toolkit pages"><div class="jump-in">\n{links}\n</div></nav>\n'


def pager(i):
    parts = []
    if i > 0:
        f, _, label, _ = PAGES[i - 1]
        parts.append(f'<a class="prev" href="{f}">← {label}</a>')
    if i < len(PAGES) - 1:
        f, _, label, _ = PAGES[i + 1]
        parts.append(f'<a class="next" href="{f}">{label} →</a>')
    else:
        parts.append('<a class="next" href="index.html">Back to summary ↑</a>')
    return '<div class="pn">' + ''.join(parts) + '</div>'


def body_for(i):
    f, sid, _, _ = PAGES[i]
    sec = sections[sid].replace(f'<section id="{sid}">', f'<section id="{sid}" class="page-sec">', 1)
    if sid == 'summary':
        for other_sid, other_f in FILE_OF.items():
            sec = sec.replace(f'href="#{other_sid}"', f'href="{other_f}"')
        top = header + '\n\n'
        note = ''
    else:
        sec = sec.replace('<h2>', '<h1>', 1).replace('</h2>', '</h1>', 1)
        top = '  <p class="crumb"><a href="index.html">Delta Flood Ready Toolkit</a></p>\n'
        note = NOTE
        if sid == 'website':
            sec += '\n\n' + sections['sources']
    return (nav(f) + '<div class="wrap">\n' + top + sec + '\n  ' + pager(i) + '\n  ' + note +
            '\n</div>\n\n' + script + '\n')


def head_bits(title):
    return (f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            + style + '\n' + EXTRA_CSS + '\n')


def full_doc(title, body):
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="description" content="A rural flood early-warning pilot for Delta, Utah, with illustrative '
            'mockups of the public brief, map, program website, and library disaster corner.">\n'
            + RESET + '\n' + head_bits(title) + '</head>\n<body>\n' + body + '</body>\n</html>\n')


os.makedirs(ART, exist_ok=True)
for i, (f, sid, _, title) in enumerate(PAGES):
    body = body_for(i)
    doc = full_doc(title, body)
    open(os.path.join(SITE, f), 'w').write(doc)
    # the artifact wraps its main page itself, so index there is head bits plus body only
    open(os.path.join(ART, f), 'w').write(head_bits(title) + body if f == 'index.html' else doc)
print('built', len(PAGES), 'pages')
