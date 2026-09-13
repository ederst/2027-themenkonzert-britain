#!/usr/bin/env python3
# make_site.py: build a self-contained, static, German-UI browseable site
# (docs/index.html, served by GitHub Pages from the docs/ folder)
# from the two canonical semicolon CSVs.
# Stdlib only: csv, html, json. No third-party deps, no network, no build step.
# The HTML embeds the row data as JSON + a tiny vanilla JS filter; works from
# file:// and any static host / gh-pages. CSV stays the single source of truth;
# this script only renders it.
import csv, html, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "docs" / "index.html"
TS   = ROOT / "britain-arrangements.csv"
GS   = ROOT / "guest-acts.csv"

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

# German UI labels mapped onto known British-only array (reuses CSV data as-is)
SECTIONS = [
    ("arrangements", "Arrangements (Blasmusik)", t_rows, t_header, len(t_rows)),
    ("guests", "Gäste (Bands · Dudelsack · Brass & Klassik)", g_rows, g_header, len(g_rows)),
]

def rows_json(section_rows):
    return json.dumps(section_rows, ensure_ascii=False).replace("</", "<\\/")

def cell(c):
    """Escaped cell; render as clickable link if it is a URL (https/http)."""
    if c.startswith(("https://", "http://")):
        return f'<a href="{c}" target="_blank" rel="noopener">{c}</a>'
    return c if c else '<span class="empty">–</span>'

parts = ["""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Großbritannien Themenkonzert 2027, Auswahl-Hilfe</title>
<style>
:root{--ink:#1c2733;--mut:#6b7280;--line:#e2e8f0;--acc:#1d4ed8;--soft:#f1f5f9;--good:#166534;--warn:#92400e}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:#f8fafc;line-height:1.45}
header{padding:2rem 1.25rem 1.25rem;background:linear-gradient(120deg,#0f2f5e,#1d4ed8);color:#fff}
header h1{margin:0 0 .25rem}header p{margin:0;color:#c7d6f2}
main{max-width:1180px;margin:0 auto;padding:1.25rem}
.tools{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0;position:sticky;top:0;background:#f8fafc;padding:.4rem 0;z-index:5}
.tools input[type=search]{flex:1 1 220px;min-width:200px;padding:.6rem .8rem;border:1px solid var(--line);border-radius:.5rem;font-size:.95rem}
select{padding:.6rem .7rem;border:1px solid var(--line);border-radius:.5rem;background:#fff;font-size:.9rem}
section{margin:2rem 0}
h2{display:flex;align-items:center;gap:.5rem;font-size:1.1rem;margin:0 0 .9rem;padding-bottom:.4rem;border-bottom:2px solid var(--line)}
h2 .count{color:var(--mut);font-weight:400;font-size:.85rem}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:.6rem;background:#fff}
table{border-collapse:collapse;width:100%;font-size:.85rem;min-width:740px}
th,td{text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--line);vertical-align:top}
th{position:sticky;top:0;background:#fff;font-size:.7rem;text-transform:uppercase;letter-spacing:.4px;color:var(--mut)}
tbody tr:hover{background:var(--soft)}
a{color:var(--acc);text-decoration:none;white-space:nowrap}a:hover{text-decoration:underline}
.tag{display:inline-block;padding:.05rem .45rem;border-radius:999px;background:var(--soft);font-size:.72rem;color:var(--mut)}
.badge-gut{background:#dcfce7;color:var(--good)}
.badge-warn{background:#fef3c7;color:var(--warn)}
.empty{color:var(--mut);font-style:italic}
footer{padding:1.5rem 1.25rem 2.5rem;text-align:center;color:var(--mut);font-size:.8rem}
</style>
</head>
<body>
<header>
<h1>Großbritannien wichtig · Themenkonzert 2027</h1>
<p>Was wir spielen können: Arrangements &amp; Gastakte für unsere Blasmusik. Gefiltert, sortierbar, alle Links anklickbar.</p>
</header>
<main>
<div class="tools">
<input type="search" id="q" placeholder="Suchen… z.B. „Queen“, „Viva la Vida“, „Dirigiersteife“" autocomplete="off">
<select id="g1"><option value="">Genre: alle</option><option>pop/rock</option><option>classical</option><option>film</option><option>musical</option></select>
<select id="d1"><option value="">Schwierigkeit: alle</option><option>Leicht</option><option>Mittel</option><option>Schwer</option></select>
</div>
"""]

for sid, title, rows, header, expect in SECTIONS:
    hdr_cells = "".join(f"<th>{html.escape(h)}</th>" for h in header)
    # pre-render tbody (basic); real filtering is client-side on the embedded JSON
    parts.append(f'''<section id="{sid}">
<h2>{title} <span class="count js-cnt" data-src="{sid}"></span></h2>
<div class="wrap"><table>
<thead><tr>{hdr_cells}</tr></thead>
<tbody data-t="{sid}">{''.join('<tr>'+''.join(f'<td>{cell(c)}</td>' for c in row)+'</tr>' for row in rows)}</tbody>
</table></div>
</section>
''')

parts.append(f"""<footer>Stand der Recherche · Großbritannien-Themenkonzert 2027 · {len(t_rows)} Arrangements, {len(g_rows)} Gastakte. Datenquelle: <code>.csv</code> (eine Wahrheit), diese Seite wird daraus erzeugt.</footer>
<script>
const DATA = {{
  arrangements: {rows_json(t_rows)},
  guests: {rows_json(g_rows)}
}};
const COLS = {{
  arrangements: {json.dumps(t_header, ensure_ascii=False)},
  guests: {json.dumps(g_header, ensure_ascii=False)}
}};
const PINS = {{arrangements:{len(t_rows)}, guests:{len(g_rows)}}};
function el(s){{return document.querySelector(s)}}
function filter(sid){{
  const q=(el('#q').value||'').toLowerCase();
  const genre=el('#g1').value, diff=el('#d1').value;
  const rows=DATA[sid], tbl=el(`#${{sid}} tbody[data-t]`);
  let shown=0, h='';
  rows.forEach((r,i)=>{{
    const hay=(r.join(' ')+COLS[sid].join(' ')).toLowerCase();
    if(q && !hay.includes(q)) return;
    const g=r[COLS[sid].indexOf('Genre')]; const d=r[COLS[sid].indexOf('Difficulty')];
    if(genre && !(g||'').toLowerCase().includes(genre.toLowerCase())) return;
    if(diff && !(d||'').toLowerCase().includes(diff.toLowerCase())) return;
    shown++;
    h+='<tr>'+r.map(c=>c?(c.startsWith('https://')||c.startsWith('http://'))?'<td><a href="'+c+'" target="_blank" rel="noopener">'+c+'</a></td>':'<td>'+c+'</td>':'<td class="empty">–</td>').join('')+'</tr>';
  }});
  tbl.innerHTML=h;
  el(`[data-src=${{sid}}]`).textContent='('+shown+' von '+PINS[sid]+')';
}}
['q','g1','d1'].forEach(id=>el('#'+id).addEventListener('input',()=>{{filter('arrangements');filter('guests')}}));
filter('arrangements');filter('guests');
</script>
</body>
</html>""")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("".join(parts), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size}b, {len(t_rows)} arr + {len(g_rows)} guest rows embedded)")