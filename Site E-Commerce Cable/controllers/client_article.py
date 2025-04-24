#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, session, request, redirect
from connexion_db import get_db
from controllers.client_liste_envies import client_historique_add

client_article = Blueprint('client_article', __name__, template_folder='templates')


@client_article.route('/client/article/declinaisons')
def client_article_declinaisons():
    mycursor = get_db().cursor()
    id_article = request.args.get('id_article', None)
    selected_couleur = request.args.get('couleur')
    selected_longueur = request.args.get('longueur')

    if not id_article:
        return redirect('/client/index')

    sql = '''
    SELECT
        c.id_cable AS id_article,
        c.nom_cable AS nom,
        c.image_cable AS image,
        c.id_type_prise
    FROM
        cable c
    WHERE
        c.id_cable = %s
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    if not article:
        return redirect('/client/index')

    sql_declinaisons = '''
    SELECT
        dc.id_declinaison_cable AS id_declinaison,
        dc.prix_declinaison AS prix,
        dc.stock,
        coul.nom_couleur AS couleur,
        lg.nom_longueur AS longueur,
        coul.id_couleur,
        lg.id_longueur
    FROM
        declinaison_cable dc
    JOIN
        couleur coul ON dc.id_couleur = coul.id_couleur
    JOIN
        longueur lg ON dc.id_longueur = lg.id_longueur
    WHERE
        dc.id_cable = %s
    ORDER BY
        coul.nom_couleur, lg.nom_longueur
    '''
    mycursor.execute(sql_declinaisons, (id_article,))
    declinaisons = mycursor.fetchall()

    selected_declinaison = None
    if selected_couleur and selected_longueur:
        selected_couleur = int(selected_couleur)
        selected_longueur = int(selected_longueur)

        sql_selected_declinaison = '''
        SELECT
            dc.id_declinaison_cable AS id_declinaison,
            dc.prix_declinaison AS prix,
            dc.stock,
            coul.nom_couleur AS couleur,
            lg.nom_longueur AS longueur,
            coul.id_couleur,
            lg.id_longueur
        FROM
            declinaison_cable dc
        JOIN
            couleur coul ON dc.id_couleur = coul.id_couleur
        JOIN
            longueur lg ON dc.id_longueur = lg.id_longueur
        WHERE
            dc.id_cable = %s
            AND dc.id_couleur = %s
            AND dc.id_longueur = %s
        LIMIT 1
        '''
        mycursor.execute(sql_selected_declinaison, (id_article, selected_couleur, selected_longueur))
        selected_declinaison = mycursor.fetchone()

    return render_template(
        'client/boutique/declinaison_article.html',
        article=article,
        declinaisons=declinaisons,
        selected_couleur=selected_couleur,
        selected_longueur=selected_longueur,
        selected_declinaison=selected_declinaison
    )


@client_article.route('/client/index')
@client_article.route('/client/article/show')
def client_article_show():
    mycursor = get_db().cursor()
    id_client = session.get('id_user')

    if not id_client:
        return "Utilisateur non connecté", 401

    filter_word = session.get('filter_word', None)
    filter_prix_min = session.get('filter_prix_min', None)
    filter_prix_max = session.get('filter_prix_max', None)
    filter_types = session.get('filter_types', None)

    sql = '''
    SELECT
        c.id_cable AS id_article,
        c.nom_cable AS nom,
        c.image_cable AS image,
        MIN(dc.prix_declinaison) AS prix,
        SUM(dc.stock) AS stock_total,
        COUNT(dc.id_declinaison_cable) AS nb_declinaisons,
        c.id_type_prise,
        (SELECT COUNT(*) FROM commentaire WHERE id_cable = c.id_cable) AS nb_commentaires,
        (SELECT AVG(note) FROM note WHERE id_cable = c.id_cable) AS note_moyenne,
        (SELECT COUNT(*) FROM liste_envie WHERE cable_id = c.id_cable AND utilisateur_id = %s) AS liste_envie
    FROM
        cable c
    JOIN
        declinaison_cable dc ON c.id_cable = dc.id_cable
    WHERE
        1=1
    '''
    params = [id_client]

    if filter_word:
        sql += " AND c.nom_cable LIKE %s"
        params.append(f"%{filter_word}%")

    if filter_prix_min:
        sql += " AND dc.prix_declinaison >= %s"
        params.append(filter_prix_min)

    if filter_prix_max:
        sql += " AND dc.prix_declinaison <= %s"
        params.append(filter_prix_max)

    if filter_types:
        sql += " AND c.id_type_prise IN (%s)" % ",".join(["%s"] * len(filter_types))
        params.extend(filter_types)

    sql += " GROUP BY c.id_cable, c.nom_cable, c.image_cable, c.id_type_prise"
    sql += " ORDER BY c.nom_cable;"
    mycursor.execute(sql, params)
    articles = mycursor.fetchall()

    sql_types = '''
    SELECT id_type_prise AS id_type_article,
           nom_type_prise AS libelle
    FROM type_prise
    ORDER BY libelle;
    '''
    mycursor.execute(sql_types)
    types_article = mycursor.fetchall()

    sql_panier = '''
    SELECT 
        c.nom_cable AS nom_article, 
        dc.prix_declinaison AS prix, 
        dc.stock AS stock, 
        lp.quantite AS quantite, 
        dc.id_declinaison_cable AS id_declinaison_article,
        coul.nom_couleur AS libelle_couleur, 
        lg.nom_longueur AS libelle_taille, 
        coul.id_couleur AS id_couleur, 
        lg.id_longueur AS id_taille,
        (dc.prix_declinaison * lp.quantite) AS sous_total
    FROM declinaison_cable AS dc
    JOIN cable AS c ON dc.id_cable = c.id_cable
    JOIN ligne_panier AS lp ON dc.id_declinaison_cable = lp.id_declinaison_cable
    JOIN couleur AS coul ON dc.id_couleur = coul.id_couleur
    JOIN longueur AS lg ON dc.id_longueur = lg.id_longueur
    WHERE lp.id_utilisateur = %s;
    '''
    mycursor.execute(sql_panier, (id_client,))
    articles_panier = mycursor.fetchall()

    sql_prix_total = '''
    SELECT COALESCE(SUM(dc.prix_declinaison * lp.quantite), 0) AS prix_total
    FROM ligne_panier lp
    JOIN declinaison_cable dc ON lp.id_declinaison_cable = dc.id_declinaison_cable
    WHERE lp.id_utilisateur = %s;
    '''
    mycursor.execute(sql_prix_total, (id_client,))
    prix_total = mycursor.fetchone()['prix_total']

    return render_template(
        'client/boutique/panier_article.html',
        articles=articles,
        articles_panier=articles_panier,
        prix_total=prix_total,
        items_filtre=types_article
    )


@client_article.route('/client/article/details')
def client_article_details():
    id_article = request.args.get('id_article', type=int)
    if id_article is None:
        return redirect('/client/index')

    mycursor = get_db().cursor()
    id_client = session.get('id_user')

    if not id_client:
        return redirect('/client/index')

    # Ajouter l'article à l'historique
    client_historique_add(id_article, id_client)

    sql = '''
    SELECT
    c.id_cable AS id_article,
    c.nom_cable AS nom,
    c.description_cable AS description,
    c.blindage,
    c.fournisseur,
    c.image_cable AS image,
    tp.nom_type_prise AS type_prise,
    MIN(dc.prix_declinaison) AS prix_min,
    MAX(dc.prix_declinaison) AS prix_max,
    SUM(dc.stock) AS stock_total,
    COUNT(dc.id_declinaison_cable) AS nb_declinaisons,
    (SELECT AVG(note) FROM note WHERE id_cable = c.id_cable) AS note_moyenne,
    (SELECT COUNT(*) FROM note WHERE id_cable = c.id_cable) AS nb_notes,
    (SELECT COUNT(*) FROM liste_envie WHERE cable_id = c.id_cable AND utilisateur_id = %s) AS liste_envie
    FROM
        cable c
    JOIN
        type_prise tp ON c.id_type_prise = tp.id_type_prise
    JOIN
        declinaison_cable dc ON c.id_cable = dc.id_cable
    WHERE
        c.id_cable = %s
    GROUP BY
        c.id_cable, c.nom_cable, c.description_cable, c.blindage, c.fournisseur, c.image_cable, tp.nom_type_prise
    '''
    mycursor.execute(sql, (id_client, id_article))
    article = mycursor.fetchone()

    if not article:
        return redirect('/client/index')

    sql_commentaires = '''
    SELECT
        com.id_commentaire,
        com.commentaire,
        com.date_publication,
        com.id_cable as id_article,
        com.valider,
        u.login AS nom_utilisateur,
        u.id_utilisateur,
        com.id_commentaire_parent
    FROM
        commentaire com
    JOIN
        utilisateur u ON com.id_utilisateur = u.id_utilisateur
    WHERE
        com.id_cable = %s AND (com.valider = 1 OR com.id_utilisateur = %s)
    ORDER BY
        CASE 
            WHEN com.id_commentaire_parent IS NULL THEN com.date_publication
            ELSE (SELECT parent.date_publication FROM commentaire parent WHERE parent.id_commentaire = com.id_commentaire_parent)
        END DESC,
        CASE
            WHEN com.id_commentaire_parent IS NULL THEN 0
            ELSE 1
        END,
        com.date_publication ASC
    '''
    mycursor.execute(sql_commentaires, (id_article, id_client))
    commentaires = mycursor.fetchall()

    sql_note_user = '''
    SELECT note
    FROM note
    WHERE id_cable = %s AND id_utilisateur = %s
    '''
    mycursor.execute(sql_note_user, (id_article, id_client))
    note_user = mycursor.fetchone()

    sql_commandes = '''
    SELECT 
        COUNT(DISTINCT c.id_commande) AS nb_commandes_article
    FROM 
        commande c
    JOIN 
        ligne_commande lc ON c.id_commande = lc.id_commande
    JOIN 
        declinaison_cable dc ON lc.id_declinaison_cable = dc.id_declinaison_cable
    WHERE 
        c.id_utilisateur = %s AND dc.id_cable = %s
    '''
    mycursor.execute(sql_commandes, (id_client, id_article))
    commandes_articles = mycursor.fetchone()

    if not commandes_articles:
        commandes_articles = {'nb_commandes_article': 0}

    sql_nb_commentaires = '''
    SELECT 
        COUNT(*) AS nb_commentaires_total,
        SUM(CASE WHEN valider = 1 THEN 1 ELSE 0 END) AS nb_commentaires_total_valide,
        (SELECT COUNT(*) FROM commentaire WHERE id_cable = %s AND id_utilisateur = %s) AS nb_commentaires_utilisateur,
        (SELECT COUNT(*) FROM commentaire WHERE id_cable = %s AND id_utilisateur = %s AND valider = 1) AS nb_commentaires_utilisateur_valide
    FROM 
        commentaire
    WHERE 
        id_cable = %s
    '''
    mycursor.execute(sql_nb_commentaires, (id_article, id_client, id_article, id_client, id_article))
    nb_commentaires = mycursor.fetchone()

    if not nb_commentaires:
        nb_commentaires = {
            'nb_commentaires_total': 0,
            'nb_commentaires_total_valide': 0,
            'nb_commentaires_utilisateur': 0,
            'nb_commentaires_utilisateur_valide': 0
        }

    return render_template(
        'client/article_info/article_details.html',
        article=article,
        commentaires=commentaires,
        note=note_user,
        commandes_articles=commandes_articles,
        nb_commentaires=nb_commentaires
    )
