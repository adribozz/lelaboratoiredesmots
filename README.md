# Le Laboratoire des Mots — site statique

HTML/CSS sans build, servi par nginx (Docker) sur Coolify.

- Pages internes, `sitemap.xml`, `robots.txt` et sélecteur `index.html` : générés par `python _gen/gen.py` (dates, liens HelloAsso et textes sont dans ce fichier).
- Propositions d'accueil : `landing-1.html`, `landing-3.html`, `landing-5.html` (éditées à la main, `noindex`).
- Contrôle SEO / liens : `python _gen/check.py`.
- Newsletter : remplacer `MAILCHIMP_ACTION_URL` (et `b_MAILCHIMP_HONEYPOT`) par les valeurs du formulaire intégré Mailchimp.

## Déploiement Coolify
Application → ce dépôt, branche `main` → Build Pack **Dockerfile** → port **80** → domaine. `_gen/` n'est pas copié dans l'image.

Une fois la proposition choisie : la copier en `index.html`, passer son `robots` en `index, follow`, supprimer les autres et retirer le bloc « Sélecteur » de `_gen/gen.py`.
