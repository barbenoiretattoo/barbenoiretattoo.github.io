"""Écrit la galerie en dur dans index.html (entre GALERIE:START et GALERIE:END)
pour que Google et les IA voient les photos sans exécuter de JavaScript.
Au passage : noms de fichiers propres (sans espaces ni accents) et photos ramenées à 1400 px.
Lancé par .github/workflows/galerie.yml à chaque envoi dans photos/."""
import html, os, re, unicodedata, urllib.parse
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = re.compile(r'\.(jpe?g|png|webp|gif|avif)$', re.I)

def alt(name):  # même règle que l'ancien altFromName du site
    base = re.sub(r'[-_\s]+', ' ', IMG.sub('', name))
    base = re.sub(r'^\d{4} \d{2}( \d{2})? ?', '', base).strip()
    return f"Tatouage {base or 'fine line et dotwork'} - Barbe Noire Tattoo, Mouvaux"

def slug(name):  # « Tattoo Rose des vents.JPG » → « rose-des-vents.jpg »
    base, ext = os.path.splitext(name)
    base = unicodedata.normalize('NFKD', base).encode('ascii', 'ignore').decode().lower()
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-')
    base = re.sub(r'^(tattoo|tatouage)-', '', base) or 'tatouage'
    return base + ext.lower().replace('.jpeg', '.jpg')

def normalize(folder):
    """Renomme proprement et ramène à 1400 px max les photos envoyées telles quelles."""
    for name in sorted(os.listdir(folder)):
        if not IMG.search(name):
            continue
        src = os.path.join(folder, name)
        new = slug(name)
        if new != name:
            stem, ext = os.path.splitext(new)
            i = 2
            while os.path.exists(os.path.join(folder, new)):
                new = f'{stem}-{i}{ext}'; i += 1
            os.rename(src, os.path.join(folder, new))
            src = os.path.join(folder, new)
        im = Image.open(src)
        if max(im.size) > 1400 and im.format in ('JPEG', 'PNG', 'WEBP'):
            fmt = im.format
            im = ImageOps.exif_transpose(im)
            im.thumbnail((1400, 1400))
            if fmt == 'JPEG':
                im.convert('RGB').save(src, quality=80, optimize=True, progressive=True)
            else:
                im.save(src, optimize=True)

normalize(os.path.join(ROOT, 'photos'))
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
