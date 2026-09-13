#!/usr/bin/env python3
# make_site.py: build self-contained, static, German-UI browseable pages
# (docs/index.html landing + docs/arrangements.html + docs/guests.html,
# served by GitHub Pages from the docs/ folder) from the two canonical
# semicolon CSVs. Stdlib only: csv, html, json. No third-party deps, no
# network, no build step. Each section page embeds its row data as JSON +
# a tiny vanilla JS filter; works from file:// and any static host / gh-pages.
# CSV stays the single source of truth; this script only renders it.
import csv, html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TS = ROOT / "britain-arrangements.csv"
GS = ROOT / "guest-acts.csv"


def load(p, expected_cols):
    rows = []
    with open(p, encoding="utf-8", newline="") as fh:
        r = csv.reader(fh, delimiter=";")
        header = next(r)
        if len(header) != expected_cols:
            raise SystemExit(f"{p.name}: {len(header)} cols, expected {expected_cols}")
        for i, row in enumerate(r, 2):
            if len(row) != expected_cols:
                raise SystemExit(f"{p.name}:{i}: {len(row)} cols != {expected_cols}")
            rows.append([html.escape(c).strip() for c in row])
    return header, rows


t_header, t_rows = load(TS, 10)
g_header, g_rows = load(GS, 16)

SECTIONS = {
    "arrangements": ("Arrangements (Blasmusik)", t_rows, t_header),
    "guests": ("Gäste (Bands · Dudelsack · Brass & Klassik)", g_rows, g_header),
}


def rows_json(rows):
    return json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")


def cell(c):
    """Escaped cell; render as clickable link if it is a URL (https/http)."""
    if c.startswith(("https://", "http://")):
        return f'<a href="{c}" target="_blank" rel="noopener">{c}</a>'
    return c if c else '<span class="empty">–</span>'


HEAD = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root{{--ink:#1c2733;--mut:#6b7280;--line:#e2e8f0;--acc:#1d4ed8;--soft:#f1f5f9;--good:#166534;--warn:#92400e}}
*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:#f8fafc;line-height:1.45}}
header{{padding:2rem 1.25rem 1.25rem;background:linear-gradient(120deg,#0f2f5e,#1d4ed8);color:#fff}}
header h1{{margin:0 0 .25rem}}header p{{margin:0;color:#c7d6f2}}
main{{max-width:1180px;margin:0 auto;padding:1.25rem}}
.tools{{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0;position:sticky;top:0;background:#f8fafc;padding:.4rem 0;z-index:5}}
.tools input[type=search]{{flex:1 1 220px;min-width:200px;padding:.6rem .8rem;border:1px solid var(--line);border-radius:.5rem;font-size:.95rem}}
select{{padding:.6rem .7rem;border:1px solid var(--line);border-radius:.5rem;background:#fff;font-size:.9rem}}
section{{margin:2rem 0}}
h2{{display:flex;align-items:center;gap:.5rem;font-size:1.1rem;margin:0 0 .9rem;padding-bottom:.4rem;border-bottom:2px solid var(--line)}}
h2 .count{{color:var(--mut);font-weight:400;font-size:.85rem}}
.wrap{{overflow-x:auto;border:1px solid var(--line);border-radius:.6rem;background:#fff}}
table{{border-collapse:collapse;width:100%;font-size:.85rem;min-width:740px}}
th,td{{text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--line);vertical-align:top}}
th{{position:sticky;top:0;background:#fff;font-size:.7rem;text-transform:uppercase;letter-spacing:.4px;color:var(--mut)}}
tbody tr:hover{{background:var(--soft)}}
a{{color:var(--acc);text-decoration:none;white-space:nowrap}}a:hover{{text-decoration:underline}}
.empty{{color:var(--mut);font-style:italic}}
nav.cards{{display:grid;gap:1rem;margin:2rem 0;max-width:640px}}
nav.cards a{{display:block;padding:1.3rem 1.5rem;border:1px solid var(--line);border-radius:.6rem;background:#fff;text-decoration:none;white-space:normal;color:var(--ink)}}
nav.cards a:hover{{border-color:var(--acc)}}
nav.cards b{{display:block;font-size:1.1rem;color:var(--acc)}}
nav.cards span{{display:block;color:var(--mut);font-size:.85rem;margin-top:.15rem}}
footer{{padding:1.5rem 1.25rem 2.5rem;text-align:center;color:var(--mut);font-size:.8rem}}
.badge{{display:inline-block;padding:.05rem .45rem;border-radius:999px;background:var(--soft);font-size:.72rem;color:var(--mut)}}
</style>
</head>
<body>
<header>
<h1>Themenkonzert 2027 - Großbritannien</h1>
<p>Was wir spielen können: Arrangements &amp; Gastakte.</p>
</header>
"""

FOOTER = "<footer>Stand der Recherche · Großbritannien-Themenkonzert 2027 · {a} Arrangements, {g} Gastakte.</footer>"


def page(sid, title):
    """One section page: tools + table + single-section filter script."""
    sec_title, rows, header = SECTIONS[sid]
    hdr_cells = "".join(f"<th>{html.escape(h)}</th>" for h in header)
    has_genre = "Genre" in header
    has_diff = "Difficulty" in header
    gj = header.index("Genre") if has_genre else None
    genres = sorted({r[gj] for r in rows if r[gj]}) if has_genre else []
    sel_genre = ('<select id="g1"><option value="">Genre: alle</option>'
                 + "".join(f'<option>{html.escape(g)}</option>' for g in genres)
                 + "</select>") if has_genre else ""
    sel_diff = '<select id="d1"><option value="">Schwierigkeit: alle</option><option>Leicht</option><option>Mittel</option><option>Schwer</option></select>' if has_diff else ""
    tools = f'<div class="tools"><input type="search" id="q" placeholder="Suchen…" autocomplete="off">{sel_genre}{sel_diff}</div>'
    body = f'''{tools}
<section id="{sid}">
<h2>{sec_title} <span class="count" id="cnt"></span></h2>
<div class="wrap"><table>
<thead><tr>{hdr_cells}</tr></thead>
<tbody id="tb">{''.join('<tr>'+''.join(f'<td>{cell(c)}</td>' for c in row)+'</tr>' for row in rows)}</tbody>
</table></div>
</section>
<script>
const DATA = {rows_json(rows)};
const COLS = {json.dumps(header, ensure_ascii=False)};
const GENRE = {json.dumps(has_genre)};
const DIFF = {json.dumps(has_diff)};
function el(s){{return document.querySelector(s)}}
function filter(){{
  const q=(el('#q').value||'').toLowerCase();
  const genre = GENRE ? el('#g1').value : '';
  const diff = DIFF ? el('#d1').value : '';
  let shown=0, h='';
  DATA.forEach((r,i)=>{{
    const hay=(r.join(' ')+COLS.join(' ')).toLowerCase();
    if(q && !hay.includes(q)) return;
    if(genre){{
      const gj=COLS.indexOf('Genre'); if(gj<0) return;
      if(!(r[gj]||'').toLowerCase().includes(genre.toLowerCase())) return;
    }}
    if(diff){{
      const dj=COLS.indexOf('Difficulty'); if(dj<0) return;
      const v=parseFloat(r[dj]);
      if(!(diff==='Leicht' ? v>0 && v<=2 : diff==='Mittel' ? v>=2.5 && v<=3.5 : v>=4)) return;
    }}
    shown++;
    h+='<tr>'+r.map(c=>c?(c.startsWith('https://')||c.startsWith('http://'))?'<td><a href="'+c+'" target="_blank" rel="noopener">'+c+'</a></td>':'<td>'+c+'</td>':'<td class="empty">–</td>').join('')+'</tr>';
  }});
  el('#tb').innerHTML=h;
  el('#cnt').textContent='('+shown+' von '+DATA.length+')';
}}
const ids=['q','g1','d1'];
ids.forEach(id=>{{const e=el('#'+id); if(e) e.addEventListener('input',filter);}});
filter();
</script>'''
    return HEAD.format(title=title) + "<main>" + body + FOOTER.format(a=len(t_rows), g=len(g_rows)) + "</main></body></html>"


def landing():
    cards = ' '.join(
        f'<a href="{sid}.html"><b>{SECTIONS[sid][0].split(" (")[0]}</b><span>{len(SECTIONS[sid][1])} Einträge · <span class="badge">{sid}</span></span><span>Alle Einträge durchsuchen, filtern, Links anklicken.</span></a>'
        for sid in ("arrangements", "guests")
    )
    body = f'<nav class="cards">{cards}</nav><p>Diese Liste wird aus den <code>.csv</code>-Daten erzeugt. Stand siehe Fußzeile.</p>'
    return HEAD.format(title="Großbritannien Themenkonzert 2027, Auswahl-Hilfe") + "<main>" + body + FOOTER.format(a=len(t_rows), g=len(g_rows)) + "</main></body></html>"


DOCS.mkdir(parents=True, exist_ok=True)
files = {
    "index.html": landing(),
    "arrangements.html": page("arrangements", "Arrangements · Großbritannien Themenkonzert 2027"),
    "guests.html": page("guests", "Gäste · Großbritannien Themenkonzert 2027"),
}
for name, content in files.items():
    (DOCS / name).write_text(content, encoding="utf-8")
print(
    f"wrote {DOCS/'index.html'} ({len(files['index.html'])}b) + arrangements.html "
    f"({len(files['arrangements.html'])}b) + guests.html ({len(files['guests.html'])}b); "
    f"{len(t_rows)} arr + {len(g_rows)} guest rows"
)