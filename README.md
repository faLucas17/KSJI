# Site Vitrine KSJI

Site web professionnel pour KSJI - Kébé Services Juridiques Islamiques

## Installation

1. Cloner le projet
2. Créer un environnement virtuel : `python -m venv venv`
3. Activer l'environnement : `source venv/bin/activate` (Linux/Mac) ou `venv\Scripts\activate` (Windows)
4. Installer les dépendances : `pip install -r requirements.txt`
5. Configurer les variables d'environnement dans `.env`
6. Lancer les migrations : `python manage.py migrate`
7. Créer un superutilisateur : `python manage.py createsuperuser`
8. Lancer le serveur : `python manage.py runserver`

## Structure

- `core/` : Application principale (accueil, services, contact)
- `blog/` : Application blog/articles
- `static/` : Fichiers CSS, JS, images
- `templates/` : Templates HTML
- `media/` : Fichiers uploadés