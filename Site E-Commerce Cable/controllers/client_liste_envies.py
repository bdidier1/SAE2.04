#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session, g

from connexion_db import get_db

client_liste_envies = Blueprint('client_liste_envies', __name__,
                                template_folder='templates')


@client_liste_envies.route('/client/envie/add', methods=['get'])
def client_liste_envies_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    # Vérifier si l'article est déjà dans la liste d'envies
    sql = '''SELECT COUNT(*) AS nb_article FROM liste_envie 
             WHERE utilisateur_id = %s AND cable_id = %s'''
    mycursor.execute(sql, (id_client, id_article))
    result = mycursor.fetchone()

    if result['nb_article'] > 0:
        # Si l'article est déjà dans la liste d'envies, on le supprime
        sql = '''DELETE FROM liste_envie 
                 WHERE utilisateur_id = %s AND cable_id = %s'''
        mycursor.execute(sql, (id_client, id_article))
    else:
        # Sinon, on l'ajoute avec la date actuelle
        sql = '''INSERT INTO liste_envie (utilisateur_id, cable_id, date_update) 
                 VALUES (%s, %s, NOW())'''
        mycursor.execute(sql, (id_client, id_article))

    get_db().commit()
    return redirect('/client/article/show')


@client_liste_envies.route('/client/envie/delete', methods=['get'])
def client_liste_envies_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    # Supprimer l'article de la liste d'envies
    sql = '''DELETE FROM liste_envie 
             WHERE utilisateur_id = %s AND cable_id = %s'''
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()

    return redirect('/client/envies/show')


@client_liste_envies.route('/client/envies/show', methods=['get'])
def client_liste_envies_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Récupérer les articles de la liste d'envies triés par date d'ajout décroissante
    sql = '''
    SELECT 
        c.id_cable AS id_article,
        c.nom_cable AS nom,
        c.image_cable AS image,
        MIN(dc.prix_declinaison) AS prix,
        SUM(dc.stock) AS stock,
        COUNT(dc.id_declinaison_cable) AS nb_declinaisons,
        le.date_update,
        c.id_type_prise
    FROM 
        liste_envie le
    JOIN 
        cable c ON le.cable_id = c.id_cable
    JOIN 
        declinaison_cable dc ON c.id_cable = dc.id_cable
    WHERE 
        le.utilisateur_id = %s
    GROUP BY 
        c.id_cable, c.nom_cable, c.image_cable, le.date_update, c.id_type_prise
    ORDER BY 
        le.date_update DESC
    '''
    mycursor.execute(sql, (id_client,))
    articles_liste_envies = mycursor.fetchall()

    # Récupérer le nombre d'articles dans la liste d'envies
    sql = '''
    SELECT COUNT(*) AS nb_liste_envies 
    FROM liste_envie 
    WHERE utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_client,))
    nb_liste_envies = mycursor.fetchone()['nb_liste_envies']

    # Récupérer les articles de l'historique (limité à 6 articles)
    sql = '''
    SELECT 
        c.id_cable AS id_article,
        c.nom_cable AS nom,
        c.image_cable AS image,
        MIN(dc.prix_declinaison) AS prix,
        h.date_consultation
    FROM 
        historique h
    JOIN 
        cable c ON h.cable_id = c.id_cable
    JOIN 
        declinaison_cable dc ON c.id_cable = dc.id_cable
    WHERE 
        h.utilisateur_id = %s
    GROUP BY 
        c.id_cable, c.nom_cable, c.image_cable, h.date_consultation
    ORDER BY 
        h.date_consultation DESC
    LIMIT 6
    '''
    mycursor.execute(sql, (id_client,))
    articles_historique = mycursor.fetchall()

    # Récupérer le nombre d'articles dans l'historique
    sql = '''
    SELECT COUNT(DISTINCT cable_id) AS nb_liste_historique 
    FROM historique 
    WHERE utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_client,))
    nb_liste_historique = mycursor.fetchone()['nb_liste_historique']

    # Récupérer les informations supplémentaires si un article est sélectionné
    id_article_detail = request.args.get('id_article_detail_wishlist', None)
    info_wishlist = None
    info_wishlist_categorie = None

    if id_article_detail:
        # Nombre d'autres clients ayant cet article dans leur wishlist
        sql = '''
        SELECT 
            c.nom_cable AS nom,
            COUNT(DISTINCT le.utilisateur_id) AS nb_wish_list_other
        FROM 
            liste_envie le
        JOIN 
            cable c ON le.cable_id = c.id_cable
        WHERE 
            le.cable_id = %s AND le.utilisateur_id != %s
        GROUP BY 
            c.nom_cable
        '''
        mycursor.execute(sql, (id_article_detail, id_client))
        info_wishlist = mycursor.fetchone()
        if not info_wishlist:
            info_wishlist = {'nom': '', 'nb_wish_list_other': 0}

            # Récupérer le nom de l'article
            sql = '''SELECT nom_cable AS nom FROM cable WHERE id_cable = %s'''
            mycursor.execute(sql, (id_article_detail,))
            nom_article = mycursor.fetchone()
            if nom_article:
                info_wishlist['nom'] = nom_article['nom']

        # Nombre d'articles de la même catégorie dans la wishlist du client
        sql = '''
        SELECT 
            tp.nom_type_prise AS libelle,
            COUNT(DISTINCT le2.cable_id) AS nb_wish_list_other_categorie
        FROM 
            cable c
        JOIN 
            type_prise tp ON c.id_type_prise = tp.id_type_prise
        JOIN 
            liste_envie le ON c.id_cable = %s
        LEFT JOIN 
            liste_envie le2 ON le2.utilisateur_id = %s AND le2.cable_id != %s
        LEFT JOIN 
            cable c2 ON le2.cable_id = c2.id_cable AND c2.id_type_prise = c.id_type_prise
        WHERE 
            c.id_cable = %s
        GROUP BY 
            tp.nom_type_prise
        '''
        mycursor.execute(sql, (id_article_detail, id_client, id_article_detail, id_article_detail))
        info_wishlist_categorie = mycursor.fetchone()
        if not info_wishlist_categorie:
            info_wishlist_categorie = {'libelle': '', 'nb_wish_list_other_categorie': 0}

            # Récupérer le libellé de la catégorie
            sql = '''
            SELECT tp.nom_type_prise AS libelle 
            FROM cable c 
            JOIN type_prise tp ON c.id_type_prise = tp.id_type_prise 
            WHERE c.id_cable = %s
            '''
            mycursor.execute(sql, (id_article_detail,))
            categorie = mycursor.fetchone()
            if categorie:
                info_wishlist_categorie['libelle'] = categorie['libelle']

    return render_template('client/liste_envies/liste_envies_show.html',
                           articles_liste_envies=articles_liste_envies,
                           articles_historique=articles_historique,
                           nb_liste_envies=nb_liste_envies,
                           nb_liste_historique=nb_liste_historique,
                           info_wishlist=info_wishlist,
                           info_wishlist_categorie=info_wishlist_categorie
                           )


def client_historique_add(article_id, client_id):
    mycursor = get_db().cursor()

    # Rechercher si l'article pour cet utilisateur est dans l'historique
    sql = '''SELECT * FROM historique 
             WHERE utilisateur_id = %s AND cable_id = %s
             ORDER BY date_consultation DESC'''
    mycursor.execute(sql, (client_id, article_id))
    historique_produit = mycursor.fetchall()

    # Si l'article est déjà dans l'historique, on met à jour la date de consultation
    if historique_produit:
        sql = '''UPDATE historique 
                 SET date_consultation = NOW() 
                 WHERE utilisateur_id = %s AND cable_id = %s AND date_consultation = %s'''
        mycursor.execute(sql, (client_id, article_id, historique_produit[0]['date_consultation']))
    else:
        # Sinon, on l'ajoute à l'historique
        sql = '''INSERT INTO historique (utilisateur_id, cable_id, date_consultation) 
                 VALUES (%s, %s, NOW())'''
        mycursor.execute(sql, (client_id, article_id))

    # Limiter l'historique à 6 articles différents maximum
    sql = '''
    SELECT cable_id, date_consultation 
    FROM historique 
    WHERE utilisateur_id = %s 
    ORDER BY date_consultation DESC
    '''
    mycursor.execute(sql, (client_id,))
    historiques = mycursor.fetchall()

    # Récupérer les articles distincts
    articles_distincts = []
    articles_ids = set()

    for historique in historiques:
        if historique['cable_id'] not in articles_ids:
            articles_distincts.append(historique)
            articles_ids.add(historique['cable_id'])

    # Si plus de 6 articles distincts, supprimer les plus anciens
    if len(articles_distincts) > 6:
        for i in range(6, len(articles_distincts)):
            sql = '''DELETE FROM historique 
                     WHERE utilisateur_id = %s AND cable_id = %s AND date_consultation = %s'''
            mycursor.execute(sql,
                             (client_id, articles_distincts[i]['cable_id'], articles_distincts[i]['date_consultation']))

    # Supprimer les articles de l'historique datant de plus d'un mois
    sql = '''DELETE FROM historique 
             WHERE utilisateur_id = %s AND date_consultation < DATE_SUB(NOW(), INTERVAL 1 MONTH)'''
    mycursor.execute(sql, (client_id,))

    get_db().commit()


@client_liste_envies.route('/client/envies/up', methods=['get'])
def client_liste_envies_article_up():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    # Récupérer les articles de la liste d'envies triés par date d'ajout décroissante
    sql = '''
    SELECT cable_id, date_update 
    FROM liste_envie 
    WHERE utilisateur_id = %s 
    ORDER BY date_update DESC
    '''
    mycursor.execute(sql, (id_client,))
    articles = mycursor.fetchall()

    # Trouver l'article à déplacer et l'article précédent
    for i in range(len(articles)):
        if str(articles[i]['cable_id']) == str(id_article) and i > 0:
            # Obtenir une date légèrement supérieure à celle de l'article précédent
            sql = '''
            UPDATE liste_envie 
            SET date_update = (SELECT DATE_ADD(%s, INTERVAL 1 SECOND))
            WHERE utilisateur_id = %s AND cable_id = %s
            '''
            mycursor.execute(sql, (articles[i - 1]['date_update'], id_client, id_article))
            get_db().commit()
            break

    return redirect('/client/envies/show')


@client_liste_envies.route('/client/envies/down', methods=['get'])
def client_liste_envies_article_down():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    # Récupérer les articles de la liste d'envies triés par date d'ajout décroissante
    sql = '''
    SELECT cable_id, date_update 
    FROM liste_envie 
    WHERE utilisateur_id = %s 
    ORDER BY date_update DESC
    '''
    mycursor.execute(sql, (id_client,))
    articles = mycursor.fetchall()

    # Trouver l'article à déplacer et l'article suivant
    for i in range(len(articles) - 1):
        if str(articles[i]['cable_id']) == str(id_article):
            # Obtenir une date légèrement inférieure à celle de l'article suivant
            sql = '''
            UPDATE liste_envie 
            SET date_update = (SELECT DATE_SUB(%s, INTERVAL 1 SECOND))
            WHERE utilisateur_id = %s AND cable_id = %s
            '''
            mycursor.execute(sql, (articles[i + 1]['date_update'], id_client, id_article))
            get_db().commit()
            break

    return redirect('/client/envies/show')


@client_liste_envies.route('/client/envies/last', methods=['get'])
def client_liste_envies_article_last():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    # Mettre à jour la date de l'article pour qu'il soit en dernier (date la plus ancienne)
    sql = '''
    UPDATE liste_envie 
    SET date_update = (
        SELECT MIN(date_update) - INTERVAL 1 SECOND 
        FROM (SELECT date_update FROM liste_envie WHERE utilisateur_id = %s) AS dates
    )
    WHERE utilisateur_id = %s AND cable_id = %s
    '''
    mycursor.execute(sql, (id_client, id_client, id_article))
    get_db().commit()

    return redirect('/client/envies/show')


@client_liste_envies.route('/client/envies/first', methods=['get'])
def client_liste_envies_article_first():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    # Mettre à jour la date de l'article pour qu'il soit en premier (date la plus récente)
    sql = '''
    UPDATE liste_envie 
    SET date_update = NOW()
    WHERE utilisateur_id = %s AND cable_id = %s
    '''
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()

    return redirect('/client/envies/show')