#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                        template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['GET', 'POST'])
def admin_commande_show():
    mycursor = get_db().cursor()

    sql_all = """
    SELECT 
    c.id_commande AS id_commande, 
    c.date_achat AS date_achat, 
    COALESCE(SUM(lc.quantite * lc.prix), 0) AS prix_total, 
    c.etat_id AS etat_id, 
    e.libelle AS libelle, 
    u.login AS login, 
    COALESCE(COUNT(lc.id_declinaison_cable), 0) AS nbr_articles
FROM commande c
JOIN etat e ON c.etat_id = e.id_etat
JOIN utilisateur u ON c.id_utilisateur = u.id_utilisateur
LEFT JOIN ligne_commande lc ON c.id_commande = lc.id_commande
GROUP BY c.id_commande, c.date_achat, c.etat_id, e.libelle, u.login
ORDER BY c.date_achat DESC;


    """

    mycursor.execute(sql_all)
    commandes = mycursor.fetchall()

    id_commande = request.args.get('id_commande', None)
    articles_commande = None
    commande_adresses = None

    if id_commande:
        sql_one = '''
            SELECT
    c.id_commande,
    c.date_achat,
    c.etat_id,
    e.libelle AS etat_commande,
    u.login AS client_login,
    livr.nom_client AS nom_livraison,
    livr.rue AS rue_livraison,
    livr.code_postal AS code_postal_livraison,
    livr.ville AS ville_livraison,
    fact.nom_client AS nom_facturation,
    fact.rue AS rue_facturation,
    fact.code_postal AS code_postal_facturation,
    fact.ville AS ville_facturation,
    ca.nom_cable AS nom,
    lc.quantite,
    lc.prix AS prix,
    (lc.quantite * lc.prix) AS prix_ligne,
    dc.stock AS nb_declinaisons,
    co.nom_couleur AS libelle_couleur,
    lo.nom_longueur AS libelle_longueur
FROM
    commande c
JOIN
    etat e ON c.etat_id = e.id_etat
JOIN
    utilisateur u ON c.id_utilisateur = u.id_utilisateur
JOIN
    adresse livr ON c.adresse_id_livr = livr.id_adresse
JOIN
    adresse fact ON c.adresse_id_fact = fact.id_adresse
LEFT JOIN
    ligne_commande lc ON c.id_commande = lc.id_commande
LEFT JOIN
    declinaison_cable dc ON lc.id_declinaison_cable = dc.id_declinaison_cable
LEFT JOIN
    cable ca ON dc.id_cable = ca.id_cable
LEFT JOIN
    couleur co ON dc.id_couleur = co.id_couleur
LEFT JOIN
    longueur lo ON dc.id_longueur = lo.id_longueur
WHERE
    c.id_commande = %s;

        '''
        mycursor.execute(sql_one, (id_commande,))
        resultats = mycursor.fetchall()

        if resultats:
            articles_commande = resultats
            commande_adresses = resultats[0]

    return render_template('admin/commandes/show.html',
                           commandes=commandes,
                           articles_commande=articles_commande,
                           commande_adresses=commande_adresses)



@admin_commande.route('/admin/commande/valider', methods=['get','post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id != None:
        print(commande_id)
        sql = '''
                   UPDATE commande 
            SET etat_id = 2 
            WHERE id_commande = %s 
            AND etat_id = 1;
            '''
        mycursor.execute(sql, commande_id)
        get_db().commit()
    return redirect('/admin/commande/show')