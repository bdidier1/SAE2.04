#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                          template_folder='templates')


@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_article_stock():
    mycursor = get_db().cursor()
    sql = '''
    SELECT 
        tp.id_type_prise AS id_type_article,
        tp.nom_type_prise AS libelle,
        COUNT(DISTINCT c.id_cable) AS nbr_articles,
        COUNT(DISTINCT n.id_utilisateur) AS nbr_notes,
        AVG(n.note) AS note_moyenne,
        COUNT(DISTINCT com.id_utilisateur) AS nbr_commentaires
    FROM 
        type_prise tp
    LEFT JOIN 
        cable c ON tp.id_type_prise = c.id_type_prise
    LEFT JOIN 
        note n ON c.id_cable = n.id_cable
    LEFT JOIN 
        commentaire com ON c.id_cable = com.id_cable
    GROUP BY 
        tp.id_type_prise, tp.nom_type_prise
    ORDER BY 
        tp.nom_type_prise;
    '''
    mycursor.execute(sql)
    datas_show = mycursor.fetchall()

    # Préparation des données pour les graphiques
    labels = [str(row['libelle']) for row in datas_show]

    # Données pour le graphique de la note moyenne par type d'article
    values_note_moyenne = [float(row['note_moyenne']) if row['note_moyenne'] is not None else 0 for row in datas_show]

    # Données pour le graphique du nombre de commentaires par type d'article
    values_nb_commentaires = [int(row['nbr_commentaires']) if row['nbr_commentaires'] is not None else 0 for row in
                              datas_show]

    # Données pour le graphique du nombre de notes par type d'article
    values_nb_notes = [int(row['nbr_notes']) if row['nbr_notes'] is not None else 0 for row in datas_show]

    return render_template('admin/dataviz/dataviz_etat_1.html',
                           datas_show=datas_show,
                           labels=labels,
                           values_note_moyenne=values_note_moyenne,
                           values_nb_commentaires=values_nb_commentaires,
                           values_nb_notes=values_nb_notes)


# sujet 3 : adresses


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    mycursor = get_db().cursor()

    # Requête pour les statistiques par département
    sql_stats = '''
    SELECT 
        LEFT(a.code_postal, 2) as dep,
        COUNT(DISTINCT c.id_commande) as nombre_ventes,
        COUNT(DISTINCT c.id_utilisateur) as nombre_clients,
        SUM(lc.prix * lc.quantite) as chiffre_affaires,
        SUM(lc.prix * lc.quantite) / COUNT(DISTINCT c.id_commande) as panier_moyen,
        COUNT(DISTINCT c.id_commande) / MAX(COUNT(DISTINCT c.id_commande)) OVER() as indice_ventes,
        SUM(lc.prix * lc.quantite) / MAX(SUM(lc.prix * lc.quantite)) OVER() as indice_ca
    FROM commande c
    JOIN adresse a ON c.adresse_id_livr = a.id_adresse
    JOIN ligne_commande lc ON c.id_commande = lc.id_commande
    GROUP BY LEFT(a.code_postal, 2)
    ORDER BY dep;
    '''
    mycursor.execute(sql_stats)
    stats = mycursor.fetchall()

    # Préparation des données pour les graphiques
    labels = [row['dep'] for row in stats]
    values_ventes = [row['nombre_ventes'] for row in stats]
    values_ca = [row['chiffre_affaires'] for row in stats]

    return render_template('admin/dataviz/dataviz_etat_map.html',
                           stats=stats,
                           labels=labels,
                           values_ventes=values_ventes,
                           values_ca=values_ca)


@admin_dataviz.route('/admin/dataviz/type_article')
def show_dataviz_type_article():
    id_type_article = request.args.get('id_type_article', type=int)
    if id_type_article is None:
        abort(404, "Type d'article non trouvé")
        
    mycursor = get_db().cursor()

    # Récupérer le nom du type d'article
    sql_type = '''
    SELECT nom_type_prise AS libelle
    FROM type_prise
    WHERE id_type_prise = %s;
    '''
    mycursor.execute(sql_type, (id_type_article,))
    type_article = mycursor.fetchone()

    # Récupérer les données pour les articles de ce type
    sql = '''
    SELECT 
        c.id_cable AS id_article,
        c.nom_cable AS libelle,
        COUNT(DISTINCT n.id_utilisateur) AS nbr_notes,
        AVG(n.note) AS note_moyenne,
        COUNT(DISTINCT com.id_utilisateur) AS nbr_commentaires
    FROM 
        cable c
    LEFT JOIN 
        note n ON c.id_cable = n.id_cable
    LEFT JOIN 
        commentaire com ON c.id_cable = com.id_cable
    WHERE 
        c.id_type_prise = %s
    GROUP BY 
        c.id_cable, c.nom_cable
    ORDER BY 
        c.nom_cable;
    '''
    mycursor.execute(sql, (id_type_article,))
    datas_show = mycursor.fetchall()

    # Préparation des données pour les graphiques
    labels = [str(row['libelle']) for row in datas_show]

    # Données pour le graphique de la note moyenne par article
    values_note_moyenne = [float(row['note_moyenne']) if row['note_moyenne'] is not None else 0 for row in datas_show]

    # Données pour le graphique du nombre de commentaires par article
    values_nb_commentaires = [int(row['nbr_commentaires']) if row['nbr_commentaires'] is not None else 0 for row in
                              datas_show]

    # Données pour le graphique du nombre de notes par article
    values_nb_notes = [int(row['nbr_notes']) if row['nbr_notes'] is not None else 0 for row in datas_show]

    return render_template('admin/dataviz/dataviz_type_article.html',
                           type_article=type_article,
                           datas_show=datas_show,
                           labels=labels,
                           values_note_moyenne=values_note_moyenne,
                           values_nb_commentaires=values_nb_commentaires,
                           values_nb_notes=values_nb_notes)


@admin_dataviz.route('/admin/dataviz/wishlist')
def show_dataviz_wishlist():
    mycursor = get_db().cursor()

    # Récupérer le nombre d'articles dans les wishlists par catégorie
    sql = '''
    SELECT 
        tp.id_type_prise AS id_type_article,
        tp.nom_type_prise AS libelle,
        COUNT(DISTINCT le.cable_id) AS nb_articles_wishlist
    FROM 
        type_prise tp
    LEFT JOIN 
        cable c ON tp.id_type_prise = c.id_type_prise
    LEFT JOIN 
        liste_envie le ON c.id_cable = le.cable_id
    GROUP BY 
        tp.id_type_prise, tp.nom_type_prise
    ORDER BY 
        tp.nom_type_prise;
    '''
    mycursor.execute(sql)
    datas_wishlist = mycursor.fetchall()

    # Récupérer le nombre d'articles dans les historiques par catégorie (sur le mois)
    sql = '''
    SELECT 
        tp.id_type_prise AS id_type_article,
        tp.nom_type_prise AS libelle,
        COUNT(DISTINCT h.cable_id) AS nb_articles_historique
    FROM 
        type_prise tp
    LEFT JOIN 
        cable c ON tp.id_type_prise = c.id_type_prise
    LEFT JOIN 
        historique h ON c.id_cable = h.cable_id
    WHERE 
        h.date_consultation >= DATE_SUB(NOW(), INTERVAL 1 MONTH) OR h.date_consultation IS NULL
    GROUP BY 
        tp.id_type_prise, tp.nom_type_prise
    ORDER BY 
        tp.nom_type_prise;
    '''
    mycursor.execute(sql)
    datas_historique = mycursor.fetchall()

    # Préparation des données pour les graphiques
    labels = [str(row['libelle']) for row in datas_wishlist]

    # Données pour le graphique du nombre d'articles dans les wishlists par catégorie
    values_wishlist = [int(row['nb_articles_wishlist']) if row['nb_articles_wishlist'] is not None else 0 for row in
                       datas_wishlist]

    # Données pour le graphique du nombre d'articles dans les historiques par catégorie
    values_historique = [int(row['nb_articles_historique']) if row['nb_articles_historique'] is not None else 0 for row
                         in datas_historique]

    return render_template('admin/dataviz/dataviz_wishlist.html',
                           datas_wishlist=datas_wishlist,
                           datas_historique=datas_historique,
                           labels=labels,
                           values_wishlist=values_wishlist,
                           values_historique=values_historique)


@admin_dataviz.route('/admin/dataviz/wishlist/type_article')
def show_dataviz_wishlist_type_article():
    id_type_article = request.args.get('id_type_article', type=int)
    if id_type_article is None:
        abort(404, "Type d'article non trouvé")
        
    mycursor = get_db().cursor()

    # Récupérer le nom du type d'article
    sql_type = '''
    SELECT nom_type_prise AS libelle
    FROM type_prise
    WHERE id_type_prise = %s;
    '''
    mycursor.execute(sql_type, (id_type_article,))
    type_article = mycursor.fetchone()

    # Récupérer le nombre d'articles dans les wishlists pour chaque article de ce type
    sql = '''
    SELECT 
        c.id_cable AS id_article,
        c.nom_cable AS libelle,
        COUNT(DISTINCT le.utilisateur_id) AS nb_utilisateurs_wishlist
    FROM 
        cable c
    LEFT JOIN 
        liste_envie le ON c.id_cable = le.cable_id
    WHERE 
        c.id_type_prise = %s
    GROUP BY 
        c.id_cable, c.nom_cable
    ORDER BY 
        c.nom_cable;
    '''
    mycursor.execute(sql, (id_type_article,))
    datas_wishlist = mycursor.fetchall()

    # Récupérer le nombre d'articles dans les historiques pour chaque article de ce type (sur le mois)
    sql = '''
    SELECT 
        c.id_cable AS id_article,
        c.nom_cable AS libelle,
        COUNT(DISTINCT h.utilisateur_id) AS nb_utilisateurs_historique
    FROM 
        cable c
    LEFT JOIN 
        historique h ON c.id_cable = h.cable_id
    WHERE 
        c.id_type_prise = %s
        AND (h.date_consultation >= DATE_SUB(NOW(), INTERVAL 1 MONTH) OR h.date_consultation IS NULL)
    GROUP BY 
        c.id_cable, c.nom_cable
    ORDER BY 
        c.nom_cable;
    '''
    mycursor.execute(sql, (id_type_article,))
    datas_historique = mycursor.fetchall()

    # Préparation des données pour les graphiques
    labels = [str(row['libelle']) for row in datas_wishlist]

    # Données pour le graphique du nombre d'utilisateurs ayant l'article dans leur wishlist
    values_wishlist = [int(row['nb_utilisateurs_wishlist']) if row['nb_utilisateurs_wishlist'] is not None else 0 for
                       row in datas_wishlist]

    # Données pour le graphique du nombre d'utilisateurs ayant l'article dans leur historique
    values_historique = [int(row['nb_utilisateurs_historique']) if row['nb_utilisateurs_historique'] is not None else 0
                         for row in datas_historique]

    return render_template('admin/dataviz/dataviz_wishlist_type_article.html',
                           type_article=type_article,
                           datas_wishlist=datas_wishlist,
                           datas_historique=datas_historique,
                           labels=labels,
                           values_wishlist=values_wishlist,
                           values_historique=values_historique)

