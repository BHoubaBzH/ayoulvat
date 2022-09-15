# Titre du projet
AYOULVAT

logiciel de gestion d'évènement : plannings bénévoles responsables

# Pour commencer

Projet basé sur le framework django et bootstrap en cours de construction, les evenements et les ressources pour l'inscription des bénévoles sont OK.
il reste comme fonctionnalités à développer:
- création d'association par les utilisateurs ( utilisation de django-admin pour l'instant)
- création d'évènement par les utilisateurs ( utilisation de django-admin pour l'instant)
- module de paiement ( a ajouter en totalité )

# Pré-requis

- Python 3.10
- Django 4.0
- Bootstrap 5

un hébergement web offrant la possibilité d'applications python

# Installation

Cloner le projet sur la racine application python de l'hébergeur.
Mettre à jour les appli et modules suivant le requirements.txt

`pip install -r requirements.txt`

Créer le fichier .env à la racine de l'application python, et compléter les infos:

```
# SECURITY WARNING: keep the secret key used in production secret!`
SECRET_KEY = ''

# Database
DB_NAME = ''
DB_USER = ''
DB_PASSWORD = ''
DB_HOST = ''
DB_PORT = ''

# smtp
EMAIL_HOST = ""
EMAIL_PORT = ""
EMAIL_USERNAME = ""
EMAIL_PASSWORD = ""
EMAIL_USE_TLS =     #False or True
EMAIL_USE_SSL =     #False or True
EMAIL_TIMEOUT = ""  #default 10 
EMAIL_DEFAULT_FROM = ""
#ssl_keyfile: EMAIL_SSL_KEYFILE
#ssl_certfile: EMAIL_SSL_CERTFILE

# Projet
PROJET_ENV = "PROD" #DEV or PROD, use PROD for production
```

exemples :

visualisaton des créneaux:

https://ayoulvat.deusta.bzh/github_ress/creneaux.png


visualisation des équipes:


https://ayoulvat.deusta.bzh/github_ress/equipes.png


visualisation des stats organisateur:

https://ayoulvat.deusta.bzh/github_ress/stats.png


# Démarrage

cela va dépendre de votre hébergeur,

Voir le lien suivant pour plus de détail sur django:

https://www.djangoproject.com/start/

# Fabriqué avec

* [![django](https://badgen.net/badge/made_with/django/20AA76)](https://www.djangoproject.com/)
* [![python](https://badgen.net/badge/made_with/python/3776ab)](https://www.python.org/)
* [![bootstrap](https://badgen.net/badge/made_with/bootsrap/795da3)](https://getbootstrap.com/)
* [![javascript](https://badgen.net/badge/made_with/javascript/f7e018)](https://developer.mozilla.org/fr/docs/Web/JavaScript)

## Contributing

send me a message ;)

## Versions

## Auteurs

* **Phil RIOUAL** _alias_ [@BhoubaBZH](http://phil.rioual.free.fr)

## License

Ce projet est sous licence ``GPLv3`` 