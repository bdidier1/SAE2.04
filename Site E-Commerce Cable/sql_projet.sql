DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS liste_envie;
DROP TABLE IF EXISTS historique;
DROP TABLE IF EXISTS commentaire;
DROP TABLE IF EXISTS note;
DROP TABLE IF EXISTS adresse;
DROP TABLE IF EXISTS declinaison_cable;
DROP TABLE IF EXISTS cable;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS type_prise;
DROP TABLE IF EXISTS longueur;
DROP TABLE IF EXISTS couleur;


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

CREATE TABLE type_prise(
    id_type_prise INT AUTO_INCREMENT,
    nom_type_prise VARCHAR(255) NOT NULL,
    PRIMARY KEY(id_type_prise)
);

CREATE TABLE longueur(
    id_longueur INT AUTO_INCREMENT,
    nom_longueur VARCHAR(255) NOT NULL,
    PRIMARY KEY(id_longueur)
);

CREATE TABLE couleur(
    id_couleur INT AUTO_INCREMENT,
    nom_couleur VARCHAR(255) NOT NULL,
    PRIMARY KEY(id_couleur)
);

CREATE TABLE etat(
    id_etat INT AUTO_INCREMENT,
    libelle VARCHAR(50) NOT NULL,
    PRIMARY KEY(id_etat)
);

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

CREATE TABLE adresse(
    id_adresse INT AUTO_INCREMENT,
    rue VARCHAR(255),
    nom_client VARCHAR(255),
    code_postal VARCHAR(5),
    ville VARCHAR(255),
    date_utilisation DATE,
    id_utilisateur INT NOT NULL,
    est_favorite BOOLEAN DEFAULT FALSE,
    est_valide BOOLEAN DEFAULT TRUE,
    PRIMARY KEY(id_adresse),
    FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

CREATE TABLE note(
    id_cable INT,
    id_utilisateur INT,
    note DOUBLE,
    PRIMARY KEY(id_cable, id_utilisateur),
    FOREIGN KEY(id_cable) REFERENCES cable(id_cable),
    FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

CREATE TABLE commentaire(
    id_commentaire INT AUTO_INCREMENT,
    id_cable INT,
    id_utilisateur INT,
    date_publication DATETIME,
    commentaire TEXT,
    valider TINYINT(1) DEFAULT 0,
    id_commentaire_parent INT NULL,
    PRIMARY KEY(id_commentaire),
    FOREIGN KEY(id_cable) REFERENCES cable(id_cable),
    FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY(id_commentaire_parent) REFERENCES commentaire(id_commentaire) ON DELETE CASCADE
);

CREATE TABLE historique(
    utilisateur_id INT,
    cable_id INT,
    date_consultation DATETIME,
    PRIMARY KEY(utilisateur_id, cable_id, date_consultation),
    FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY(cable_id) REFERENCES cable(id_cable)
);

CREATE TABLE liste_envie(
    utilisateur_id INT,
    cable_id INT,
    date_update DATETIME,
    PRIMARY KEY(utilisateur_id, cable_id, date_update),
    FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY(cable_id) REFERENCES cable(id_cable)
);

CREATE TABLE commande(
   id_commande INT AUTO_INCREMENT,
   date_achat DATE NOT NULL,
   etat_id INT NOT NULL,
   id_utilisateur INT NOT NULL,
   adresse_id_livr INT NOT NULL,
   adresse_id_fact  INT NOT NULL,
   PRIMARY KEY(id_commande),
   CONSTRAINT fk_commande_etat FOREIGN KEY(etat_id) REFERENCES etat(id_etat),
   CONSTRAINT fk_commande_utilisateur FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur),
   CONSTRAINT fk_commande_livraison FOREIGN KEY(adresse_id_livr) REFERENCES adresse(id_adresse),
   CONSTRAINT fk_commande_facturation FOREIGN KEY(adresse_id_fact) REFERENCES adresse(id_adresse)
);

CREATE TABLE ligne_commande(
    id_declinaison_cable INT,
    id_commande INT,
    prix DECIMAL(6,2) NOT NULL,
    quantite INT NOT NULL,
    PRIMARY KEY(id_declinaison_cable, id_commande),
    FOREIGN KEY(id_declinaison_cable) REFERENCES declinaison_cable(id_declinaison_cable),
    FOREIGN KEY(id_commande) REFERENCES commande(id_commande)
);

CREATE TABLE ligne_panier(
    id_declinaison_cable INT,
    id_utilisateur INT,
    quantite INT NOT NULL,
    date_ajout DATE,
    PRIMARY KEY(id_declinaison_cable, id_utilisateur),
    FOREIGN KEY(id_declinaison_cable) REFERENCES declinaison_cable(id_declinaison_cable),
    FOREIGN KEY(id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

INSERT INTO etat (id_etat, libelle) VALUES (1, 'En cours de traitement');
INSERT INTO etat (id_etat, libelle) VALUES (2, 'expédié');
INSERT INTO etat (id_etat, libelle) VALUES (3, 'validé');

INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (1, 'USB-A');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (2, 'USB-C');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (3, 'HDMI');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (4, 'Ethernet');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (5, 'Lightning');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (6, 'DisplayPort');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (7, 'VGA');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (8, 'DVI');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (9, 'Thunderbolt');
INSERT INTO type_prise (id_type_prise, nom_type_prise) VALUES (10, 'Micro-USB');

INSERT INTO longueur (id_longueur, nom_longueur) VALUES (1, '1m');
INSERT INTO longueur (id_longueur, nom_longueur) VALUES (2, '2m');
INSERT INTO longueur (id_longueur, nom_longueur) VALUES (3, '3m');
INSERT INTO longueur (id_longueur, nom_longueur) VALUES (4, '5m');
INSERT INTO longueur (id_longueur, nom_longueur) VALUES (5, '10m');

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

INSERT INTO couleur (id_couleur, nom_couleur) VALUES (1, 'Noir');
INSERT INTO couleur (id_couleur, nom_couleur) VALUES (2, 'Blanc');
INSERT INTO couleur (id_couleur, nom_couleur) VALUES (3, 'Gris');
INSERT INTO couleur (id_couleur, nom_couleur) VALUES (4, 'Bleu');
INSERT INTO couleur (id_couleur, nom_couleur) VALUES (5, 'Rouge');

INSERT INTO cable (id_cable, nom_cable, prix_cable, blindage, fournisseur, image_cable, id_type_prise)
VALUES
(1, 'Cable USB-A', 5.99, 'Non', 'Fournisseur A', 'usb_noir.png', 1),
(2, 'Cable USB-C', 7.99, 'Oui', 'Fournisseur B', 'usbc_blanc.png', 2),
(3, 'Cable HDMI', 12.99, 'Non', 'Fournisseur C', 'hdmi_gris.png', 3),
(4, 'Cable Ethernet', 8.99, 'Oui', 'Fournisseur D', 'ethernet_bleu.png', 4),
(5, 'Cable Lightning', 14.99, 'Non', 'Fournisseur E', 'lightning_rouge.png', 5),
(6, 'Câble DisplayPort', 10.99, 'Non', 'Fournisseur F', 'displayport.jpeg', 6),
(7, 'Câble VGA', 6.99, 'Non', 'Fournisseur G', 'vga.jpg', 7),
(8, 'Câble DVI', 9.99, 'Non', 'Fournisseur H', 'dvi.jpg', 8),
(9, 'Câble Thunderbolt', 19.99, 'Oui', 'Fournisseur I', 'thunderbolt.jpeg', 9),
(10, 'Câble Micro-USB', 4.99, 'Non', 'Fournisseur J', 'microusb.jpeg', 10),
(11, 'Câble USB-A vers USB-C', 6.99, 'Non', 'Fournisseur K', 'usb_a_to_c.jpeg', 1),
(12, 'Câble HDMI Haute Vitesse', 15.99, 'Oui', 'Fournisseur L', 'hdmi_hdmi.jpeg', 3),
(13, 'Câble Ethernet Cat6', 11.99, 'Oui', 'Fournisseur M', 'ethernet_cat6.jpeg', 4),
(14, 'Câble Lightning vers USB-C', 17.99, 'Non', 'Fournisseur N', 'lightning_to_usbc.jpeg', 5),
(15, 'Câble DisplayPort vers HDMI', 13.99, 'Non', 'Fournisseur O', 'displayport_hdmi.jpeg', 6);

-- Insert missing combinations for each cable, longueur, and couleur
INSERT INTO declinaison_cable (stock, prix_declinaison, image, id_longueur, id_couleur, id_cable)
VALUES
-- USB-A Cable (id_cable = 1)
(0, 6.99, 'usb_blanc.png', 1, 2, 1),
(10, 7.99, 'usb_blanc.png', 3, 2, 1),
(5, 9.99, 'usb_blanc.png', 4, 2, 1),
(12, 6.53, 'usb_gris.png', 2, 3, 1),
(15, 6.99, 'usb_bleu.png', 1, 4, 1),
(10, 7.99, 'usb_bleu.png', 3, 4, 1),
(5, 9.99, 'usb_bleu.png', 4, 4, 1),
(12, 6.53, 'usb_rouge.png', 2, 5, 1),

-- USB-C Cable (id_cable = 2)
(20, 8.99, 'usbc_noir.png', 1, 1, 2),
(18, 9.99, 'usbc_noir.png', 2, 1, 2),
(12, 11.99, 'usbc_noir.png', 3, 1, 2),
(20, 8.99, 'usbc_gris.png', 1, 3, 2),
(0, 9.99, 'usbc_gris.png', 2, 3, 2),
(12, 11.99, 'usbc_gris.png', 3, 3, 2),
(20, 8.99, 'usbc_bleu.png', 1, 4, 2),
(18, 9.99, 'usbc_bleu.png', 2, 4, 2),
(12, 11.99, 'usbc_bleu.png', 3, 4, 2),
(20, 8.99, 'usbc_rouge.png', 1, 5, 2),
(18, 9.99, 'usbc_rouge.png', 2, 5, 2),
(12, 11.99, 'usbc_rouge.png', 3, 5, 2),

-- HDMI Cable (id_cable = 3)
(25, 13.99, 'hdmi_noir.png', 1, 1, 3),
(20, 14.99, 'hdmi_noir.png', 2, 1, 3),
(10, 16.99, 'hdmi_noir.png', 4, 1, 3),
(25, 13.99, 'hdmi_blanc.png', 1, 2, 3),
(20, 14.99, 'hdmi_blanc.png', 2, 2, 3),
(10, 16.99, 'hdmi_blanc.png', 4, 2, 3),
(25, 13.99, 'hdmi_bleu.png', 1, 4, 3),
(20, 14.99, 'hdmi_bleu.png', 2, 4, 3),
(10, 16.99, 'hdmi_bleu.png', 4, 4, 3),
(25, 13.99, 'hdmi_rouge.png', 1, 5, 3),
(0, 14.99, 'hdmi_rouge.png', 2, 5, 3),
(10, 16.99, 'hdmi_rouge.png', 4, 5, 3),

-- Ethernet Cable (id_cable = 4)
(30, 9.99, 'ethernet_noir.png', 1, 1, 4),
(28, 10.99, 'ethernet_noir.png', 2, 1, 4),
(15, 12.99, 'ethernet_noir.png', 4, 1, 4),
(30, 9.99, 'ethernet_blanc.png', 1, 2, 4),
(28, 10.99, 'ethernet_blanc.png', 2, 2, 4),
(0, 12.99, 'ethernet_blanc.png', 4, 2, 4),
(30, 9.99, 'ethernet_gris.png', 1, 3, 4),
(28, 10.99, 'ethernet_gris.png', 2, 3, 4),
(15, 12.99, 'ethernet_gris.png', 4, 3, 4),
(30, 9.99, 'ethernet_rouge.png', 1, 5, 4),
(28, 10.99, 'ethernet_rouge.png', 2, 5, 4),
(15, 12.99, 'ethernet_rouge.png', 4, 5, 4),

-- Lightning Cable (id_cable = 5)
(18, 15.99, 'lightning_noir.png', 1, 1, 5),
(14, 17.99, 'lightning_noir.png', 2, 1, 5),
(10, 19.99, 'lightning_noir.png', 3, 1, 5),
(18, 15.99, 'lightning_blanc.png', 1, 2, 5),
(0, 17.99, 'lightning_blanc.png', 2, 2, 5),
(10, 19.99, 'lightning_blanc.png', 3, 2, 5),
(18, 15.99, 'lightning_gris.png', 1, 3, 5),
(14, 17.99, 'lightning_gris.png', 2, 3, 5),
(10, 19.99, 'lightning_gris.png', 3, 3, 5),
(18, 15.99, 'lightning_bleu.png', 1, 4, 5),
(14, 17.99, 'lightning_bleu.png', 2, 4, 5),
(10, 19.99, 'lightning_bleu.png', 3, 4, 5),

-- DisplayPort Cable (id_cable = 6)
(15, 11.99, 'displayport.jpeg', 1, 1, 6),
(10, 12.99, 'displayport.jpeg', 2, 1, 6),
(5, 14.99, 'displayport.jpeg', 3, 1, 6),
(12, 11.53, 'displayport_hdmi.jpeg', 1, 2, 6),
(15, 11.99, 'displayport_hdmi.jpeg', 1, 4, 6),
(10, 12.99, 'displayport_hdmi.jpeg', 2, 4, 6),
(3, 14.99, 'displayport_hdmi.jpeg', 3, 4, 6),
(12, 11.53, 'displayport_hdmi.jpeg', 1, 5, 6),

-- VGA Cable (id_cable = 7)
(20, 7.99, 'vga.jpg', 1, 1, 7),
(18, 8.99, 'vga.jpg', 2, 1, 7),
(0, 10.99, 'vga.jpg', 3, 1, 7),
(20, 7.99, 'vga.jpg', 1, 2, 7),
(18, 8.99, 'vga.jpg', 2, 2, 7),
(12, 10.99, 'vga.jpg', 3, 2, 7),
(20, 7.99, 'vga.jpg', 1, 4, 7),
(18, 8.99, 'vga.jpg', 2, 4, 7),
(12, 10.99, 'vga.jpg', 3, 4, 7),
(20, 7.99, 'vga.jpg', 1, 5, 7),
(18, 8.99, 'vga.jpg', 2, 5, 7),
(12, 10.99, 'vga.jpg', 3, 5, 7),

-- DVI Cable (id_cable = 8)
(25, 10.99, 'dvi.jpg', 1, 1, 8),
(20, 11.99, 'dvi.jpg', 2, 1, 8),
(10, 13.99, 'dvi.jpg', 4, 1, 8),
(25, 10.99, 'dvi.jpg', 1, 2, 8),
(20, 11.99, 'dvi.jpg', 2, 2, 8),
(10, 13.99, 'dvi.jpg', 4, 2, 8),
(25, 10.99, 'dvi.jpg', 1, 4, 8),
(20, 11.99, 'dvi.jpg', 2, 4, 8),
(10, 13.99, 'dvi.jpg', 4, 4, 8),
(25, 10.99, 'dvi.jpg', 1, 5, 8),
(0, 11.99, 'dvi.jpg', 2, 5, 8),
(10, 13.99, 'dvi.jpg', 4, 5, 8),

-- Thunderbolt Cable (id_cable = 9)
(18, 20.99, 'thunderbolt.jpeg', 1, 1, 9),
(14, 22.99, 'thunderbolt.jpeg', 2, 1, 9),
(10, 24.99, 'thunderbolt.jpeg', 3, 1, 9),
(18, 20.99, 'thunderbolt.jpeg', 1, 2, 9),
(14, 22.99, 'thunderbolt.jpeg', 2, 2, 9),
(10, 24.99, 'thunderbolt.jpeg', 3, 2, 9),
(18, 20.99, 'thunderbolt.jpeg', 1, 3, 9),
(14, 22.99, 'thunderbolt.jpeg', 2, 3, 9),
(0, 24.99, 'thunderbolt.jpeg', 3, 3, 9),
(18, 20.99, 'thunderbolt.jpeg', 1, 4, 9),
(14, 22.99, 'thunderbolt.jpeg', 2, 4, 9),
(10, 24.99, 'thunderbolt.jpeg', 3, 4, 9),

-- Micro-USB Cable (id_cable = 10)
(30, 5.99, 'microusb.jpeg', 1, 1, 10),
(28, 6.99, 'microusb.jpeg', 2, 1, 10),
(15, 8.99, 'microusb.jpeg', 4, 1, 10),
(0, 5.99, 'microusb.jpeg', 1, 2, 10),
(28, 6.99, 'microusb.jpeg', 2, 2, 10),
(15, 8.99, 'microusb.jpeg', 4, 2, 10),
(30, 5.99, 'microusb.jpeg', 1, 5, 10),
(28, 6.99, 'microusb.jpeg', 2, 5, 10),
(15, 8.99, 'microusb.jpeg', 4, 5, 10),

-- USB-A to USB-C Cable (id_cable = 11)
(20, 7.99, 'usb_a_to_c.jpeg', 1, 1, 11),
(18, 8.99, 'usb_a_to_c.jpeg', 2, 1, 11),
(12, 10.99, 'usb_a_to_c.jpeg', 3, 1, 11),
(20, 7.99, 'usb_a_to_c.jpeg', 1, 2, 11),
(18, 8.99, 'usb_a_to_c.jpeg', 2, 2, 11),
(12, 10.99, 'usb_a_to_c.jpeg', 3, 2, 11),
(20, 7.99, 'usb_a_to_c.jpeg', 1, 3, 11),
(18, 8.99, 'usb_a_to_c.jpeg', 2, 3, 11),
(12, 10.99, 'usb_a_to_c.jpeg', 3, 3, 11),

-- HDMI High Speed Cable (id_cable = 12)
(25, 16.99, 'hdmi_hdmi.jpeg', 1, 1, 12),
(20, 17.99, 'hdmi_hdmi.jpeg', 2, 1, 12),
(10, 19.99, 'hdmi_hdmi.jpeg', 4, 1, 12),
(25, 16.99, 'hdmi_hdmi.jpeg', 1, 2, 12),
(20, 17.99, 'hdmi_hdmi.jpeg', 2, 2, 12),
(0, 19.99, 'hdmi_hdmi.jpeg', 4, 2, 12),
(25, 16.99, 'hdmi_hdmi.jpeg', 1, 4, 12),
(20, 17.99, 'hdmi_hdmi.jpeg', 2, 4, 12),
(10, 19.99, 'hdmi_hdmi.jpeg', 4, 4, 12),
(25, 16.99, 'hdmi_hdmi.jpeg', 1, 5, 12),
(20, 17.99, 'hdmi_hdmi.jpeg', 2, 5, 12),
(10, 19.99, 'hdmi_hdmi.jpeg', 4, 5, 12),

-- Ethernet Cat6 Cable (id_cable = 13)
(30, 12.99, 'ethernet_cat6.jpeg', 1, 1, 13),
(28, 13.99, 'ethernet_cat6.jpeg', 2, 1, 13),
(15, 15.99, 'ethernet_cat6.jpeg', 4, 1, 13),
(30, 12.99, 'ethernet_cat6.jpeg', 1, 2, 13),
(28, 13.99, 'ethernet_cat6.jpeg', 2, 2, 13),
(15, 15.99, 'ethernet_cat6.jpeg', 4, 2, 13),
(30, 12.99, 'ethernet_cat6.jpeg', 1, 3, 13),
(28, 13.99, 'ethernet_cat6.jpeg', 2, 3, 13),
(15, 15.99, 'ethernet_cat6.jpeg', 4, 3, 13),
(30, 12.99, 'ethernet_cat6.jpeg', 1, 5, 13),
(28, 13.99, 'ethernet_cat6.jpeg', 2, 5, 13),
(0, 15.99, 'ethernet_cat6.jpeg', 4, 5, 13),

-- Lightning to USB-C Cable (id_cable = 14)
(0, 18.99, 'lightning_to_usbc.jpeg', 1, 1, 14),
(14, 20.99, 'lightning_to_usbc.jpeg', 2, 1, 14),
(10, 22.99, 'lightning_to_usbc.jpeg', 3, 1, 14),
(18, 18.99, 'lightning_to_usbc.jpeg', 1, 2, 14),
(14, 20.99, 'lightning_to_usbc.jpeg', 2, 2, 14),
(10, 22.99, 'lightning_to_usbc.jpeg', 3, 2, 14),
(18, 18.99, 'lightning_to_usbc.jpeg', 1, 3, 14),
(14, 20.99, 'lightning_to_usbc.jpeg', 2, 3, 14),
(10, 22.99, 'lightning_to_usbc.jpeg', 3, 3, 14),

-- DisplayPort to HDMI Cable (id_cable = 15)
(20, 14.99, 'displayport_hdmi.jpeg', 1, 1, 15),
(18, 15.99, 'displayport_hdmi.jpeg', 2, 1, 15),
(12, 17.99, 'displayport_hdmi.jpeg', 3, 1, 15),
(0, 14.99, 'displayport_hdmi.jpeg', 1, 2, 15),
(18, 15.99, 'displayport_hdmi.jpeg', 2, 2, 15),
(12, 17.99, 'displayport_hdmi.jpeg', 3, 2, 15),
(20, 14.99, 'displayport_hdmi.jpeg', 1, 3, 15),
(18, 15.99, 'displayport_hdmi.jpeg', 2, 3, 15),
(12, 17.99, 'displayport_hdmi.jpeg', 3, 3, 15);

INSERT INTO adresse (nom_client, rue, code_postal, ville, date_utilisation, id_utilisateur)
VALUES
('Natcow', '123 Rue Exemple', '75001', 'Paris', NOW(), 2),
('Babadidier', '456 Avenue Exemple', '75002', 'Paris', NOW(), 2);

-- Commandes pour l'utilisateur "client"
INSERT INTO commande (date_achat, etat_id, id_utilisateur, adresse_id_livr, adresse_id_fact) VALUES
('2025-04-01', 1, 2, 1, 1),
('2025-04-02', 2, 2, 1, 1),
('2025-04-03', 3, 2, 1, 1),
('2025-04-04', 1, 2, 1, 1),
('2025-04-05', 2, 2, 1, 1),
('2025-04-06', 3, 2, 1, 1),
('2025-04-07', 1, 2, 1, 1),
('2025-04-08', 2, 2, 1, 1),
('2025-04-09', 3, 2, 1, 1),
('2025-04-10', 1, 2, 1, 1);

-- Lignes de commande pour "client"
INSERT INTO ligne_commande (id_declinaison_cable, id_commande, prix, quantite) VALUES
(1, 1, 6.99, 2),
(16, 2, 15.99, 1),
(25, 3, 9.99, 3),
(36, 4, 19.99, 2),
(48, 5, 12.49, 1),
(59, 6, 5.99, 4),
(65, 7, 24.99, 1),
(42, 8, 7.49, 2),
(70, 9, 14.99, 1),
(80, 10, 11.99, 3);

-- Commandes pour l'utilisateur "client2"
INSERT INTO commande (date_achat, etat_id, id_utilisateur, adresse_id_livr, adresse_id_fact) VALUES
('2025-04-01', 1, 3, 2, 2),
('2025-04-02', 2, 3, 2, 2),
('2025-04-03', 3, 3, 2, 2),
('2025-04-04', 1, 3, 2, 2),
('2025-04-05', 2, 3, 2, 2),
('2025-04-06', 3, 3, 2, 2),
('2025-04-07', 1, 3, 2, 2),
('2025-04-08', 2, 3, 2, 2),
('2025-04-09', 3, 3, 2, 2),
('2025-04-10', 1, 3, 2, 2);

-- Lignes de commande pour "client2"
INSERT INTO ligne_commande (id_declinaison_cable, id_commande, prix, quantite) VALUES
(90, 11, 8.99, 1),
(110, 12, 14.99, 2),
(120, 13, 7.99, 1),
(130, 14, 21.99, 1),
(140, 15, 10.49, 3),
(150, 16, 4.99, 2),
(90, 17, 29.99, 2),
(111, 18, 6.49, 1),
(27, 19, 16.99, 3),
(135, 20, 13.99, 2);

INSERT INTO note (id_cable, id_utilisateur, note) VALUES
(1, 2, 4.5),
(1, 3, 3.8),
(2, 2, 5.0),
(2, 3, 4.2),
(3, 2, 4.7),
(3, 3, 3.5),
(4, 2, 4.0),
(4, 3, 4.8),
(5, 2, 3.9),
(5, 3, 4.6),
(6, 2, 5.0),
(6, 3, 4.3),
(7, 2, 4.1),
(7, 3, 3.7),
(8, 2, 4.9),
(8, 3, 4.2),
(9, 2, 4.4),
(9, 3, 4.0),
(10, 2, 3.6),
(10, 3, 4.5);

INSERT INTO commentaire (id_cable, id_utilisateur, date_publication, commentaire, valider) VALUES
(8, 2, NOW(), 'Super câble DVI, fonctionne parfaitement !', 1),
(7, 2, NOW(), 'Qualité correcte, mais un peu cher.', 1),
(4, 2, NOW(), 'Longueur parfaite pour mon setup.', 1),
(1, 2, NOW(), 'Bonne connectivité, satisfait.', 1),
(4, 2, NOW(), 'Idéal pour connecter mon PC à la télé.', 1),
(5, 2, NOW(), 'Bonne qualité, mais jaurais aimé une meilleure finition.', 1),
(2, 2, NOW(), 'Bon câble USB-C, rapide et fiable.', 1),
(6, 2, NOW(), 'Un peu rigide mais très performant.', 1),
(7, 2, NOW(), 'Compatibilité parfaite avec mon iPhone.', 1),
(3, 2, NOW(), 'Charge rapide et solide.', 1),
 (6, 2, NOW(), 'Affichage nickel, aucun souci.', 1),

(13, 3, NOW(), 'Bonne transmission vidéo.', 1),
(9, 3, NOW(), 'Un Thunderbolt classique, fait le job.', 1),
(12, 3, NOW(), 'Pas mal, mais je préfère HDMI.', 1),
(9, 3, NOW(), 'Thunderbolt encore utile pour mes vieux écrans.', 1),
(11, 3, NOW(), 'Un bon rapport qualité/prix.', 1),
(13, 3, NOW(), 'Ethernet Cat6, toujours au top !', 1),
(11, 3, NOW(), 'Transfert rapide, rien à redire.', 1),
(3, 3, NOW(), 'HDMI fonctionne bien, mais obsolète.', 1),
(14, 3, NOW(), 'Pas très solide, dommage.', 1);

-- Ajout de données pour l'historique de consultation
INSERT INTO historique (utilisateur_id, cable_id, date_consultation) VALUES
(2, 1, '2023-01-10 09:30:45'), -- Client 1 consulte Cable USB-A
(2, 2, '2023-01-10 09:35:22'), -- Client 1 consulte Cable USB-C
(2, 3, '2023-01-10 09:40:15'), -- Client 1 consulte Cable HDMI
(2, 3, '2023-01-11 10:15:30'), -- Client 1 reconsulte Cable HDMI
(2, 5, '2023-01-11 10:20:45'), -- Client 1 consulte Cable Lightning
(3, 2, '2023-01-12 11:30:15'), -- Client 2 consulte Cable USB-C
(3, 4, '2023-01-12 11:35:45'), -- Client 2 consulte Cable Ethernet
(3, 6, '2023-01-12 11:40:22'), -- Client 2 consulte Cable DisplayPort
(3, 8, '2023-01-13 14:25:12'), -- Client 2 consulte Cable DVI
(2, 9, '2023-01-14 15:10:34'), -- Client 1 consulte Cable Thunderbolt
(2, 7, '2023-01-14 15:15:28'), -- Client 1 consulte Cable VGA
(3, 1, '2023-01-15 16:05:42'), -- Client 2 consulte Cable USB-A
(3, 3, '2023-01-15 16:10:18'), -- Client 2 consulte Cable HDMI
(3, 5, '2023-01-15 16:15:35'), -- Client 2 consulte Cable Lightning
(2, 4, '2023-01-16 09:20:53'), -- Client 1 consulte Cable Ethernet
(2, 6, '2023-01-17 10:30:12'), -- Client 1 consulte Cable DisplayPort
(3, 7, '2023-01-18 11:45:30'), -- Client 2 consulte Cable VGA
(3, 9, '2023-01-19 13:15:45'); -- Client 2 consulte Cable Thunderbolt

-- Ajout de données récentes pour l'historique (pour les graphiques dataviz)
INSERT INTO historique (utilisateur_id, cable_id, date_consultation) VALUES
(2, 1, NOW() - INTERVAL 5 DAY),
(2, 3, NOW() - INTERVAL 4 DAY),
(2, 5, NOW() - INTERVAL 3 DAY),
(3, 2, NOW() - INTERVAL 5 DAY),
(3, 4, NOW() - INTERVAL 4 DAY),
(3, 6, NOW() - INTERVAL 3 DAY),
(2, 7, NOW() - INTERVAL 2 DAY),
(3, 8, NOW() - INTERVAL 2 DAY),
(2, 9, NOW() - INTERVAL 1 DAY),
(3, 1, NOW() - INTERVAL 1 DAY);

-- CORRECTION: Liste d'envies avec une seule entrée par article par utilisateur
-- Dates espacées régulièrement pour permettre les opérations de tri up/down
-- Client 1 (id=2) - Articles avec des dates espacées de 1 heure
INSERT INTO liste_envie (utilisateur_id, cable_id, date_update) VALUES
(2, 1, NOW() - INTERVAL 15 HOUR), -- Le plus ancien (position 15)
(2, 3, NOW() - INTERVAL 14 HOUR), -- (position 14)
(2, 5, NOW() - INTERVAL 13 HOUR), -- (position 13)
(2, 7, NOW() - INTERVAL 12 HOUR), -- (position 12)
(2, 9, NOW() - INTERVAL 11 HOUR), -- (position 11)
(2, 10, NOW() - INTERVAL 10 HOUR), -- (position 10)
(2, 11, NOW() - INTERVAL 9 HOUR), -- (position 9)
(2, 12, NOW() - INTERVAL 8 HOUR), -- (position 8)
(2, 13, NOW() - INTERVAL 7 HOUR), -- (position 7)
(2, 14, NOW() - INTERVAL 6 HOUR), -- (position 6)
(2, 15, NOW() - INTERVAL 5 HOUR); -- (position 5, le plus récent)

-- Client 2 (id=3) - Articles avec des dates espacées de 1 heure
INSERT INTO liste_envie (utilisateur_id, cable_id, date_update) VALUES
(3, 2, NOW() - INTERVAL 15 HOUR), -- Le plus ancien (position 15)
(3, 4, NOW() - INTERVAL 14 HOUR), -- (position 14)
(3, 6, NOW() - INTERVAL 13 HOUR), -- (position 13)
(3, 8, NOW() - INTERVAL 12 HOUR), -- (position 12)
(3, 10, NOW() - INTERVAL 11 HOUR), -- (position 11)
(3, 11, NOW() - INTERVAL 10 HOUR), -- (position 10)
(3, 12, NOW() - INTERVAL 9 HOUR), -- (position 9)
(3, 13, NOW() - INTERVAL 8 HOUR), -- (position 8)
(3, 14, NOW() - INTERVAL 7 HOUR), -- (position 7)
(3, 15, NOW() - INTERVAL 6 HOUR); -- (position 6, le plus récent)

-- Ajout de données supplémentaires pour l'historique de consultation
INSERT INTO historique (utilisateur_id, cable_id, date_consultation) VALUES
-- Client 1 (id=2) consultations supplémentaires
(2, 10, '2023-01-20 10:25:15'), -- Client 1 consulte Cable Micro-USB
(2, 11, '2023-01-20 10:30:22'), -- Client 1 consulte Cable USB-A vers USB-C
(2, 12, '2023-01-20 10:35:45'), -- Client 1 consulte Cable HDMI Haute Vitesse
(2, 13, '2023-01-21 09:40:12'), -- Client 1 consulte Cable Ethernet Cat6
(2, 14, '2023-01-21 09:45:30'), -- Client 1 consulte Cable Lightning vers USB-C
(2, 15, '2023-01-21 09:50:45'), -- Client 1 consulte Cable DisplayPort vers HDMI
(2, 1, '2023-01-22 14:10:20'), -- Client 1 reconsulte Cable USB-A
(2, 3, '2023-01-22 14:15:35'), -- Client 1 reconsulte Cable HDMI
(2, 5, '2023-01-22 14:20:48'), -- Client 1 reconsulte Cable Lightning
(2, 7, '2023-01-23 16:30:22'), -- Client 1 reconsulte Cable VGA
(2, 9, '2023-01-23 16:35:12'), -- Client 1 reconsulte Cable Thunderbolt
(2, 11, '2023-01-23 16:40:33'), -- Client 1 reconsulte Cable USB-A vers USB-C

-- Client 2 (id=3) consultations supplémentaires
(3, 10, '2023-01-20 11:05:15'), -- Client 2 consulte Cable Micro-USB
(3, 11, '2023-01-20 11:10:30'), -- Client 2 consulte Cable USB-A vers USB-C
(3, 12, '2023-01-20 11:15:45'), -- Client 2 consulte Cable HDMI Haute Vitesse
(3, 13, '2023-01-21 13:20:22'), -- Client 2 consulte Cable Ethernet Cat6
(3, 14, '2023-01-21 13:25:33'), -- Client 2 consulte Cable Lightning vers USB-C
(3, 15, '2023-01-21 13:30:45'), -- Client 2 consulte Cable DisplayPort vers HDMI
(3, 2, '2023-01-22 15:35:12'), -- Client 2 reconsulte Cable USB-C
(3, 4, '2023-01-22 15:40:25'), -- Client 2 reconsulte Cable Ethernet
(3, 6, '2023-01-22 15:45:33'), -- Client 2 reconsulte Cable DisplayPort
(3, 8, '2023-01-23 17:50:45'), -- Client 2 reconsulte Cable DVI
(3, 10, '2023-01-23 17:55:15'), -- Client 2 reconsulte Cable Micro-USB
(3, 12, '2023-01-23 18:00:30'), -- Client 2 reconsulte Cable HDMI Haute Vitesse

-- Consultations récentes pour le client 1 (pour dataviz)
(2, 1, NOW() - INTERVAL 23 DAY),
(2, 2, NOW() - INTERVAL 22 DAY),
(2, 3, NOW() - INTERVAL 21 DAY),
(2, 4, NOW() - INTERVAL 20 DAY),
(2, 5, NOW() - INTERVAL 19 DAY),
(2, 6, NOW() - INTERVAL 18 DAY),
(2, 7, NOW() - INTERVAL 17 DAY),
(2, 8, NOW() - INTERVAL 16 DAY),
(2, 9, NOW() - INTERVAL 15 DAY),
(2, 10, NOW() - INTERVAL 14 DAY),
(2, 11, NOW() - INTERVAL 13 DAY),
(2, 12, NOW() - INTERVAL 12 DAY),
(2, 13, NOW() - INTERVAL 11 DAY),
(2, 14, NOW() - INTERVAL 10 DAY),
(2, 15, NOW() - INTERVAL 9 DAY),

-- Consultations récentes pour le client 2 (pour dataviz)
(3, 1, NOW() - INTERVAL 22 DAY),
(3, 2, NOW() - INTERVAL 21 DAY),
(3, 3, NOW() - INTERVAL 20 DAY),
(3, 4, NOW() - INTERVAL 19 DAY),
(3, 5, NOW() - INTERVAL 18 DAY),
(3, 6, NOW() - INTERVAL 17 DAY),
(3, 7, NOW() - INTERVAL 16 DAY),
(3, 8, NOW() - INTERVAL 15 DAY),
(3, 9, NOW() - INTERVAL 14 DAY),
(3, 10, NOW() - INTERVAL 13 DAY),
(3, 11, NOW() - INTERVAL 12 DAY),
(3, 12, NOW() - INTERVAL 11 DAY),
(3, 13, NOW() - INTERVAL 10 DAY),
(3, 14, NOW() - INTERVAL 9 DAY),
(3, 15, NOW() - INTERVAL 8 DAY),

-- Consultations très récentes (moins d'une semaine) pour le client 1
(2, 1, NOW() - INTERVAL 6 DAY),
(2, 3, NOW() - INTERVAL 6 DAY),
(2, 5, NOW() - INTERVAL 5 DAY),
(2, 7, NOW() - INTERVAL 5 DAY),
(2, 9, NOW() - INTERVAL 4 DAY),
(2, 11, NOW() - INTERVAL 4 DAY),
(2, 13, NOW() - INTERVAL 3 DAY),
(2, 15, NOW() - INTERVAL 3 DAY),
(2, 2, NOW() - INTERVAL 2 DAY),
(2, 4, NOW() - INTERVAL 2 DAY),
(2, 6, NOW() - INTERVAL 1 DAY),
(2, 8, NOW() - INTERVAL 1 DAY),
(2, 10, NOW() - INTERVAL 12 HOUR),
(2, 12, NOW() - INTERVAL 8 HOUR),
(2, 14, NOW() - INTERVAL 4 HOUR),

-- Consultations très récentes (moins d'une semaine) pour le client 2
(3, 2, NOW() - INTERVAL 6 DAY),
(3, 4, NOW() - INTERVAL 6 DAY),
(3, 6, NOW() - INTERVAL 5 DAY),
(3, 8, NOW() - INTERVAL 5 DAY),
(3, 10, NOW() - INTERVAL 4 DAY),
(3, 12, NOW() - INTERVAL 4 DAY),
(3, 14, NOW() - INTERVAL 3 DAY),
(3, 1, NOW() - INTERVAL 3 DAY),
(3, 3, NOW() - INTERVAL 2 DAY),
(3, 5, NOW() - INTERVAL 2 DAY),
(3, 7, NOW() - INTERVAL 1 DAY),
(3, 9, NOW() - INTERVAL 1 DAY),
(3, 11, NOW() - INTERVAL 12 HOUR),
(3, 13, NOW() - INTERVAL 8 HOUR),
(3, 15, NOW() - INTERVAL 4 HOUR);

-- Consultations multiples du même article le même jour (pour montrer l'intérêt)
INSERT INTO historique (utilisateur_id, cable_id, date_consultation) VALUES
(2, 1, NOW() - INTERVAL 3 DAY + INTERVAL 1 HOUR),
(2, 1, NOW() - INTERVAL 3 DAY + INTERVAL 2 HOUR),
(2, 1, NOW() - INTERVAL 3 DAY + INTERVAL 3 HOUR),
(2, 3, NOW() - INTERVAL 2 DAY + INTERVAL 1 HOUR),
(2, 3, NOW() - INTERVAL 2 DAY + INTERVAL 2 HOUR),
(2, 5, NOW() - INTERVAL 1 DAY + INTERVAL 1 HOUR),
(2, 5, NOW() - INTERVAL 1 DAY + INTERVAL 2 HOUR),
(3, 2, NOW() - INTERVAL 3 DAY + INTERVAL 1 HOUR),
(3, 2, NOW() - INTERVAL 3 DAY + INTERVAL 2 HOUR),
(3, 2, NOW() - INTERVAL 3 DAY + INTERVAL 3 HOUR),
(3, 4, NOW() - INTERVAL 2 DAY + INTERVAL 1 HOUR),
(3, 4, NOW() - INTERVAL 2 DAY + INTERVAL 2 HOUR),
(3, 6, NOW() - INTERVAL 1 DAY + INTERVAL 1 HOUR),
(3, 6, NOW() - INTERVAL 1 DAY + INTERVAL 2 HOUR);
