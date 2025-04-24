#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint, request, render_template, redirect, flash
from connexion_db import get_db

admin_article = Blueprint('admin_article', __name__, template_folder='templates')


@admin_article.route('/admin/article/show')
def show_article():
    mycursor = get_db().cursor()
    sql = '''
    SELECT 
        c.id_cable AS id_article,
        c.nom_cable AS nom,
        c.image_cable AS image,
        c.prix_cable AS prix,
        t.nom_type_prise AS libelle,
        c.id_type_prise,
        COUNT(dc.id_declinaison_cable) AS nb_declinaisons,
        SUM(dc.stock) AS stock,
        (SELECT MIN(dc2.stock) FROM declinaison_cable dc2 WHERE dc2.id_cable = c.id_cable) AS min_stock
    FROM 
        cable c
    LEFT JOIN 
        declinaison_cable dc ON c.id_cable = dc.id_cable
    JOIN 
        type_prise t ON c.id_type_prise = t.id_type_prise 
    GROUP BY 
        c.id_cable, c.nom_cable, c.image_cable, c.prix_cable, t.nom_type_prise, c.id_type_prise;
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()

    # Récupérer les informations sur les commentaires pour chaque article
    for article in articles:
        sql_commentaires = '''
        SELECT 
            COUNT(*) AS nb_commentaires_total,
            SUM(CASE WHEN valider = 1 THEN 1 ELSE 0 END) AS nb_commentaires_valides,
            SUM(CASE WHEN valider = 0 THEN 1 ELSE 0 END) AS nb_commentaires_non_valides
        FROM commentaire
        WHERE id_cable = %s;
        '''
        mycursor.execute(sql_commentaires, (article['id_article'],))
        commentaires_info = mycursor.fetchone()

        # Initialiser les valeurs par défaut à 0
        article['nb_commentaires_total'] = 0
        article['nb_commentaires_valides'] = 0
        article['nb_commentaires_non_valides'] = 0

        if commentaires_info:
            # Vérifier que les valeurs ne sont pas NULL et les convertir en entiers
            article['nb_commentaires_total'] = int(commentaires_info['nb_commentaires_total'] or 0)
            article['nb_commentaires_valides'] = int(commentaires_info['nb_commentaires_valides'] or 0)
            article['nb_commentaires_non_valides'] = int(commentaires_info['nb_commentaires_non_valides'] or 0)

    return render_template('admin/article/show_article.html', articles=articles)


@admin_article.route('/admin/article/add', methods=['GET'])
def add_article():
    mycursor = get_db().cursor()

    # Récupérer les types d'articles
    sql_types = '''SELECT id_type_prise AS id_type_article, nom_type_prise AS libelle FROM type_prise'''
    mycursor.execute(sql_types)
    types_article = mycursor.fetchall()

    # Récupérer les longueurs
    sql_longueurs = '''SELECT id_longueur, nom_longueur FROM longueur'''
    mycursor.execute(sql_longueurs)
    longueurs = mycursor.fetchall()

    # Récupérer les couleurs
    sql_couleurs = '''SELECT id_couleur, nom_couleur FROM couleur'''
    mycursor.execute(sql_couleurs)
    couleurs = mycursor.fetchall()

    return render_template('admin/article/add_article.html',
                           types_article=types_article,
                           longueurs=longueurs,
                           couleurs=couleurs)


@admin_article.route('/admin/article/add', methods=['POST'])
def valid_add_article():
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')
    longueur_id = request.form.get('longueur_id', '')
    couleur_id = request.form.get('couleur_id', '')
    stock = request.form.get('stock', 0)

    if not longueur_id or not couleur_id:
        flash('Veuillez sélectionner une longueur et une couleur.', 'alert-danger')
        return redirect('/admin/article/add')

    if image:
        filename = 'img_upload' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        filename = None

    sql = ''' 
    INSERT INTO declinaison_cable (stock, prix_declinaison, image, id_longueur, id_couleur, id_cable)
    VALUES (%s, %s, %s, %s, %s, %s)
    '''
    tuple_add = (stock, prix, filename, longueur_id, couleur_id, type_article_id)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    flash(f'Article ajouté avec succès : {nom} - {type_article_id} - {prix} - {description}', 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/delete', methods=['GET'])
def delete_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()

    sql = '''SELECT COUNT(*) AS nb_declinaison FROM declinaison_cable WHERE id_cable = %s'''
    mycursor.execute(sql, (id_article,))
    nb_declinaison = mycursor.fetchone()

    if nb_declinaison['nb_declinaison'] > 0:
        flash('Il y a des déclinaisons pour cet article : vous ne pouvez pas le supprimer', 'alert-warning')
    else:
        sql = '''SELECT image_cable FROM cable WHERE id_cable = %s'''
        mycursor.execute(sql, (id_article,))
        article = mycursor.fetchone()

        if article and article['image_cable']:
            image = article['image_cable']
            image_path = os.path.join('static/images/', image)
            if os.path.exists(image_path):
                os.remove(image_path)

        sql = '''DELETE FROM cable WHERE id_cable = %s'''
        mycursor.execute(sql, (id_article,))
        get_db().commit()

        flash(f'Article supprimé, ID : {id_article}', 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()

    # Récupérer les informations de l'article principal
    sql_article = '''
    SELECT 
        c.id_cable AS id_article,
        c.nom_cable AS nom,
        c.image_cable AS image,
        c.prix_cable AS prix,
        t.nom_type_prise AS libelle,
        SUM(dc.stock) AS stock,
        c.id_type_prise AS type_article_id,
        c.description_cable AS description
    FROM 
        cable c
    JOIN 
        type_prise t ON c.id_type_prise = t.id_type_prise
    JOIN 
        declinaison_cable dc ON c.id_cable = dc.id_cable
    WHERE 
        c.id_cable = %s;
    '''
    mycursor.execute(sql_article, (id_article,))
    article = mycursor.fetchone()

    # Récupérer les déclinaisons de l'article
    sql_declinaisons = '''
    SELECT 
        dc.id_declinaison_cable AS id_declinaison_article,
        l.nom_longueur AS libelle_taille,
        co.nom_couleur AS libelle_couleur,
        dc.stock AS stock,
        dc.id_cable AS article_id
    FROM 
        declinaison_cable dc
    LEFT JOIN 
        longueur l ON dc.id_longueur = l.id_longueur
    LEFT JOIN 
        couleur co ON dc.id_couleur = co.id_couleur
    WHERE 
        dc.id_cable = %s;
    '''
    mycursor.execute(sql_declinaisons, (id_article,))
    declinaisons_article = mycursor.fetchall()

    # Récupérer les longueurs disponibles
    sql_longueurs = '''SELECT id_longueur, nom_longueur FROM longueur'''
    mycursor.execute(sql_longueurs)
    longueurs = mycursor.fetchall()

    # Récupérer les couleurs disponibles
    sql_couleurs = '''SELECT id_couleur, nom_couleur FROM couleur'''
    mycursor.execute(sql_couleurs)
    couleurs = mycursor.fetchall()

    # Récupérer les types d'articles disponibles
    sql_types = '''SELECT id_type_prise AS id_type_article, nom_type_prise AS libelle FROM type_prise'''
    mycursor.execute(sql_types)
    types_article = mycursor.fetchall()

    return render_template('admin/article/edit_article.html',
                           article=article,
                           declinaisons_article=declinaisons_article,
                           longueurs=longueurs,
                           couleurs=couleurs,
                           types_article=types_article)


@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()

    # Récupérer les données du formulaire
    id_article = request.form.get('id_article')
    nom = request.form.get('nom')
    type_article_id = request.form.get('type_article_id')
    prix = request.form.get('prix')
    description = request.form.get('description')
    image = request.files.get('image', '')
    id_longueur = request.form.get('id_longueur')
    id_couleur = request.form.get('id_couleur')
    stock = request.form.get('stock')

    # Vérifier que les champs obligatoires sont remplis
    if not id_longueur or not id_couleur:
        flash("Les champs 'Longueur' et 'Couleur' doivent être remplis.", 'alert-warning')
        return redirect('/admin/article/edit?id_article=' + id_article)

    # Récupérer l'ancienne image (si elle existe)
    sql = '''SELECT image_cable FROM cable WHERE id_cable = %s'''
    mycursor.execute(sql, (id_article,))
    result = mycursor.fetchone()
    image_nom = result['image_cable'] if result else None

    # Gestion de l'image
    if image:
        # Supprimer l'ancienne image si elle existe
        if image_nom and os.path.exists(os.path.join('static/images/', image_nom)):
            os.remove(os.path.join('static/images/', image_nom))

        # Enregistrer la nouvelle image
        filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
        image_nom = filename

    # Mettre à jour les informations de l'article principal dans la table `cable`
    sql_update_cable = '''
    UPDATE cable 
    SET nom_cable = %s, image_cable = %s, prix_cable = %s, id_type_prise = %s, description_cable = %s 
    WHERE id_cable = %s
    '''
    mycursor.execute(sql_update_cable, (nom, image_nom, prix, type_article_id, description, id_article))

    # Vérifier si une déclinaison avec la même longueur et couleur existe déjà
    sql_check_declinaison = '''
    SELECT id_declinaison_cable 
    FROM declinaison_cable 
    WHERE id_cable = %s AND id_longueur = %s AND id_couleur = %s;
    '''
    mycursor.execute(sql_check_declinaison, (id_article, id_longueur, id_couleur))
    existing_declinaison = mycursor.fetchone()

    if existing_declinaison:
        # Mettre à jour la déclinaison existante
        sql_update_declinaison = '''
        UPDATE declinaison_cable 
        SET prix_declinaison = %s, stock = %s 
        WHERE id_declinaison_cable = %s;
        '''
        mycursor.execute(sql_update_declinaison, (prix, stock, existing_declinaison['id_declinaison_cable']))

    # Valider les modifications dans la base de données
    get_db().commit()

    # Afficher un message de succès et rediriger
    flash(f'Article modifié avec succès : {nom} - {type_article_id} - {prix} - {description}', 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/avis', methods=['GET'])
def admin_avis():
    id = request.args.get('id', type=int)
    mycursor = get_db().cursor()
    article = []
    commentaires = {}
    return render_template('admin/article/show_avis.html',
                           article=article,
                           commentaires=commentaires)


@admin_article.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    article_id = request.form.get('idArticle', None)
    userId = request.form.get('idUser', None)
    return redirect(f'/admin/article/avis?id={article_id}')