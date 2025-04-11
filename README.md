# EpicEvents CRM

**EpicEvents CRM** est une application en ligne de commande (CLI) de gestion client (CRM).

Elle permet à l'entreprise Epic Events de gérer ses utilisateurs, clients, contrats et événements dans le cadre de son activité d'organisation d'événements, de manière sécurisée.

---

## Fonctionnalités principales

- Authentification sécurisée par JWT
- Gestion des rôles des employés d'Epic Events : gestion, commercial, support,
- Gestion des employés d'Epic Events : création, mise à jour, suppression, rôle,
- Gestion des clients : création, mise à jour, coordonnées, contrats et événements liés,
- Gestion des contrats : création, mise à jour, clients et événements liés,
- Gestion des événements : création, mise à jour, contrats liés,

---
## technologies utilisées

- **Python 3.12**
- **MySQL** pour la base de données relationnelle
- [SQLAlchemy](https://www.sqlalchemy.org/) – ORM
- [Pendulum](https://pypi.org/project/pendulum/) : gestion des dates
- [bcrypt](https://pypi.org/project/bcrypt/) : hachage des mots de passe
- [PyJWT](https://pypi.org/project/PyJWT/) : génération et validation de tokens JWT
- [InquirerPy](https://pypi.org/project/InquirerPy/) : menus interactifs en ligne de commande
- [python-dotenv](https://pypi.org/project/python-dotenv/)  : gestion des variables d'environnement
- [Sentry SDK](https://pypi.org/project/sentry-sdk/)   : suivi des erreurs

---

## Structure du projet

```bash
EpicEvents/
├── main.py                  # Point d'entrée de l'application
├── auth.py                  # Authentification JWT
├── .env                     # Variables d'environnement (à créer)
├── models/                  # Modèles SQLAlchemy
├── controllers/             # Logique métier
├── views/                   # Interfaces utilisateur CLI
├── tests/                   # Tests unitaires
├── db/database.py           # Connexion à la base
└── requirements.txt         # Dépendances du projet
└── sentry_config.py         # configuration de Sentry.io
```
## Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/JCOzanne/EpicEvents.git
cd EpicEvents
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate      # sur Mac/Linux
venv\Scripts\activate         # sur Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Créer le fichier `.env`
À la racine du projet, créer un fichier `.env` avec les variables d'environnement suivantes :

```env
# Connexion à la base de données
DB_USER=epic_user
DB_PASSWORD=epic_password
DB_NAME=epicevents_db
DB_HOST=localhost

# Clé secrète JWT (à générer, voir plus bas)
SECRET_KEY=your_secret_key

# DSN Sentry
SENTRY_DSN=https://your_dsn@sentry.io/project-id
(se créer un compte sur Sentry.io et obtenir sa clé dsn)
```

---

## Création de la base de données MySQL

L'application utilise **MySQL**.  
Vous devez créer la base de données et un utilisateur associé.

### Avec MySQL Command Client (https://dev.mysql.com/downloads/installer/ ):
```sql
CREATE DATABASE epicevents_db ;
CREATE USER 'epic_user'@'localhost' IDENTIFIED BY 'epic_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON epicevents_db.* TO 'epic_user'@'localhost';;
FLUSH PRIVILEGES;
```

## Lancer l'application

Une fois les dépendances installées et la base configurée :

```bash
python main.py login
```
Vous pouvez vous connecter en renseignant :  
adresse mail : admin@epicevents.com  
mot de passe : adminpassword  
Vous accéderez alors au menu principal de l'application puis aux menus interactifs pour gérer les utilisateurs, clients, contrats, événements.

---
