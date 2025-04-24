DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS cable;
DROP TABLE IF EXISTS type_prise;
DROP TABLE IF EXISTS longueur;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS etat;

CREATE TABLE type_prise(
   id_type_prise INT,
   nom_type_prise VARCHAR(255),
   PRIMARY KEY(id_type_prise)
);

CREATE TABLE longueur(
   id_longueur INT,
   nom_longueur VARCHAR(255),
   PRIMARY KEY(id_longueur)
);

CREATE TABLE cable(
   id_cable INT,
   nom_cable VARCHAR(255),
   couleur VARCHAR(50),
   prix_cable DECIMAL(6,2),
   blindage VARCHAR(50),
   fournisseur VARCHAR(255),
   image_cable VARCHAR(50),
   id_type_prise INT NOT NULL,
   id_longueur INT NOT NULL,
   PRIMARY KEY(id_cable),
   FOREIGN KEY(id_type_prise) REFERENCES type_prise(id_type_prise),
   FOREIGN KEY(id_longueur) REFERENCES longueur(id_longueur)
);

CREATE TABLE utilisateur(
    id_utilisateur INT AUTO_INCREMENT,
    login VARCHAR(255),
    email VARCHAR(255),
    nom VARCHAR(255),
    password VARCHAR(255),
    role VARCHAR(255),
    est_actif tinyint(1),
    PRIMARY KEY(id_utilisateur)
)DEFAULT CHARSET utf8mb4;

CREATE TABLE etat(
   id_etat INT,
   libelle VARCHAR(50),
   PRIMARY KEY(id_etat)
);

CREATE TABLE commande(
   id_commande INT,
   date_achat DATE,
   id_etat INT NOT NULL,
   id_utilisateur INT NOT NULL,
   PRIMARY KEY(id_commande),
   CONSTRAINT fk_etat FOREIGN KEY(id_etat) REFERENCES etat(id_etat),
   CONSTRAINT fk_utilisateur FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);


CREATE TABLE ligne_commande(
   id_cable INT,
   id_commande INT,
   prix DECIMAL(6,2),
   quantite INT,
   PRIMARY KEY(id_cable, id_commande),
   FOREIGN KEY(id_cable) REFERENCES cable(id_cable),
   FOREIGN KEY(id_commande) REFERENCES commande(id_commande)
);

CREATE TABLE ligne_panier(
   id_cable INT,
   id_utilisateur INT,
   quantite INT,
   date_ajout DATE,
   PRIMARY KEY(id_cable, id_utilisateur),
   FOREIGN KEY(id_cable) REFERENCES cable(id_cable),
   FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

INSERT INTO etat (id_etat, libelle) VALUES (1, 'Très Mauvais');
INSERT INTO etat (id_etat, libelle) VALUES (2, 'Mauvais');
INSERT INTO etat (id_etat, libelle) VALUES (3, 'Moyen');
INSERT INTO etat (id_etat, libelle) VALUES (4, 'Bon');
INSERT INTO etat (id_etat, libelle) VALUES (5, 'Très Bon');

INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (1, 'USB-A');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (2, 'USB-C');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (3, 'HDMI');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (4, 'Ethernet');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (5, 'Lightning');


INSERT INTO longueur (id_longueur, nom_longueur) VALUES (1, '1 meter');
INSERT INTO longueur (id_longueur, nom_longueur) VALUES (2, '2 meters');
INSERT INTO longueur (id_longueur, nom_longueur) VALUES (3, '3 meters');
INSERT INTO longueur (id_longueur, nom_longueur) VALUES (4, '5 meters');
INSERT INTO longueur (id_longueur, nom_longueur) VALUES (5, '10 meters');

INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom,est_actif) VALUES
(1,'admin','admin@admin.fr',
    'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
    'ROLE_admin','admin','1'),
(2,'client','client@client.fr',
    'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
    'ROLE_client','client','1'),
(3,'client2','client2@client2.fr',
    'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
    'ROLE_client','client2','1');


INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (1, 'Cable USB-A 1m',  'Noir', 5.99, 'Non', 'Fournisseur A', 'usb_noir.png', 1, 1);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (2, 'Cable USB-C 2m',  'Blanc', 7.99, 'Oui', 'Fournisseur B', 'usbc_blanc.png', 2, 2);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (3, 'Cable HDMI 3m',  'Gris', 12.99, 'Non', 'Fournisseur C', 'hdmi_gris.png', 3, 3);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (4, 'Cable Ethernet 5m',  'Bleu', 8.99, 'Oui', 'Fournisseur D', 'ethernet_bleu.png', 4, 4);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (5, 'Cable Lightning 1m',  'Rouge', 14.99, 'Non', 'Fournisseur E', 'lightning_rouge.png', 5, 1);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (6, 'Cable USB-A 2m',  'Blanc', 6.99, 'Oui', 'Fournisseur A', 'usb_blanc.png', 1, 2);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (7, 'Cable USB-C 3m',  'Rouge', 9.99, 'Non', 'Fournisseur B', 'usbc_rouge.png', 2, 3);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (8, 'Cable HDMI 5m',  'Bleu', 15.99, 'Oui', 'Fournisseur C', 'hdmi_bleu.png', 3, 4);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (9, 'Cable Ethernet 10m',  'Noir', 11.99, 'Non', 'Fournisseur D', 'ethernet_noir.png', 4, 5);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (10, 'Cable Lightning 2m',  'Bleu', 16.99, 'Oui', 'Fournisseur E', 'lightning_bleu.png', 5, 2);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (11, 'Cable USB-A 3m',  'Gris', 7.99, 'Non', 'Fournisseur A', 'usb_gris.png', 1, 3);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (12, 'Cable USB-C 5m',  'Bleu', 10.99, 'Oui', 'Fournisseur B', 'usbc_bleu.png', 2, 4);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (13, 'Cable HDMI 10m',  'Rouge', 18.99, 'Non', 'Fournisseur C', 'hdmi_rouge.png', 3, 5);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (14, 'Cable Ethernet 1m',  'Blanc', 5.49, 'Oui', 'Fournisseur D', 'ethernet_blanc.png', 4, 1);
INSERT INTO cable (id_cable, nom_cable, couleur, prix_cable, blindage, fournisseur, image_cable, id_type_prise, id_longueur) VALUES (15, 'Cable Lightning 5m',  'Noir', 19.99, 'Non', 'Fournisseur E', 'lightning_noir.png', 5, 4);