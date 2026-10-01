# Génère les pages internes statiques (en-tête, pied, SEO partagés).
# Usage : python _gen/gen.py  (depuis le dossier site/)
import json, html
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://le-laboratoire-des-mots.fr"
H = "https://www.helloasso.com/associations/le-laboratoire-des-mots"
HA_ADHESION = H + "/adhesions/adhesion"
HA_FORFAIT = H + "/evenements/inscription-aux-ateliers-d-ecriture-du-jeudi-soir"
MAIL, TEL, TEL_LIEN = "lelabodesmots@outlook.fr", "06 47 00 84 70", "+33647008470"
INSTA = "https://www.instagram.com/cecilia_tarek/"
MOIS = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MOIS_SLUG = {10: "octobre", 11: "novembre", 12: "decembre"}
MOIS_COURT = ["", "janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

FALQUE = {"nom": "CMA Falque", "rue": "36, rue Falque", "cp": "13006", "quartier": "Marseille 6e"}
BRIQ = {"nom": "La Briqueterie", "rue": "19, place Jean Jaurès", "cp": "13005", "quartier": "Marseille 5e"}

# Jeudis CMA Falque 14h–16h et mardis La Briqueterie 19h–21h (liens relevés sur le site actuel)
JEUDIS_LIENS = {
    date(2026, 10, 1): H + "/evenements/ateliers-d-ecriture-creative-jeudi-apres-midi-2",
    date(2026, 10, 15): H + "/evenements/atelier-d-ecriture-creative-jeudi-15-octobre-de-14h-a-16h-2",
}
JEUDIS = [date(2026, 10, 1), date(2026, 10, 15), date(2026, 11, 5), date(2026, 11, 19), date(2026, 12, 3), date(2026, 12, 17),
          date(2027, 1, 7), date(2027, 1, 21), date(2027, 2, 4), date(2027, 2, 18), date(2027, 3, 18),
          date(2027, 4, 1), date(2027, 4, 15), date(2027, 5, 6), date(2027, 5, 20), date(2027, 6, 3), date(2027, 6, 17)]
MARDIS = [date(2026, 10, 6), date(2026, 10, 20), date(2026, 11, 3), date(2026, 11, 17), date(2026, 12, 8), date(2026, 12, 15)]


def lien_jeudi(d):
    if d in JEUDIS_LIENS:
        return JEUDIS_LIENS[d]
    if d.year == 2026:
        return f"{H}/evenements/atelier-d-ecriture-creative-jeudi-{d.day}-{MOIS_SLUG[d.month]}-de-14h-a-16h"
    return H  # pas encore de billetterie dédiée


def lien_mardi(d):
    s = f"{H}/evenements/atelier-d-ecriture-creative-mardi-{d.day}-{MOIS_SLUG[d.month]}-de-19h-a-21h"
    return s + "-2" if d == date(2026, 12, 15) else s


def ateliers():
    a = [dict(d=d, lieu=FALQUE, debut="14:00", fin="16:00", h="14h – 16h", lien=lien_jeudi(d), titre="Atelier du jeudi après-midi") for d in JEUDIS]
    a += [dict(d=d, lieu=BRIQ, debut="19:00", fin="21:00", h="19h – 21h", lien=lien_mardi(d), titre="Atelier du mardi soir") for d in MARDIS]
    return sorted(a, key=lambda x: x["d"])


def tz(d):  # heure d'été : 29/03/2026–25/10/2026 et 28/03/2027–31/10/2027
    ete = date(2026, 3, 29) <= d < date(2026, 10, 25) or date(2027, 3, 28) <= d < date(2027, 10, 31)
    return "+02:00" if ete else "+01:00"


ORGA = {
    "@context": "https://schema.org", "@type": "EducationalOrganization", "@id": SITE + "/#organisation",
    "name": "Le Laboratoire des Mots", "url": SITE + "/", "logo": SITE + "/assets/img/logo.png",
    "description": "Association marseillaise d'ateliers d'écriture créative, de journées d'écriture et d'accompagnement au récit de vie.",
    "email": MAIL, "telephone": TEL_LIEN,
    "address": {"@type": "PostalAddress", "addressLocality": "Marseille", "addressRegion": "Provence-Alpes-Côte d'Azur", "addressCountry": "FR"},
    "areaServed": "Marseille", "founder": [{"@type": "Person", "name": "Cécilia Tarek Strano"}, {"@type": "Person", "name": "Marie-Paule Tooms"}],
    "sameAs": [INSTA, "https://www.wattpad.com/user/Cecilia_tarek", H],
}


def event_ld(a):
    d, l = a["d"], a["lieu"]
    return {
        "@context": "https://schema.org", "@type": "Event",
        "name": f"Atelier d'écriture créative – {a['titre'].lower().replace('atelier du ', '')} ({l['nom']})",
        "startDate": f"{d.isoformat()}T{a['debut']}{tz(d)}", "endDate": f"{d.isoformat()}T{a['fin']}{tz(d)}",
        "eventStatus": "https://schema.org/EventScheduled", "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {"@type": "Place", "name": l["nom"], "address": {"@type": "PostalAddress", "streetAddress": l["rue"], "postalCode": l["cp"], "addressLocality": "Marseille", "addressCountry": "FR"}},
        "image": [SITE + "/assets/img/og.webp"],
        "description": "Deux heures pour écrire, explorer l'imaginaire et partager ses textes dans un cadre bienveillant. Aucun prérequis.",
        "offers": {"@type": "Offer", "price": "20", "priceCurrency": "EUR", "url": a["lien"], "availability": "https://schema.org/InStock", "validFrom": "2026-09-01"},
        "organizer": {"@id": SITE + "/#organisation"}, "performer": {"@type": "Person", "name": "Cécilia Tarek Strano"},
    }


def faq_ld(qr):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in qr]}


def faq_html(qr):
    return '<div class="faq">' + "".join(f"<details><summary>{html.escape(q)}</summary><div><p>{html.escape(r)}</p></div></details>" for q, r in qr) + "</div>"


NAV = [("ateliers.html", "Ateliers"), ("ateliers-mensuels.html", "Ateliers mensuels"), ("journees.html", "Journées"),
       ("biographie.html", "Récit de vie"), ("institutions.html", "Institutions"), ("animatrices.html", "Les animatrices"),
       ("agenda.html", "Agenda"), ("contact.html", "Contact")]


def nav_items(courant):
    cur = ' aria-current="page"'
    return "".join(f'<li><a href="{h}"{cur if h == courant else ""}>{t}</a></li>' for h, t in NAV)


def head(fichier, titre, desc, ld=(), index=True, image="og.webp"):
    canon = SITE + "/" + ("" if fichier == "index.html" else fichier)
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in (ORGA, *ld))
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{'index, follow' if index else 'noindex, follow'}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Le Laboratoire des Mots">
<meta property="og:title" content="{titre}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/img/{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#8E2C6E">
<link rel="icon" href="assets/img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Allura&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Montserrat:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/css/style.css">
{lds}</head>
<body>
"""


def entete(courant=""):
    return f"""<a class="sr-only" href="#contenu">Aller au contenu</a>
<header class="entete">
  <div class="conteneur">
    <a class="logo" href="index.html" aria-label="Le Laboratoire des Mots – accueil">
      <span><b>Le laboratoire</b><small>des mots</small></span>
    </a>
    <nav class="nav" aria-label="Navigation principale"><ul>{nav_items(courant)}</ul></nav>
    <details class="nav-mobile"><summary>Menu</summary><nav aria-label="Navigation mobile"><ul>{nav_items(courant)}</ul></nav></details>
  </div>
</header>
<main id="contenu">
"""


NEWSLETTER = """<section class="section" aria-labelledby="titre-newsletter">
  <div class="conteneur">
    <div class="newsletter">
      <div>
        <span class="surtitre" style="color:#F2B8DC">La lettre du labo ✨</span>
        <h2 id="titre-newsletter">Recevez les prochaines dates en avant-première</h2>
        <p>Une lettre par mois, pas plus : les nouveaux ateliers, les journées d'écriture, une proposition d'écriture à tester chez vous.</p>
      </div>
      <form action="MAILCHIMP_ACTION_URL" method="post" target="_blank">
        <label class="sr-only" for="nl-email">Votre adresse e-mail</label>
        <div class="champ">
          <input id="nl-email" type="email" name="EMAIL" placeholder="votre@email.fr" autocomplete="email" required>
          <button class="btn" type="submit">Je m'inscris</button>
        </div>
        <label class="consentement"><input type="checkbox" name="gdpr_consent" value="Y" required> J'accepte de recevoir la lettre du Laboratoire des Mots. Désinscription en un clic à tout moment.</label>
        <div class="piege" aria-hidden="true"><input type="text" name="b_MAILCHIMP_HONEYPOT" tabindex="-1" value=""></div>
      </form>
    </div>
  </div>
</section>
"""

PIED = f"""</main>
<footer class="pied">
  <div class="conteneur">
    <a class="logo" href="index.html"><span><b>Le laboratoire</b><small>des mots</small></span></a>
    <div class="grille">
      <div><h2>L'association</h2><p>Ateliers d'écriture créative à Marseille. Écrire, transmettre, créer — sans prérequis, avec bienveillance.</p></div>
      <div><h2>Écrire avec nous</h2><ul>
        <li><a href="ateliers-mensuels.html">Ateliers mensuels</a></li><li><a href="journees.html">Journées d'écriture</a></li>
        <li><a href="biographie.html">Biographie &amp; récit de vie</a></li><li><a href="institutions.html">Institutions</a></li>
        <li><a href="agenda.html">Agenda</a></li></ul></div>
      <div><h2>Contact</h2><ul>
        <li><a href="mailto:{MAIL}">{MAIL}</a></li><li><a href="tel:{TEL_LIEN}">{TEL}</a></li>
        <li><a href="{INSTA}" rel="noopener">Instagram @cecilia_tarek</a></li>
        <li><a href="{H}" rel="noopener">Billetterie HelloAsso</a></li></ul></div>
      <div><h2>Adhérer</h2><p>L'adhésion annuelle (15 €) soutient l'association et ouvre le tarif réduit.</p><a class="btn btn--petit" href="{HA_ADHESION}" rel="noopener">J'adhère</a></div>
    </div>
    <div class="bas"><span>© {date.today().year} Le Laboratoire des Mots · Association loi 1901 · Marseille</span>
      <span><a href="mentions-legales.html">Mentions légales</a> · <a href="credits.html">Crédits photos</a></span></div>
  </div>
</footer>
</body>
</html>
"""


def ariane(titre, fichier):
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": titre, "item": f"{SITE}/{fichier}"}]}
    return f'<nav class="ariane" aria-label="Fil d\'Ariane"><ol><li><a href="index.html">Accueil</a></li><li aria-current="page">{titre}</li></ol></nav>', ld


def bandeau(fichier, court, surtitre, h1, chapo, img=None, alt="", actions=""):
    nav, ld = ariane(court, fichier)
    if img:
        return f"""<section class="bandeau bandeau--image"><img src="assets/img/{img}" alt="{alt}" width="1600" height="1067" fetchpriority="high">
  <div class="conteneur apparition">{nav}<span class="surtitre">{surtitre}</span><h1>{h1}</h1><p class="chapo">{chapo}</p>{actions}</div></section>
""", ld
    return f"""<section class="bandeau"><div class="conteneur apparition">{nav}<span class="surtitre">{surtitre}</span><h1>{h1}</h1><p class="chapo">{chapo}</p>{actions}</div></section>
""", ld


def date_li(a, titre_lieu=True):
    d = a["d"]
    lieu = f"{a['lieu']['nom']}, {a['lieu']['rue']}, {a['lieu']['quartier']}"
    libelle = "Réserver" if a["lien"] != H else "Billetterie"
    return f"""<li class="date"><time datetime="{d.isoformat()}T{a['debut']}"><b>{d.day}</b><small>{MOIS_COURT[d.month]}</small></time>
  <div><strong>{JOURS[d.weekday()].capitalize()} {d.day} {MOIS[d.month]} {d.year} · {a['h']}</strong><span>{a['titre']} — {lieu}</span></div>
  <a class="btn btn--petit" href="{a['lien']}" rel="noopener" aria-label="{libelle} : {a['titre']} du {d.day} {MOIS[d.month]}">{libelle}</a></li>
"""


TARIFS = f"""<table class="tarifs"><caption class="sr-only">Tarifs des ateliers mensuels</caption>
<thead><tr><th scope="col">Formule</th><th scope="col">Tarif</th></tr></thead><tbody>
<tr><td>Un atelier (non-adhérent)</td><td>20 €</td></tr>
<tr><td>Un atelier (adhérent)</td><td>17 €</td></tr>
<tr><td>Forfait trimestre jeudi — 6 ateliers</td><td>100 €</td></tr>
<tr><td>Forfait année jeudi — 18 ateliers</td><td>290 €</td></tr>
<tr><td>Adhésion annuelle à l'association</td><td>15 €</td></tr>
</tbody></table>
<div class="actions"><a class="btn" href="{HA_FORFAIT}" rel="noopener">Forfait trimestre ou année</a><a class="btn btn--contour" href="{HA_ADHESION}" rel="noopener">J'adhère (15 €)</a></div>
"""

FAQ_GENERALE = [
    ("Faut-il savoir bien écrire pour participer ?", "Non. Les ateliers sont ouverts à toutes et à tous, sans aucun prérequis littéraire. On vient pour jouer avec les mots, pas pour être noté."),
    ("Que dois-je apporter ?", "Un carnet et un stylo suffisent. Les propositions d'écriture, les textes d'inspiration et la bonne humeur sont fournis."),
    ("Suis-je obligé·e de lire mon texte ?", "Jamais. La lecture à voix haute est une invitation : chacun·e choisit de partager ou de garder son texte pour soi."),
    ("Comment réserver ?", "Chaque atelier se réserve en ligne sur HelloAsso, à l'unité ou au forfait. Le paiement est sécurisé et vous recevez une confirmation par e-mail."),
    ("À quoi sert l'adhésion ?", "L'adhésion annuelle (15 €) soutient l'association et vous donne accès au tarif réduit : 17 € l'atelier au lieu de 20 €."),
    ("Puis-je offrir un atelier ?", "Oui ! Un atelier, un forfait ou un accompagnement biographique font de très beaux cadeaux. Écrivez-nous pour préparer une carte cadeau."),
]

PAGES = {}

# ---------- Ateliers (hub) ----------
b, bl = bandeau("ateliers.html", "Ateliers", "Ateliers d'écriture créative à Marseille", 'Nos ateliers <span class="script">&amp; journées d\'écriture</span>',
                "Animer, c'est donner de l'âme : c'est ce que signifie <em>animare</em> en latin. C'est aussi ce qui guide chacun de nos ateliers.",
                "ecriture-main.webp", "Mains qui écrivent dans un carnet")
PAGES["ateliers.html"] = dict(titre="Ateliers d'écriture créative à Marseille | Labo des Mots",
    desc="Ateliers d'écriture créative à Marseille : jeudis au CMA Falque, mardis à la Briqueterie, journées d'écriture le samedi. Ouverts à tous, sans prérequis.",
    ld=[bl, faq_ld(FAQ_GENERALE)], corps=b + f"""
<section class="section"><div class="conteneur">
  <div class="centre"><span class="surtitre">Trois rendez-vous</span><h2>Choisissez <span class="script">votre rythme</span></h2>
  <p class="chapo">Un après-midi en journée, une soirée après le travail ou une journée entière pour s'évader : il y a forcément une formule pour votre plume.</p></div>
  <div class="grille grille--3" style="margin-top:40px">
    <article class="carte"><img src="assets/img/cafe-ecriture.webp" alt="Carnet ligné et tasse de café sur une table en bois" width="800" height="800" loading="lazy">
      <div class="carte__corps"><span class="etiquette">Deux jeudis par mois</span><h3>Le jeudi après-midi au CMA Falque</h3><p>De 14h à 16h, rue Falque (6e). Un rendez-vous régulier pour installer l'écriture dans sa vie.</p><a class="btn btn--petit fleche" href="ateliers-mensuels.html#jeudi">Voir les dates</a></div></article>
    <article class="carte"><img src="assets/img/ecriture-stylo-rouge.webp" alt="Main tenant un stylo rouge au-dessus d'un carnet" width="1600" height="1067" loading="lazy">
      <div class="carte__corps"><span class="etiquette">Deux mardis par mois</span><h3>Le mardi soir à la Briqueterie</h3><p>De 19h à 21h, place Jean Jaurès (5e). Deux heures pour déposer la journée et laisser venir les mots.</p><a class="btn btn--petit fleche" href="ateliers-mensuels.html#mardi">Voir les dates</a></div></article>
    <article class="carte"><img src="assets/img/atelier-illustration.webp" alt="Groupe de participants écrivant autour d'une grande table" width="1122" height="1402" loading="lazy">
      <div class="carte__corps"><span class="etiquette">Un samedi par trimestre</span><h3>Les journées d'écriture</h3><p>Une journée entière hors du quotidien, en petit groupe, pour explorer une histoire de bout en bout.</p><a class="btn btn--petit fleche" href="journees.html">Découvrir</a></div></article>
  </div>
</div></section>
<section class="section section--sable"><div class="conteneur">
  <div class="centre"><span class="surtitre">Comment ça se passe ?</span><h2>Un atelier <span class="script">en quatre temps</span></h2></div>
  <ol class="etapes" style="margin-top:36px">
    <li><h3>L'accueil</h3><p>On s'installe, un thé, quelques mots pour faire connaissance. Pas de pression.</p></li>
    <li><h3>La proposition</h3><p>Un texte, une image, une contrainte ludique : de quoi faire jaillir l'idée.</p></li>
    <li><h3>L'écriture</h3><p>Un temps rien qu'à vous, en silence, pour suivre le fil de votre plume.</p></li>
    <li><h3>Le partage</h3><p>Celles et ceux qui le souhaitent lisent ; les retours sont toujours bienveillants.</p></li>
  </ol>
</div></section>
<section class="section"><div class="conteneur grille grille--2">
  <div><span class="surtitre">Pour qui ?</span><h2>Pour toutes <span class="script">les plumes</span></h2>
    <ul class="puces"><li>Celles et ceux qui n'ont plus écrit depuis l'école</li><li>Les curieux qui ont envie d'essayer, juste pour voir</li><li>Les passionnés qui cherchent un cadre régulier et des retours</li><li>Toute personne qui a une histoire à raconter</li></ul>
    <p>Groupes de 10 personnes maximum, pour que chaque voix ait sa place.</p></div>
  <img class="image-arrondie" src="assets/img/rentree.webp" alt="Personne écrivant dans un carnet au milieu de fleurs orange" width="1024" height="1024" loading="lazy">
</div></section>
<section class="section section--rose"><div class="conteneur" style="max-width:820px">
  <div class="centre"><span class="surtitre">Questions fréquentes</span><h2>Vous vous demandez…</h2></div>{faq_html(FAQ_GENERALE)}
</div></section>
""")

# ---------- Ateliers mensuels ----------
tous = ateliers()
jeudis = [a for a in tous if a["lieu"] is FALQUE]
mardis = [a for a in tous if a["lieu"] is BRIQ]
b, bl = bandeau("ateliers-mensuels.html", "Ateliers mensuels", "CMA Falque (13006) · La Briqueterie (13005)", 'Les ateliers <span class="script">du mois</span>',
                "Un rendez-vous deux fois par mois pour débloquer sa plume, explorer l'imaginaire et partager ses récits.", "papier-ligne.webp", "Stylo-plume posé sur un carnet manuscrit",
                '<div class="actions"><a class="btn" href="#jeudi">Jeudi après-midi</a><a class="btn btn--contour" style="color:#fff;border-color:#fff" href="#mardi">Mardi soir</a></div>')
PAGES["ateliers-mensuels.html"] = dict(titre="Atelier d'écriture mensuel à Marseille – dates et tarifs",
    desc="Ateliers d'écriture créative deux fois par mois à Marseille : jeudi 14h–16h au CMA Falque, mardi 19h–21h à la Briqueterie. 20 €, réservation HelloAsso.",
    ld=[bl] + [event_ld(a) for a in tous], corps=b + f"""
<section class="section"><div class="conteneur grille grille--2">
  <div><span class="surtitre">L'esprit des ateliers</span><h2>Écrire, créer <span class="script">et oser</span></h2>
    <p>Animés par Cécilia Tarek Strano, poétesse et autrice, les ateliers reposent sur trois piliers : <strong>l'écoute, la bienveillance et l'expérimentation créative</strong>.</p>
    <p>Aucun prérequis littéraire : on y vient pour se surprendre, découvrir d'autres manières d'écrire et repartir avec des textes qu'on n'imaginait pas écrire.</p>
    <ul class="puces"><li>Un cadre chaleureux, des retours bienveillants</li><li>Des propositions variées : poésie, récit, souvenirs, imaginaire</li><li>Des petits groupes pour que chacun trouve sa place</li></ul></div>
  <img class="image-arrondie" src="assets/img/cecilia-tarek-strano.webp" alt="Portrait de Cécilia Tarek Strano, animatrice des ateliers" width="500" height="500" loading="lazy">
</div></section>
<section class="section section--sable" id="jeudi"><div class="conteneur grille grille--2" style="align-items:start">
  <div><span class="surtitre">Deux jeudis par mois · 14h – 16h</span><h2>Le jeudi <span class="script">après-midi</span></h2>
    <p><strong>CMA Falque</strong><br>36, rue Falque, 13006 Marseille</p>
    <p>Le forfait trimestre (6 ateliers, 100 €) ou année (18 ateliers, 290 €) vous garantit votre place à chaque séance.</p>
    <div class="actions"><a class="btn" href="{HA_FORFAIT}" rel="noopener">Je prends le forfait</a></div></div>
  <ul class="dates">{''.join(date_li(a) for a in jeudis)}</ul>
</div></section>
<section class="section" id="mardi"><div class="conteneur grille grille--2" style="align-items:start">
  <div><span class="surtitre">Deux mardis par mois · 19h – 21h</span><h2>Le mardi <span class="script">soir</span></h2>
    <p><strong>La Briqueterie</strong><br>19, place Jean Jaurès, 13005 Marseille — <a href="https://www.la-briqueterie.fr/" rel="noopener">découvrir le lieu</a></p>
    <p>Après le travail, deux heures pour soi au cœur de la Plaine.</p></div>
  <ul class="dates">{''.join(date_li(a) for a in mardis)}</ul>
</div></section>
<section class="section section--rose"><div class="conteneur" style="max-width:820px">
  <div class="centre"><span class="surtitre">Tarifs</span><h2>Simple <span class="script">et accessible</span></h2></div>{TARIFS}
  <p style="margin-top:1.4em;font-size:1rem">Une question avant de vous lancer ? Écrivez à <a href="mailto:lelaboratoiredesmots@gmail.com">lelaboratoiredesmots@gmail.com</a> ou appelez le <a href="tel:+33626755827">06 26 75 58 27</a>.</p>
</div></section>
""")

# ---------- Journées ----------
b, bl = bandeau("journees.html", "Journées & week-ends", "Un samedi par trimestre", 'Les journées <span class="script">d\'écriture</span>',
                "Prendre le temps d'écrire, d'explorer des histoires, d'expérimenter avec les mots et de partager un moment hors du quotidien.", "marseille-escaliers.webp", "Ruelle en escaliers bordée de façades ocre à Marseille",
                f'<div class="actions"><a class="btn" href="{H}" rel="noopener">Je m\'inscris sur HelloAsso</a></div>')
PAGES["journees.html"] = dict(titre="Journée d'écriture créative à Marseille | Labo des Mots",
    desc="Une journée entière d'écriture créative à Marseille, un samedi par trimestre : 8 participants maximum, deux ateliers, déjeuner partagé. Tous niveaux.",
    ld=[bl], corps=b + f"""
<section class="section"><div class="conteneur grille grille--2">
  <img class="image-arrondie" src="assets/img/atelier-illustration.webp" alt="Participants écrivant ensemble autour d'une table chaleureuse" width="1122" height="1402" loading="lazy">
  <div><span class="surtitre">Une parenthèse</span><h2>Une journée <span class="script">rien que pour écrire</span></h2>
    <p>Les journées d'écriture sont des parenthèses conviviales, accessibles à toutes et à tous, quel que soit votre rapport à l'écriture.</p>
    <p>Sur une journée, on a le temps d'aller plus loin : laisser mûrir une idée, la réécrire, l'emmener là où on ne l'attendait pas.</p>
    <div class="chiffres" style="margin:30px 0"><div><strong>8</strong><span>participants max.</span></div><div><strong>2</strong><span>ateliers</span></div><div><strong>1</strong><span>déjeuner partagé</span></div></div>
    <p>Lieu habituel : <strong>CMA Hopkinson</strong>, Marseille. Le lieu exact et les informations pratiques sont confirmés à l'inscription.</p></div>
</div></section>
<section class="section section--sable"><div class="conteneur">
  <div class="centre"><span class="surtitre">Le déroulé</span><h2>Une journée <span class="script">type</span></h2></div>
  <ol class="etapes" style="margin-top:36px">
    <li><h3>9h30 – 10h</h3><p>Accueil des participants, café et présentations.</p></li>
    <li><h3>10h – 12h30</h3><p>Premier atelier : on ouvre les portes de l'imaginaire.</p></li>
    <li><h3>12h30 – 14h</h3><p>Pause déjeuner, chacun apporte son repas (micro-ondes et vaisselle sur place).</p></li>
    <li><h3>14h – 16h30</h3><p>Second atelier : on approfondit, on réécrit, on partage.</p></li>
  </ol>
</div></section>
<section class="section"><div class="conteneur" style="max-width:820px">
  <div class="centre"><span class="surtitre">Tarifs</span><h2>Participer</h2></div>
  <table class="tarifs"><caption class="sr-only">Tarifs des journées d'écriture</caption><thead><tr><th scope="col">Formule</th><th scope="col">Tarif</th></tr></thead>
  <tbody><tr><td>Journée d'écriture</td><td>50 €</td></tr><tr><td>Tarif réduit</td><td>40 €</td></tr></tbody></table>
  <div class="actions"><a class="btn" href="{H}" rel="noopener">Voir les prochaines journées</a><a class="btn btn--contour" href="mailto:mptooms@orange.fr">Écrire à Marie-Paule</a></div>
  <p style="margin-top:1.4em;font-size:1rem">Les dates des journées sont annoncées en priorité dans la lettre du labo — inscrivez-vous ci-dessous pour ne pas les manquer.</p>
</div></section>
""")

# ---------- Biographie ----------
FAQ_BIO = [
    ("Combien de temps faut-il ?", "Il faut compter entre 6 et 10 heures d'entretien, réparties en plusieurs rencontres, selon la richesse de votre parcours et ce que vous souhaitez transmettre."),
    ("Mes confidences restent-elles privées ?", "Oui. Tout ce qui est dit pendant les entretiens reste confidentiel. Vous relisez le texte et décidez de ce qui y figure."),
    ("Est-ce que je dois savoir écrire ?", "Pas du tout : vous racontez, l'animatrice écoute et met votre histoire en mots, avec votre voix."),
    ("Pour qui écrire une biographie ?", "Pour soi, pour ses enfants et petits-enfants, pour garder la mémoire d'un parent : un récit de vie est un cadeau qui traverse les générations."),
    ("Combien cela coûte-t-il ?", "Chaque projet est différent. Contactez-nous pour un premier échange gratuit et un devis adapté."),
]
b, bl = bandeau("biographie.html", "Biographie & récit de vie", "Accompagnement personnalisé", 'Votre histoire <span class="script">mérite d\'être écrite</span>',
                "Vous racontez, nous écoutons, et votre vie devient un livre à transmettre.", "the-livre.webp", "Tasse de thé posée sur un livre ouvert",
                f'<div class="actions"><a class="btn" href="contact.html">Premier échange gratuit</a></div>')
PAGES["biographie.html"] = dict(titre="Écrire sa biographie à Marseille – récit de vie accompagné",
    desc="Faites écrire votre biographie ou votre récit de vie à Marseille : entretiens bienveillants (6 à 10 h), texte fidèle à votre voix, à transmettre à vos proches.",
    ld=[bl, faq_ld(FAQ_BIO)], corps=b + f"""
<section class="section"><div class="conteneur grille grille--2">
  <div><span class="surtitre">En quelques mots</span><h2>Une biographie, <span class="script">à deux voix</span></h2>
    <p>Le Laboratoire des Mots vous propose d'écrire votre biographie ou votre récit de vie. Au fil de rencontres chaleureuses, l'animatrice écoute votre histoire puis la transpose en texte, en restant fidèle à vos mots et à votre façon de dire.</p>
    <p>Ces accompagnements sont réalisés par <strong>Cécilia Tarek</strong>, poétesse et biographe, qui intervient aussi auprès de personnes âgées en EHPAD.</p></div>
  <img class="image-arrondie" src="assets/img/biographie-1.webp" alt="Illustration d'une personne âgée racontant ses souvenirs" width="683" height="1024" loading="lazy" style="max-height:560px">
</div></section>
<section class="section section--sable"><div class="conteneur">
  <div class="centre"><span class="surtitre">Fonctionnement</span><h2>De la parole <span class="script">au livre</span></h2></div>
  <ol class="etapes" style="margin-top:36px">
    <li><h3>La rencontre</h3><p>Un premier échange gratuit pour faire connaissance et définir votre projet.</p></li>
    <li><h3>Les entretiens</h3><p>Entre 6 et 10 heures de conversation, à votre rythme, pour dérouler le fil de votre vie.</p></li>
    <li><h3>L'écriture</h3><p>L'animatrice met votre récit en forme, chapitre après chapitre.</p></li>
    <li><h3>La relecture</h3><p>Vous relisez, corrigez, ajoutez : le texte final vous ressemble.</p></li>
  </ol>
</div></section>
<section class="section"><div class="conteneur grille grille--2">
  <img class="image-arrondie" src="assets/img/biographie-2.webp" alt="Illustration d'une conversation chaleureuse autour d'une table" width="1448" height="1086" loading="lazy">
  <div><span class="surtitre">Une idée cadeau</span><h2>Offrir <span class="script">un récit de vie</span></h2>
    <p>Pour un anniversaire, une retraite, une naissance dans la famille : offrir l'écriture de sa vie à un parent ou un grand-parent, c'est offrir du temps, de l'écoute, et un héritage pour toute la famille.</p>
    <div class="actions"><a class="btn" href="contact.html">Préparer un cadeau</a></div></div>
</div></section>
<section class="section section--rose"><div class="conteneur" style="max-width:820px">
  <div class="centre"><span class="surtitre">FAQ</span><h2>Vos questions</h2></div>{faq_html(FAQ_BIO)}
</div></section>
""")

# ---------- Institutions ----------
b, bl = bandeau("institutions.html", "Institutions", "Résidences seniors, associations, entreprises", 'Des ateliers <span class="script">chez vous</span>',
                "Nous animons des ateliers d'écriture créative dans les institutions et les lieux associatifs : un espace de confiance où chacun retrouve sa voix.", "bibliotheque.webp", "Rayonnages de vieux livres reliés",
                '<div class="actions"><a class="btn" href="contact.html">Monter un projet</a></div>')
PAGES["institutions.html"] = dict(titre="Ateliers d'écriture pour institutions, EHPAD et associations",
    desc="Ateliers d'écriture créative pour résidences seniors, EHPAD, associations et entreprises à Marseille : petits groupes, lien social, confiance en soi.",
    ld=[bl], corps=b + """
<section class="section"><div class="conteneur grille grille--2">
  <div><span class="surtitre">Ils nous font confiance</span><h2>Un espace <span class="script">de confiance</span></h2>
    <p>Le Laboratoire des Mots intervient notamment dans des <strong>résidences pour seniors</strong> et auprès de la <strong>Ligue contre le cancer</strong>. L'écriture y devient un moment de lien, de mémoire et de fierté.</p>
    <p>Chaque projet est construit avec vous : nombre de séances, thèmes, publics, restitution finale (lecture, recueil, exposition…).</p></div>
  <img class="image-arrondie" src="assets/img/carnet-femme.webp" alt="Personne écrivant dans un carnet posé sur ses genoux" width="1067" height="1600" loading="lazy" style="max-height:560px">
</div></section>
<section class="section section--sable"><div class="conteneur">
  <div class="centre"><span class="surtitre">Notre approche</span><h2>Cinq <span class="script">engagements</span></h2></div>
  <div class="grille grille--3" style="margin-top:36px">
    <div class="carte"><div class="carte__corps"><h3>✦ Des groupes à taille humaine</h3><p>10 personnes maximum, pour que chacun soit écouté.</p></div></div>
    <div class="carte"><div class="carte__corps"><h3>✦ Du lien social</h3><p>Écrire ensemble crée des rencontres et des complicités.</p></div></div>
    <div class="carte"><div class="carte__corps"><h3>✦ La confiance en soi</h3><p>Oser écrire, oser lire : chaque texte est une petite victoire.</p></div></div>
    <div class="carte"><div class="carte__corps"><h3>✦ L'écoute active</h3><p>On apprend à recevoir les mots des autres avec attention.</p></div></div>
    <div class="carte"><div class="carte__corps"><h3>✦ Des thèmes variés</h3><p>Souvenirs, imaginaire, poésie : des propositions adaptées à chaque public, dans le respect de tous.</p></div></div>
  </div>
</div></section>
<section class="section"><div class="conteneur centre"><span class="surtitre">Parlons-en</span>
  <h2>Votre structure souhaite <span class="script">proposer des ateliers ?</span></h2>
  <p class="chapo">Contactez-nous pour construire ensemble votre projet d'ateliers d'écriture créative.</p>
  <div class="actions" style="justify-content:center"><a class="btn" href="contact.html">Nous contacter</a><a class="btn btn--contour" href="tel:+33647008470">06 47 00 84 70</a></div>
</div></section>
""")

# ---------- Animatrices ----------
PERSONNES = [
    {"@context": "https://schema.org", "@type": "Person", "name": "Cécilia Tarek Strano", "jobTitle": "Poétesse, autrice, biographe et animatrice d'ateliers d'écriture",
     "image": SITE + "/assets/img/cecilia-tarek-strano.webp", "worksFor": {"@id": SITE + "/#organisation"},
     "sameAs": [INSTA, "https://www.wattpad.com/user/Cecilia_tarek", "https://poesie.io/cecilia-tarek/au-seuil-des-reves"]},
    {"@context": "https://schema.org", "@type": "Person", "name": "Marie-Paule Tooms", "jobTitle": "Animatrice d'ateliers d'écriture",
     "image": SITE + "/assets/img/marie-paule-tooms.webp", "worksFor": {"@id": SITE + "/#organisation"}},
]
b, bl = bandeau("animatrices.html", "Les animatrices", "Qui sommes-nous ?", 'Deux plumes, <span class="script">une même passion</span>',
                "Le Laboratoire des Mots est né de la rencontre de Cécilia Tarek et Marie-Paule Tooms, convaincues que les mots sont des ponts : entre soi et soi-même, entre soi et les autres, entre soi et le monde.")
PAGES["animatrices.html"] = dict(titre="Cécilia Tarek et Marie-Paule Tooms, animatrices",
    desc="Rencontrez Cécilia Tarek Strano, poétesse et autrice, et Marie-Paule Tooms, diplômée en animation d'ateliers d'écriture, fondatrices du Laboratoire des Mots.",
    ld=[bl] + PERSONNES, corps=b + f"""
<section class="section section--blanc"><div class="conteneur grille grille--2">
  <img class="image-arrondie" src="assets/img/cecilia-tarek-strano.webp" alt="Portrait de Cécilia Tarek Strano" width="500" height="500" loading="lazy" style="max-width:440px;justify-self:center">
  <div><span class="surtitre">Poétesse · Autrice · Biographe</span><h2>Cécilia <span class="script">Tarek Strano</span></h2>
    <p>Poétesse et autrice depuis des années, Cécilia a publié <em>L'Odyssée d'une âme</em> (2016) et <em>Au seuil des rêves</em> (2024). Elle anime des espaces d'écriture fondés sur la bienveillance, l'écoute et la créativité, et intervient auprès des personnes âgées en EHPAD.</p>
    <p>C'est elle qui anime les ateliers mensuels du jeudi et du mardi, et qui accompagne les projets de biographie.</p>
    <div class="actions"><a class="btn btn--petit" href="{INSTA}" rel="noopener">Instagram</a><a class="btn btn--petit btn--contour" href="https://www.wattpad.com/user/Cecilia_tarek" rel="noopener">Wattpad</a><a class="btn btn--petit btn--contour" href="https://poesie.io/cecilia-tarek/au-seuil-des-reves" rel="noopener">Au seuil des rêves</a></div></div>
</div></section>
<section class="section"><div class="conteneur grille grille--2">
  <div><span class="surtitre">Animatrice diplômée</span><h2>Marie-Paule <span class="script">Tooms</span></h2>
    <p class="citation" style="text-align:left;margin:0 0 1em;font-size:1.6rem">« De la lecture à l'écriture, il n'y a qu'un pas… »</p>
    <p>Diplômée en animation d'ateliers d'écriture en 2020, Marie-Paule anime depuis 2019 des ateliers créatifs sans prérequis, en présentiel comme en visio. Elle organise notamment les journées d'écriture du samedi.</p>
    <div class="actions"><a class="btn btn--petit" href="journees.html">Ses journées d'écriture</a></div></div>
  <img class="image-arrondie" src="assets/img/marie-paule-tooms.webp" alt="Portrait de Marie-Paule Tooms" width="684" height="730" loading="lazy" style="max-width:440px;justify-self:center">
</div></section>
<section class="section section--encre"><div class="conteneur">
  <blockquote class="citation">Les mots deviennent des ponts : entre soi et soi-même, entre soi et les autres, entre soi et le monde.<footer>Le Laboratoire des Mots</footer></blockquote>
</div></section>
""")

# ---------- Agenda ----------
b, bl = bandeau("agenda.html", "Agenda", "Saison 2026 – 2027", 'L\'agenda <span class="script">des ateliers</span>',
                "Toutes les prochaines dates en un coup d'œil. Choisissez la vôtre et réservez en ligne en deux minutes.")
a_venir = [a for a in tous if a["d"] >= date.today()]
par_mois = {}
for a in a_venir:
    par_mois.setdefault((a["d"].year, a["d"].month), []).append(a)
blocs = "".join(f'<h2 style="margin-top:1.6em">{MOIS[m].capitalize()} <span class="script">{y}</span></h2><ul class="dates">{"".join(date_li(a) for a in l)}</ul>' for (y, m), l in par_mois.items())
PAGES["agenda.html"] = dict(titre="Agenda des ateliers d'écriture à Marseille | Labo des Mots",
    desc="Toutes les dates des ateliers d'écriture créative à Marseille : jeudis au CMA Falque, mardis à la Briqueterie, journées du samedi. Réservation HelloAsso.",
    ld=[bl] + [event_ld(a) for a in a_venir], corps=b + f"""
<section class="section" style="padding-top:20px"><div class="conteneur" style="max-width:860px">
  <p>Légende : <span class="etiquette">Jeudi 14h – 16h · CMA Falque</span> <span class="etiquette">Mardi 19h – 21h · La Briqueterie</span></p>
  {blocs}
  <div class="carte" style="margin-top:40px"><div class="carte__corps"><span class="etiquette">Un samedi par trimestre</span><h3>Journées d'écriture</h3><p>Les dates sont publiées sur HelloAsso et annoncées dans la lettre du labo.</p><a class="btn btn--petit fleche" href="journees.html">En savoir plus</a></div></div>
</div></section>
""")

# ---------- Contact ----------
b, bl = bandeau("contact.html", "Contact", "Écrivez-nous", 'Parlons <span class="script">de vos mots</span>',
                "Une question sur un atelier, un projet de biographie, une intervention dans votre structure ? Nous vous répondons avec plaisir.")
PAGES["contact.html"] = dict(titre="Contact – Le Laboratoire des Mots, Marseille",
    desc="Contactez Le Laboratoire des Mots, association d'ateliers d'écriture créative à Marseille : lelabodesmots@outlook.fr ou 06 47 00 84 70.",
    ld=[bl], corps=b + f"""
<section class="section" style="padding-top:20px"><div class="conteneur grille grille--3">
  <div class="carte"><div class="carte__corps"><span class="etiquette">Par e-mail</span><h3>L'association</h3><p><a href="mailto:{MAIL}">{MAIL}</a></p><a class="btn btn--petit" href="mailto:{MAIL}?subject=Demande%20d'information">Écrire un e-mail</a></div></div>
  <div class="carte"><div class="carte__corps"><span class="etiquette">Par téléphone</span><h3>Nous appeler</h3><p><a href="tel:{TEL_LIEN}">{TEL}</a><br><a href="tel:+33626755827">06 26 75 58 27</a> (ateliers mensuels)</p><a class="btn btn--petit" href="tel:{TEL_LIEN}">Appeler</a></div></div>
  <div class="carte"><div class="carte__corps"><span class="etiquette">Journées d'écriture</span><h3>Marie-Paule Tooms</h3><p><a href="mailto:mptooms@orange.fr">mptooms@orange.fr</a></p><a class="btn btn--petit" href="mailto:mptooms@orange.fr">Lui écrire</a></div></div>
</div>
<div class="conteneur centre" style="margin-top:60px"><span class="surtitre">Suivre le labo</span><h2>Sur <span class="script">Instagram</span></h2>
  <p class="chapo">Coulisses des ateliers, poèmes, inspirations : retrouvez Cécilia sur <a href="{INSTA}" rel="noopener">@cecilia_tarek</a>.</p></div>
</section>
""")

# ---------- Pages légales / utilitaires ----------
credits_li = "".join(f"<li>{n.replace('-', ' ').capitalize()} — photo de {a} sur <a href=\"https://unsplash.com/photos/{i.replace('photo-', '')}\" rel=\"noopener\">Unsplash</a></li>"
                     for n, i, a in (l.split("|") for l in (ROOT / "_gen/unsplash.txt").read_text(encoding="utf-8").split("\n") if l.strip()))
PAGES["credits.html"] = dict(titre="Crédits photos | Le Laboratoire des Mots", desc="Crédits des photographies utilisées sur le site du Laboratoire des Mots.", index=False,
    corps=f'<section class="section"><div class="conteneur" style="max-width:820px"><h1>Crédits <span class="script">photos</span></h1><p>Portraits, logo et illustrations : © Le Laboratoire des Mots. Photographies libres de droits (licence Unsplash) :</p><ul class="puces">{credits_li}</ul></div></section>')
PAGES["mentions-legales.html"] = dict(titre="Mentions légales | Le Laboratoire des Mots", desc="Mentions légales du site du Laboratoire des Mots, association loi 1901 à Marseille.", index=False,
    corps=f"""<section class="section"><div class="conteneur" style="max-width:820px"><h1>Mentions <span class="script">légales</span></h1>
<h2>Éditeur</h2><p>Le Laboratoire des Mots, association loi 1901, Marseille.<br>Contact : <a href="mailto:{MAIL}">{MAIL}</a> · {TEL}<br>Directrices de la publication : Cécilia Tarek Strano et Marie-Paule Tooms.</p>
<h2>Hébergement</h2><p><!-- à compléter : nom, adresse et téléphone de l'hébergeur -->Informations sur l'hébergeur à compléter.</p>
<h2>Données personnelles</h2><p>L'adresse e-mail saisie dans le formulaire de la lettre d'information est transmise à Mailchimp et utilisée uniquement pour l'envoi de cette lettre. Chaque envoi contient un lien de désinscription. Vous pouvez demander l'accès ou la suppression de vos données en écrivant à {MAIL}.</p>
<h2>Paiements</h2><p>Les réservations et adhésions sont traitées par HelloAsso ; le site ne collecte aucune donnée bancaire.</p></div></section>""")
PAGES["404.html"] = dict(titre="Page introuvable | Le Laboratoire des Mots", desc="Cette page n'existe pas ou plus.", index=False,
    corps='<section class="section centre"><div class="conteneur"><span class="surtitre">Erreur 404</span><h1>Cette page <span class="script">s\'est envolée</span></h1><p class="chapo">Comme un mot sur le bout de la langue… Elle n\'existe pas ou plus.</p><div class="actions" style="justify-content:center"><a class="btn" href="index.html">Retour à l\'accueil</a><a class="btn btn--contour" href="agenda.html">Voir l\'agenda</a></div></div></section>')

for fichier, p in PAGES.items():
    newsletter = "" if fichier in ("credits.html", "mentions-legales.html", "404.html") else NEWSLETTER
    (ROOT / fichier).write_text(head(fichier, p["titre"], p["desc"], p.get("ld", []), p.get("index", True)) + entete(fichier) + p["corps"] + newsletter + PIED, encoding="utf-8")
    print(fichier, len(p["titre"]), len(p["desc"]))

# Fragments réutilisables par les landings
(ROOT / "_gen/fragments").mkdir(exist_ok=True)
(ROOT / "_gen/fragments/entete.html").write_text(entete(), encoding="utf-8")
(ROOT / "_gen/fragments/newsletter.html").write_text(NEWSLETTER, encoding="utf-8")
(ROOT / "_gen/fragments/pied.html").write_text(PIED, encoding="utf-8")
(ROOT / "_gen/fragments/head-landing.html").write_text(head("index.html", "Atelier d'écriture à Marseille – Le Laboratoire des Mots",
    "Ateliers d'écriture créative à Marseille, journées d'écriture et biographies. Ouverts à tous, sans prérequis. Réservez votre prochain atelier.",
    [event_ld(a) for a in a_venir[:6]], index=False), encoding="utf-8")
(ROOT / "_gen/fragments/dates-prochaines.html").write_text('<ul class="dates">' + "".join(date_li(a) for a in a_venir[:6]) + "</ul>", encoding="utf-8")

pages_sitemap = ["index.html"] + [f for f in PAGES if f not in ("404.html", "credits.html", "mentions-legales.html")]
(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{SITE}/{'' if f == 'index.html' else f}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n" for f in pages_sitemap) + "</urlset>\n", encoding="utf-8")
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /_gen/\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

# ---------- Sélecteur des 3 propositions (temporaire, remplacé par la landing retenue) ----------
PROPS = [("landing-1.html", "Carnet d'écriture", "Éditorial et raffiné, comme une page de carnet.", "papier-ligne.webp"),
         ("landing-3.html", "Agenda d'abord", "Orientée réservation : prochaine date, formules, tarifs.", "cafe-ecriture.webp"),
         ("landing-5.html", "Nuit poétique", "Immersive et littéraire, sur fond d'encre.", "livre-mug.webp")]
cartes = "".join(f'<article class="carte"><img src="assets/img/{img}" alt="" width="1600" height="1067" loading="lazy"><div class="carte__corps"><span class="etiquette">Proposition {f[8]}</span><h2 style="font-size:1.2rem">{t}</h2><p>{d}</p><a class="btn btn--petit fleche" href="{f}">Voir la proposition</a></div></article>'
                 for f, t, d, img in PROPS)
(ROOT / "index.html").write_text(head("index.html", "Le Laboratoire des Mots – 3 propositions d'accueil", "Choix de la future page d'accueil du Laboratoire des Mots.", index=False) + entete() +
    f'<section class="section"><div class="conteneur"><div class="centre"><span class="surtitre">Refonte du site</span><h1>Trois propositions <span class="script">d\'accueil</span></h1><p class="chapo">Toutes partagent les mêmes pages internes, la newsletter et les liens HelloAsso. Choisissez celle qui deviendra la page d\'accueil.</p></div><div class="grille grille--3" style="margin-top:40px">{cartes}</div></div></section>' + PIED, encoding="utf-8")
