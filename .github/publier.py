#!/usr/bin/env python3
"""Publie les chroniques de .github/a-venir/ dont la date est arrivée.

Chaque dossier AAAA-MM-JJ-slug contient index.html, source.json et les deux
couvertures. Le script les range, puis met à jour manifest, liste et sitemap.
Reprend le format de redaction.html (renderArticleCardsHTML, updateSitemap).
Sans argument : date du jour à Paris. Avec un argument : cette date (essais).
"""
import html
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RACINE = Path(__file__).resolve().parent.parent
ATTENTE = RACINE / ".github/a-venir"
CHRON = RACINE / "chroniques"
SITE = "https://www.barbenoiretattoo.com"
MOIS = "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split()


def esc(t):
    return html.escape(t or "", quote=True).replace("&#x27;", "&#39;")


def date_fr(iso):
    a, m, j = iso.split("-")
    return f"{int(j)} {MOIS[int(m) - 1]} {a}"


def cartes(posts):
    blocs = []
    for p in sorted(posts, key=lambda x: x.get("date", ""), reverse=True):
        img = f'<img src="{esc(p["cover"])}" alt="{esc(p.get("coverAlt") or p["title"])}" loading="lazy" decoding="async">'
        lignes = [
            f'        <span class="plaque">{img}</span>',
            f'        <span class="plate article-date">{esc(date_fr(p["date"]))}</span>',
            f'        <h2>{esc(p["title"])}</h2>',
        ]
        if p.get("summary"):
            lignes.append(f'        <p class="excerpt">{esc(p["summary"])}</p>')
        lignes.append('        <span class="read-more">Lire l’article →</span>')
        blocs.append(f'      <a class="article-card reveal" href="{esc(p["slug"])}/">\n' + "\n".join(lignes) + "\n      </a>")
    return "\n".join(blocs)


def maj_liste(posts):
    f = CHRON / "index.html"
    t = f.read_text(encoding="utf-8")
    deb, fin = "<!-- ARTICLES:START -->", "<!-- ARTICLES:END -->"
    a, b = t.index(deb) + len(deb), t.index(fin)
    f.write_text(t[:a] + "\n" + cartes(posts) + "\n      " + t[b:], encoding="utf-8")


def maj_sitemap(slug, date):
    f = RACINE / "sitemap.xml"
    t = f.read_text(encoding="utf-8")
    url = f"{SITE}/chroniques/{slug}/"
    t = re.sub(r"[ \t]*<url>\s*<loc>" + re.escape(url) + r"</loc>[\s\S]*?</url>\n?", "", t)
    bloc = f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{date}</lastmod>\n  </url>\n"
    f.write_text(t.replace("</urlset>", bloc + "</urlset>"), encoding="utf-8")


def publier(jour):
    faits = []
    fichier_manifest = CHRON / "manifest.json"
    posts = json.loads(fichier_manifest.read_text(encoding="utf-8"))
    for d in sorted(ATTENTE.glob("*")) if ATTENTE.exists() else []:
        date = d.name[:10]
        if not d.is_dir() or date > jour:
            continue
        src = json.loads((d / "source.json").read_text(encoding="utf-8"))
        slug = src["slug"]
        (CHRON / slug).mkdir(exist_ok=True)
        shutil.copy(d / "index.html", CHRON / slug / "index.html")
        shutil.copy(d / "source.json", CHRON / "sources" / f"{slug}.json")
        for ext in ("jpg", "webp"):
            shutil.copy(d / f"couverture.{ext}", CHRON / "images" / f"{slug}-couverture.{ext}")
        posts = [p for p in posts if p["slug"] != slug] + [{
            "slug": slug, "title": src["title"], "summary": src["summary"], "date": date,
            "cover": f"{SITE}/{src['cover']}", "coverAlt": src["coverAlt"],
        }]
        maj_sitemap(slug, date)
        shutil.rmtree(d)
        faits.append(slug)
    if faits:
        fichier_manifest.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        maj_liste(posts)
    return faits


if __name__ == "__main__":
    jour = sys.argv[1] if len(sys.argv) > 1 else datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%d")
    print("\n".join(publier(jour)) or "Rien à publier.")
