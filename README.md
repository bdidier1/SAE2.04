# Projet Cablissimo - SAE 2.04

Ce projet porte sur le développement d’un site e-commerce dédié à la vente de câbles, intitulé « Cablissimo ». Il s’inscrit dans le cadre d’une Situation d’Apprentissage et d’Évaluation (SAÉ) et comprend plusieurs livrables répartis dans différents dossiers.

## Structure du Projet

### 1. Livrable 1
Ce dossier contient les éléments de modélisation de la base de données :

- **MCD_v1.pdf** : Modèle Conceptuel de Données initial
- **MLD_v1.pdf** : Modèle Logique de Données initial
- **sae_sql.sql** : Script SQL initial pour la création et l'alimentation de la base de données
- **livrable1_sae_2_4_bdd-1.ods** : Document tableur contenant les données du projet

### 2. Gestion de Projet
Ce dossier contient la documentation de gestion du projet :

- **Cahier-Des-Charges_Cablissimo.pdf** : Spécifications et exigences du projet
- **Dossier_GestionProjet_11.pdf** : Document principal de gestion de projet (planification, organisation)
- **PAQP_11.pdf** : Plan d'Assurance Qualité Projet
- **Cost_Analysis_G11.pdf** : Analyse des coûts du projet

### 3. Site E-Commerce Cable
Ce dossier contient l'implémentation du site e-commerce en utilisant le framework Flask (Python):

#### Structure du site web :
- **app.py** : Point d'entrée de l'application Flask, gestion des routes principales
- **connexion_db.py** : Gestion de la connexion à la base de données
- **sql_projet.sql** : Script SQL final avec le schéma complet de la base de données
- **flask_run.sh** : Script pour lancer l'application

#### Organisation MVC :
- **controllers/** : Contient les contrôleurs de l'application organisés par fonctionnalité :
  - Partie admin (gestion des articles, commandes, etc.)
  - Partie client (panier, commandes, articles, etc.)
  - Authentication et sécurité

- **templates/** : Contient les vues HTML organisées en dossiers :
  - admin/ : Interface d'administration
  - client/ : Interface utilisateur client
  - auth/ : Pages d'authentification

- **static/** : Ressources statiques (CSS, JavaScript, images)

## Base de données

La base de données du projet a évolué entre le livrable 1 et la version finale. Elle est centrée autour d'une boutique en ligne de câbles avec :

- Gestion des utilisateurs (clients/administrateurs)
- Catalogue de produits (câbles avec différentes caractéristiques)
- Système de commandes et panier
- Déclinaisons des articles (longueur, couleur, type de prise)
- Système de commentaires et notes

## Démarrage de l'application

Pour lancer l'application :

1. S'assurer que Flask est installé : `pip install flask`
2. Configurer la base de données MySQL
3. Exécuter le script sql_projet.sql
4. Lancer l'application avec : `bash flask_run.sh` ou `flask --debug --app app run`
5. Accéder à l'application dans un navigateur à l'adresse : http://127.0.0.1:5000

## Comptes utilisateurs

L'application dispose de comptes préconfigurés :
- Admin : login: admin, mot de passe: admin@admin.fr
- Client : login: client, mot de passe: client@client.fr
