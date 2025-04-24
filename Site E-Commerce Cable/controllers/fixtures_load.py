#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import *
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__, template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()

    tables_to_drop = [
        'ligne_panier',
        'ligne_commande',
        'commande',
        'liste_envie',
        'historique',
        'commentaire',
        'note',
        'adresse',
        'declinaison_cable',
        'cable',
        'utilisateur',
        'etat',
        'type_prise',
        'longueur',
        'couleur'
    ]

    for table in tables_to_drop:
        mycursor.execute(f"DROP TABLE IF EXISTS {table};")

    sql_queries = [
        '''
        CREATE TABLE utilisateur(
            id_utilisateur INT AUTO_INCREMENT,
            login VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            nom VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            est_actif TINYINT(1) DEFAULT 1,
            PRIMARY KEY(id_utilisateur)
        ) DEFAULT CHARSET=utf8mb4;
        ''',
        '''
        CREATE TABLE type_prise(
            id_type_prise INT AUTO_INCREMENT,
            nom_type_prise VARCHAR(255) NOT NULL,
            PRIMARY KEY(id_type_prise)
        );
        ''',
        '''
        CREATE TABLE longueur(
            id_longueur INT AUTO_INCREMENT,
            nom_longueur VARCHAR(255) NOT NULL,
            PRIMARY KEY(id_longueur)
        );
        ''',
        '''
        CREATE TABLE couleur(
            id_couleur INT AUTO_INCREMENT,
            nom_couleur VARCHAR(255) NOT NULL,
            PRIMARY KEY(id_couleur)
        );
        ''',
        '''
        CREATE TABLE etat(
            id_etat INT AUTO_INCREMENT,
            libelle VARCHAR(50) NOT NULL,
            PRIMARY KEY(id_etat)
        );
        ''',
        '''
        CREATE TABLE cable(
            id_cable INT AUTO_INCREMENT,
            nom_cable VARCHAR(255) NOT NULL,
            prix_cable DECIMAL(6,2) NOT NULL,
            description_cable VARCHAR(255),
            blindage VARCHAR(50),
            fournisseur VARCHAR(255),
            image_cable VARCHAR(50),
            id_type_prise INT NOT NULL,
            PRIMARY KEY(id_cable),
            FOREIGN KEY(id_type_prise) REFERENCES type_prise(id_type_prise)
        );
        ''',
        '''
        CREATE TABLE declinaison_cable(
            id_declinaison_cable INT AUTO_INCREMENT,
            stock INT NOT NULL DEFAULT 0,
            prix_declinaison DECIMAL(6,2) NOT NULL,
            image VARCHAR(50),
            id_longueur INT NOT NULL,
            id_couleur INT NOT NULL,
            id_cable INT NOT NULL,
            PRIMARY KEY(id_declinaison_cable),
            FOREIGN KEY(id_longueur) REFERENCES longueur(id_longueur),
            FOREIGN KEY(id_couleur) REFERENCES couleur(id_couleur),
            FOREIGN KEY(id_cable) REFERENCES cable(id_cable)
        );
        ''',
        '''
        CREATE TABLE adresse(
            id_adresse INT AUTO_INCREMENT,
            rue VARCHAR(255),
            nom_client VARCHAR(255),
            code_postal VARCHAR(5),
            ville VARCHAR(255),
            date_utilisation DATE,
            id_utilisateur INT NOT NULL,
            PRIMARY KEY(id_adresse),
            FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
        );
        ''',
        '''
        CREATE TABLE note(
            id_cable INT,
            id_utilisateur INT,
            note INT CHECK (note BETWEEN 1 AND 5),
            PRIMARY KEY(id_cable, id_utilisateur),
            FOREIGN KEY(id_cable) REFERENCES cable(id_cable),
            FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
        );
        ''',
        '''
        CREATE TABLE commentaire(
            id_cable INT,
            id_utilisateur INT,
            date_publication DATE,
            commentaire TEXT,
            valider TINYINT(1) DEFAULT 0,
            PRIMARY KEY(id_cable, id_utilisateur, date_publication),
            FOREIGN KEY(id_cable) REFERENCES cable(id_cable),
            FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
        );
        ''',
        '''
        CREATE TABLE historique(
            utilisateur_id INT,
            cable_id INT,
            date_consultation DATETIME,
            PRIMARY KEY(utilisateur_id, cable_id, date_consultation),
            FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
            FOREIGN KEY(cable_id) REFERENCES cable(id_cable)
        );
        ''',
        '''
        CREATE TABLE liste_envie(
            utilisateur_id INT,
            cable_id INT,
            date_update DATETIME,
            PRIMARY KEY(utilisateur_id, cable_id, date_update),
            FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
            FOREIGN KEY(cable_id) REFERENCES cable(id_cable)
        );
        ''',
        '''
        CREATE TABLE commande(
            id_commande INT AUTO_INCREMENT,
            date_achat DATE NOT NULL,
            etat_id INT NOT NULL,
            id_utilisateur INT NOT NULL,
            adresse_id_livr INT NOT NULL,
            adresse_id_fact INT NOT NULL,
            PRIMARY KEY(id_commande),
            CONSTRAINT fk_commande_etat FOREIGN KEY(etat_id) REFERENCES etat(id_etat),
            CONSTRAINT fk_commande_utilisateur FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur),
            CONSTRAINT fk_commande_livraison FOREIGN KEY(adresse_id_livr) REFERENCES adresse(id_adresse),
            CONSTRAINT fk_commande_facturation FOREIGN KEY(adresse_id_fact) REFERENCES adresse(id_adresse)
        );
        ''',
        '''
        CREATE TABLE ligne_commande(
            id_declinaison_cable INT,
            id_commande INT,
            prix DECIMAL(6,2) NOT NULL,
            quantite INT NOT NULL,
            PRIMARY KEY(id_declinaison_cable, id_commande),
            FOREIGN KEY(id_declinaison_cable) REFERENCES declinaison_cable(id_declinaison_cable),
            FOREIGN KEY(id_commande) REFERENCES commande(id_commande)
        );
        ''',
        '''
        CREATE TABLE ligne_panier(
            id_declinaison_cable INT,
            id_utilisateur INT,
            quantite INT NOT NULL,
            date_ajout DATE,
            PRIMARY KEY(id_declinaison_cable, id_utilisateur),
            FOREIGN KEY(id_declinaison_cable) REFERENCES declinaison_cable(id_declinaison_cable),
            FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
        );
        '''
    ]

    for sql in sql_queries:
        mycursor.execute(sql)

    insert_queries = [
        '''
        INSERT INTO etat (id_etat, libelle) VALUES
        (1, 'En cours de traitement'),
        (2, 'Expédié'),
        (3, 'Validé');
        ''',
        '''
        INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES
        (1, 'USB-A'),
        (2, 'USB-C'),
        (3, 'HDMI'),
        (4, 'Ethernet'),
        (5, 'Lightning');
        ''',
        '''
        INSERT INTO longueur (id_longueur, nom_longueur) VALUES
        (1, '1m'),
        (2, '2m'),
        (3, '3m'),
        (4, '5m'),
        (5, '10m');
        ''',
        '''
        INSERT INTO couleur (id_couleur, nom_couleur) VALUES
        (1, 'Noir'),
        (2, 'Blanc'),
        (3, 'Gris'),
        (4, 'Bleu'),
        (5, 'Rouge');
        ''',
        '''
        INSERT INTO utilisateur (id_utilisateur, login, email, password, role, nom, est_actif) VALUES
        (1, 'admin', 'admin@admin.fr', 'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988', 'ROLE_admin', 'admin', 1),
        (2, 'client', 'client@client.fr', 'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349', 'ROLE_client', 'client', 1),
        (3, 'client2', 'client2@client2.fr', 'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080', 'ROLE_client', 'client2', 1);
        ''',
        '''
        INSERT INTO cable (id_cable, nom_cable, prix_cable, blindage, fournisseur, image_cable, id_type_prise) VALUES
        (1, 'Cable USB-A', 5.99, 'Non', 'Fournisseur A', 'usb_noir.png', 1),
        (2, 'Cable USB-C', 7.99, 'Oui', 'Fournisseur B', 'usbc_blanc.png', 2),
        (3, 'Cable HDMI', 12.99, 'Non', 'Fournisseur C', 'hdmi_gris.png', 3),
        (4, 'Cable Ethernet', 8.99, 'Oui', 'Fournisseur D', 'ethernet_bleu.png', 4),
        (5, 'Cable Lightning', 14.99, 'Non', 'Fournisseur E', 'lightning_rouge.png', 5);
        ''',
        '''
        INSERT INTO declinaison_cable (id_declinaison_cable, stock, prix_declinaison, image, id_longueur, id_couleur, id_cable) VALUES
        (6, 15, 6.99, 'usb_noir.png', 2, 1, 1),
        (7, 10, 7.99, 'usb_noir.png', 3, 1, 1),
        (8, 5, 9.99, 'usb_noir.png', 4, 1, 1),
        (9, 20, 8.99, 'usbc_blanc.png', 1, 2, 2),
        (10, 18, 9.99, 'usbc_blanc.png', 2, 2, 2),
        (11, 12, 11.99, 'usbc_blanc.png', 3, 2, 2),
        (12, 25, 13.99, 'hdmi_gris.png', 1, 3, 3),
        (13, 20, 14.99, 'hdmi_gris.png', 2, 3, 3),
        (14, 10, 16.99, 'hdmi_gris.png', 4, 3, 3),
        (15, 30, 9.99, 'ethernet_bleu.png', 1, 4, 4),
        (16, 28, 10.99, 'ethernet_bleu.png', 2, 4, 4),
        (17, 15, 12.99, 'ethernet_bleu.png', 4, 4, 4),
        (18, 18, 15.99, 'lightning_rouge.png', 1, 5, 5),
        (19, 14, 17.99, 'lightning_rouge.png', 2, 5, 5),
        (20, 10, 19.99, 'lightning_rouge.png', 3, 5, 5);
        ''',
        '''
        INSERT INTO adresse (nom_client, rue, code_postal, ville, date_utilisation, id_utilisateur) VALUES
        ('Natcow', '123 Rue Exemple', '75001', 'Paris', NOW(), 2),
        ('Babadidier', '456 Avenue Exemple', '75002', 'Paris', NOW(), 2);
        ''',
        '''
        INSERT INTO commande (id_utilisateur, date_achat, etat_id, adresse_id_livr, adresse_id_fact) VALUES
        (2, NOW(), 1,
          (SELECT id_adresse FROM adresse WHERE rue = '123 Rue Exemple' AND id_utilisateur = 2 ORDER BY id_adresse DESC LIMIT 1),
          (SELECT id_adresse FROM adresse WHERE rue = '456 Avenue Exemple' AND id_utilisateur = 2 ORDER BY id_adresse DESC LIMIT 1));
        ''',
        '''
        INSERT INTO ligne_commande (id_commande, id_declinaison_cable, prix, quantite) VALUES
        (LAST_INSERT_ID(), 6, 6.99, 2),
        (LAST_INSERT_ID(), 9, 8.99, 1);
        '''
    ]

    for sql in insert_queries:
        mycursor.execute(sql)

    get_db().commit()
    return redirect('/')