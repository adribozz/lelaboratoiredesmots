# Contrôle SEO / liens de toutes les pages HTML. Usage : python _gen/check.py
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
err = []
for f in sorted(ROOT.glob("*.html")):
    s = f.read_text(encoding="utf-8")
    n = f.name
    t = re.search(r"<title>(.*?)</title>", s, re.S)
    if not t: err.append(f"{n}: pas de <title>")
    elif len(t.group(1)) > 65: err.append(f"{n}: title {len(t.group(1))} car.")
    if not re.search(r'<meta name="description" content="[^"]{20,}"', s): err.append(f"{n}: meta description")
    if 'rel="canonical"' not in s: err.append(f"{n}: canonical")
    nh1 = len(re.findall(r"<h1[\s>]", s))
    if nh1 != 1: err.append(f"{n}: {nh1} h1")
    for img in re.findall(r"<img\b[^>]*>", s):
        if "alt=" not in img: err.append(f"{n}: img sans alt {img[:80]}")
        src = re.search(r'src="([^"]+)"', img)
        if src and not src.group(1).startswith("http") and not (ROOT / src.group(1)).exists(): err.append(f"{n}: image manquante {src.group(1)}")
    for href in re.findall(r'href="([^"#:]+\.html)(?:#[^"]*)?"', s):
        if not (ROOT / href).exists(): err.append(f"{n}: lien cassé {href}")
    for ld in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(ld)
        except ValueError as e: err.append(f"{n}: JSON-LD invalide {e}")
    if n not in ("credits.html", "mentions-legales.html", "404.html", "index.html") and "MAILCHIMP_ACTION_URL" not in s:
        err.append(f"{n}: newsletter absente")
    if n.startswith("landing") and "helloasso.com" not in s: err.append(f"{n}: aucun lien HelloAsso")

tout = "".join(f.read_text(encoding="utf-8") for f in ROOT.glob("*.html"))
attendus = ["ateliers-d-ecriture-creative-jeudi-apres-midi-2", "jeudi-15-octobre-de-14h-a-16h-2", "jeudi-5-novembre", "jeudi-19-novembre", "jeudi-3-decembre",
            "jeudi-17-decembre", "inscription-aux-ateliers-d-ecriture-du-jeudi-soir", "adhesions/adhesion", "mardi-6-octobre", "mardi-20-octobre",
            "mardi-3-novembre", "mardi-17-novembre", "mardi-8-decembre", "mardi-15-decembre-de-19h-a-21h-2"]
err += [f"HelloAsso manquant : {a}" for a in attendus if a not in tout]
print("\n".join(err) or "OK : aucune anomalie")
sys.exit(1 if err else 0)
