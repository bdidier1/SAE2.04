#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, Flask, request, render_template, redirect, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__, template_folder='templates')

@client_commande.route('/client/commande/valide', methods=['GET', 'POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    if request.method == 'POST':
        id_declinaison_cable = request.form.get('id_declinaison_cable')
        if id_declinaison_cable:
            sql_check_article = '''
            SELECT lp.quantite, dc.stock
            FROM ligne_panier lp
            JOIN declinaison_cable dc ON lp.id_declinaison_cable = dc.id_declinaison_cable
            WHERE lp.id_utilisateur = %s AND lp.id_declinaison_cable = %s;
            '''
            mycursor.execute(sql_check_article, (id_client, id_declinaison_cable))
            article_info = mycursor.fetchone()

            if article_info:
                quantite = article_info['quantite']
                sql_update_stock = '''
                UPDATE declinaison_cable 
                SET stock = stock + %s 
                WHERE id_declinaison_cable = %s;
                '''
                mycursor.execute(sql_update_stock, (quantite, id_declinaison_cable))

                sql_delete_article = '''
                DELETE FROM ligne_panier
                WHERE id_utilisateur = %s AND id_declinaison_cable = %s;
                '''
                mycursor.execute(sql_delete_article, (id_client, id_declinaison_cable))

                get_db().commit()
                flash("Article supprimé du panier avec succès.", "alert-success")
            else:
                flash("L'article n'existe pas dans le panier.", "error")

    sql_articles_panier = '''
    SELECT lp.id_declinaison_cable, lp.quantite, dc.prix_declinaison AS prix,
           (lp.quantite * dc.prix_declinaison) AS sous_total, c.nom_cable AS nom_article,
           dc.id_couleur, co.nom_couleur AS libelle_couleur,
           dc.id_longueur AS id_taille, lo.nom_longueur AS libelle_taille,
           dc.stock, dc.id_declinaison_cable AS id_declinaison_article
    FROM ligne_panier lp
    JOIN declinaison_cable dc ON lp.id_declinaison_cable = dc.id_declinaison_cable
    JOIN cable c ON dc.id_cable = c.id_cable
    JOIN couleur co ON dc.id_couleur = co.id_couleur
    JOIN longueur lo ON dc.id_longueur = lo.id_longueur
    WHERE lp.id_utilisateur = %s;
    '''
    mycursor.execute(sql_articles_panier, (id_client,))
    articles_panier = mycursor.fetchall()

    sql_prix_total = '''
    SELECT COALESCE(SUM(lp.quantite * dc.prix_declinaison), 0) AS prix_total
    FROM ligne_panier lp
    JOIN declinaison_cable dc ON lp.id_declinaison_cable = dc.id_declinaison_cable
    WHERE lp.id_utilisateur = %s;
    '''
    mycursor.execute(sql_prix_total, (id_client,))
    prix_total = mycursor.fetchone()['prix_total']

    sql_adresses = '''
    SELECT 
        id_adresse, 
        rue, 
        ville, 
        code_postal,
        est_favorite
    FROM adresse
    WHERE id_utilisateur = %s AND est_valide = 1
    ORDER BY est_favorite DESC, id_adresse DESC;
    '''
    mycursor.execute(sql_adresses, (id_client,))
    adresses = mycursor.fetchall()

    return render_template('client/boutique/panier_validation_adresses.html',
                           adresses=adresses,
                           articles_panier=articles_panier,
                           prix_total=prix_total,
                           validation=1)

@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    adresse_id_livr = request.form.get('id_adresse_livraison')
    adresse_id_fact = request.form.get('id_adresse_facturation')

    adresse_identique = request.form.get('adresse_identique')

    if adresse_identique:
        adresse_id_fact = adresse_id_livr

    if not adresse_id_livr or not adresse_id_fact:
        flash(u"Veuillez fournir des adresses de livraison et de facturation valides.", 'alert-danger')
        return redirect('/client/commande/valide')

    if not adresse_id_livr.isdigit() or not adresse_id_fact.isdigit():
        flash(u"Les adresses de livraison et de facturation doivent être des entiers valides.", 'alert-danger')
        return redirect('/client/commande/valide')

    adresse_id_livr = int(adresse_id_livr)
    adresse_id_fact = int(adresse_id_fact)

    # Mettre à jour l'adresse favorite
    sql_update_favorite = '''
    UPDATE adresse 
    SET est_favorite = CASE 
        WHEN id_adresse = %s THEN 1 
        ELSE 0 
    END
    WHERE id_utilisateur = %s AND est_valide = 1;
    '''
    mycursor.execute(sql_update_favorite, (adresse_id_livr, id_client))

    sql_insert_commande = '''
    INSERT INTO commande (id_utilisateur, date_achat, etat_id, adresse_id_livr, adresse_id_fact)
    VALUES (%s, NOW(), 1, %s, %s);
    '''
    mycursor.execute(sql_insert_commande, (id_client, adresse_id_livr, adresse_id_fact))
    id_commande = mycursor.lastrowid

    sql_move_panier_to_commande = '''
    INSERT INTO ligne_commande (id_commande, id_declinaison_cable, quantite, prix)
    SELECT
        %s AS id_commande,
        lp.id_declinaison_cable,
        lp.quantite,
        dc.prix_declinaison
    FROM ligne_panier lp
    JOIN declinaison_cable dc ON lp.id_declinaison_cable = dc.id_declinaison_cable
    WHERE lp.id_utilisateur = %s;
    '''
    mycursor.execute(sql_move_panier_to_commande, (id_commande, id_client))

    # Supprimer les articles commandés de la liste d'envies
    sql_remove_from_wishlist = '''
    DELETE le FROM liste_envie le
    JOIN declinaison_cable dc ON le.cable_id = dc.id_cable
    JOIN ligne_panier lp ON dc.id_declinaison_cable = lp.id_declinaison_cable
    WHERE le.utilisateur_id = %s AND lp.id_utilisateur = %s;
    '''
    mycursor.execute(sql_remove_from_wishlist, (id_client, id_client))

    sql_delete_panier = '''
    DELETE FROM ligne_panier
    WHERE id_utilisateur = %s;
    '''
    mycursor.execute(sql_delete_panier, (id_client,))

    get_db().commit()

    flash(u'Commande ajoutée avec succès', 'alert-success')
    return redirect('/client/commande/show')

@client_commande.route('/client/commande/show', methods=['GET', 'POST'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql_commandes = '''
    SELECT
        c.id_commande,
        c.date_achat,
        c.etat_id,
        e.libelle AS libelle,
        COUNT(lc.id_declinaison_cable) AS nbr_articles,
        COALESCE(SUM(lc.quantite * lc.prix), 0) AS prix_total
    FROM commande c
    JOIN etat e ON c.etat_id = e.id_etat
    LEFT JOIN ligne_commande lc ON c.id_commande = lc.id_commande
    WHERE c.id_utilisateur = %s
    GROUP BY c.id_commande, c.date_achat, c.etat_id
    ORDER BY c.etat_id ASC;
    '''
    mycursor.execute(sql_commandes, (id_client,))
    commandes = mycursor.fetchall()

    id_commande = request.args.get('id_commande')
    articles_commande = None
    commande_adresses = None

    if id_commande:
        sql_articles_commande = '''
        SELECT
    lc.id_declinaison_cable,
    lc.quantite,
    lc.prix,
    (lc.quantite * lc.prix) AS prix_ligne, 
    c.nom_cable AS nom,
    co.nom_couleur AS libelle_couleur,
    l.nom_longueur AS libelle_taille
FROM ligne_commande lc
JOIN declinaison_cable dc ON lc.id_declinaison_cable = dc.id_declinaison_cable
JOIN cable c ON dc.id_cable = c.id_cable
JOIN couleur co ON dc.id_couleur = co.id_couleur
JOIN longueur l ON dc.id_longueur = l.id_longueur
WHERE lc.id_commande = %s;
        '''
        mycursor.execute(sql_articles_commande, (id_commande,))
        articles_commande = mycursor.fetchall()

        sql_adresses_commande = '''
        SELECT
            a_liv.rue AS rue_livraison,
            a_liv.ville AS ville_livraison,
            a_liv.code_postal AS code_postal_livraison,
            a_fact.rue AS rue_facturation,
            a_fact.ville AS ville_facturation,
            a_fact.code_postal AS code_postal_facturation
        FROM commande c
        JOIN adresse a_liv ON c.adresse_id_livr = a_liv.id_adresse
        JOIN adresse a_fact ON c.adresse_id_fact = a_fact.id_adresse
        WHERE c.id_commande = %s;
        '''
        mycursor.execute(sql_adresses_commande, (id_commande,))
        commande_adresses = mycursor.fetchone()

    return render_template('client/commandes/show.html',
                           commandes=commandes,
                           articles_commande=articles_commande,
                           commande_adresses=commande_adresses)