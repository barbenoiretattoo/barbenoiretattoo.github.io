"""Écrit la galerie en dur dans index.html (entre GALERIE:START et GALERIE:END)
pour que Google et les IA voient les photos sans exécuter de JavaScript.
Lancé par .github/workflows/galerie.yml à chaque envoi dans photos/."""
import html, os, re, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = re.compile(r'\.(jpe?g|png|webp|gif|avif)$', re.I)

def alt(name):  # même règle que l'ancien altFromName du site
    base = re.sub(r'[-_\s]+', ' ', IMG.sub('', name))
    base = re.sub(r'^\d{4} \d{2}( \d{2})? ?', '', base).strip()
    return f"Tatouage {base or 'fine line et dotwork'} - Barbe Noire Tattoo, Mouvaux"

names = sorted((n for n in os.listdir(os.path.join(ROOT, 'photos')) if IMG.search(n)), reverse=True)
items = [
    f'<button class="gallery-item" aria-label="Agrandir : {html.escape(alt(n))}">'
    f'<img src="photos/{urllib.parse.quote(n)}" alt="{html.escape(alt(n))}" loading="lazy" decoding="async"></button>'
    for n in names
] or ['<div class="gallery-empty" id="galleryEmpty">La galerie se prépare. Retrouvez en attendant tous mes travaux sur Instagram.</div>']

path = os.path.join(ROOT, 'index.html')
page = open(path, encoding='utf-8').read()
block = '<!-- GALERIE:START -->\n      ' + '\n      '.join(items) + '\n      <!-- GALERIE:END -->'
new, n = re.subn(r'<!-- GALERIE:START -->[\s\S]*?<!-- GALERIE:END -->', lambda m: block, page)
assert n == 1, 'marqueurs GALERIE introuvables dans index.html'
if new != page:
    open(path, 'w', encoding='utf-8').write(new)
    print(f'galerie : {len(names)} photo(s)')
