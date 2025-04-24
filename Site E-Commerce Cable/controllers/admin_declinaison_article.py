#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_article = Blueprint('admin_declinaison_article', __name__,
                                      template_folder='templates')

@admin_declinaison_article.route('/admin/declinaison_article/add')
def add_declinaison_article():
    """Affiche le formulaire pour ajouter une déclinaison d'article."""
    id_article = request.args.get('id_article')

    if not id_article:
        flash(u"ID article manquant.", 'alert-danger')
        return redirect('/admin/article')

    mycursor = get_db().cursor()
    
    # Récupérer l'article et vérifier son existence
    sql_article = "SELECT * FROM cable WHERE id_cable = %s"
    mycursor.execute(sql_article, (id_article,))
    article = mycursor.fetchone()

    if not article:
        flash(u"Article non trouvé.", 'alert-danger')
        mycursor.close()
        return redirect('/admin/article')

    # Récupérer les couleurs disponibles
    sql_couleurs = """
        SELECT DISTINCT c.id_couleur, c.nom_couleur AS libelle
        FROM couleur c
        LEFT JOIN declinaison_cable dc ON c.id_couleur = dc.id_couleur AND dc.id_cable = %s
        ORDER BY c.nom_couleur
    """
    mycursor.execute(sql_couleurs, (id_article,))
    couleurs = mycursor.fetchall()

    # Récupérer les tailles disponibles
    sql_tailles = """
        SELECT DISTINCT l.id_longueur, l.nom_longueur AS libelle
        FROM longueur l
        LEFT JOIN declinaison_cable dc ON l.id_longueur = dc.id_longueur AND dc.id_cable = %s
        ORDER BY l.nom_longueur
    """
    mycursor.execute(sql_tailles, (id_article,))
    tailles = mycursor.fetchall()

    mycursor.close()
    return render_template('admin/article/add_declinaison_article.html',
                           article=article,
                           couleurs=couleurs,
                           tailles=tailles)

@admin_declinaison_article.route('/admin/declinaison_article/add', methods=['POST'])
def valid_add_declinaison_article():
    """Valide l'ajout d'une nouvelle déclinaison d'article."""
    mycursor = get_db().cursor()
    
    id_article = request.form.get('id_article', '')
    stock = request.form.get('stock', '')
    taille = request.form.get('taille', '')
    couleur = request.form.get('couleur', '')
    prix = request.form.get('prix_declinaison', '')

    if not id_article or not stock or not taille or not couleur or not prix:
        flash(u"Tous les champs sont obligatoires.", 'alert-danger')
        mycursor.close()
        return redirect(f'/admin/article/edit?id_article={id_article}')

    # Vérification de l'existence d'une déclinaison similaire
    sql_check = """
        SELECT COUNT(*) as nb_declinaisons
        FROM declinaison_cable
        WHERE id_cable = %s AND id_longueur = %s AND id_couleur = %s
    """
    mycursor.execute(sql_check, (id_article, taille, couleur))
    result = mycursor.fetchone()
    
    if result and result['nb_declinaisons'] > 0:
        flash(u'Cette déclinaison existe déjà.', 'alert-warning')
        mycursor.close()
        return redirect(f'/admin/article/edit?id_article={id_article}')

    # Insertion de la nouvelle déclinaison
    sql_insert = """
        INSERT INTO declinaison_cable (id_cable, stock, id_longueur, id_couleur, prix_declinaison)
        VALUES (%s, %s, %s, %s, %s)
    """
    mycursor.execute(sql_insert, (id_article, stock, taille, couleur, prix))
    get_db().commit()
    
    flash(u'Déclinaison ajoutée avec succès !', 'alert-success')
    mycursor.close()
    return redirect(f'/admin/article/edit?id_article={id_article}')

@admin_declinaison_article.route('/admin/declinaison_article/edit')
def edit_declinaison_article():
    """Affiche le formulaire pour éditer une déclinaison d'article."""
    id_article = request.args.get('id_article')
    id_declinaison_article = request.args.get('id_declinaison_article')

    if not id_article or not id_declinaison_article:
        flash(u"ID article ou déclinaison manquant.", 'alert-danger')
        return redirect('/admin/article')

    mycursor = get_db().cursor()

    # Récupérer l'article et la déclinaison en une seule requête
    sql = """
        SELECT c.*, dc.*
        FROM cable c
        JOIN declinaison_cable dc ON c.id_cable = dc.id_cable
        WHERE c.id_cable = %s AND dc.id_declinaison_cable = %s
    """
    mycursor.execute(sql, (id_article, id_declinaison_article))
    result = mycursor.fetchone()

    if not result:
        flash(u"Article ou déclinaison non trouvé.", 'alert-danger')
        mycursor.close()
        return redirect('/admin/article')

    # Récupérer toutes les couleurs et tailles
    sql_couleurs = "SELECT id_couleur, nom_couleur AS libelle FROM couleur ORDER BY nom_couleur"
    sql_tailles = "SELECT id_longueur, nom_longueur AS libelle FROM longueur ORDER BY nom_longueur"
    
    mycursor.execute(sql_couleurs)
    couleurs = mycursor.fetchall()
    
    mycursor.execute(sql_tailles)
    tailles = mycursor.fetchall()

    mycursor.close()
    return render_template('admin/article/edit_declinaison_article.html',
                           article=result,
                           declinaison_article=result,
                           couleurs=couleurs,
                           tailles=tailles)

@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['POST'])
def valid_edit_declinaison_article():
    """Valide la modification d'une déclinaison d'article."""
    mycursor = get_db().cursor()
    
    id_declinaison_article = request.form.get('id_declinaison_article', '')
    id_article = request.form.get('id_article', '')
    stock = request.form.get('stock', '')
    taille_id = request.form.get('id_taille', '')
    couleur_id = request.form.get('id_couleur', '')
    prix = request.form.get('prix_declinaison', '')

    if not all([id_declinaison_article, id_article, stock, taille_id, couleur_id, prix]):
        flash(u"Tous les champs sont obligatoires.", 'alert-danger')
        mycursor.close()
        return redirect(f'/admin/article/edit?id_article={id_article}')

    # Vérifier les doublons
    sql_check = """
        SELECT COUNT(*) as nb_declinaisons
        FROM declinaison_cable
        WHERE id_cable = %s 
        AND id_longueur = %s 
        AND id_couleur = %s 
        AND id_declinaison_cable != %s
    """
    mycursor.execute(sql_check, (id_article, taille_id, couleur_id, id_declinaison_article))
    result = mycursor.fetchone()

    if result and result['nb_declinaisons'] > 0:
        flash(u'Une déclinaison avec cette combinaison existe déjà.', 'alert-warning')
        mycursor.close()
        return redirect(f'/admin/article/edit?id_article={id_article}')

    # Mise à jour de la déclinaison
    sql_update = """
        UPDATE declinaison_cable
        SET id_longueur = %s, 
            id_couleur = %s, 
            stock = %s, 
            prix_declinaison = %s
        WHERE id_declinaison_cable = %s
    """
    mycursor.execute(sql_update, (taille_id, couleur_id, stock, prix, id_declinaison_article))
    get_db().commit()
    
    flash(u'Déclinaison modifiée avec succès.', 'alert-success')
    mycursor.close()
    return redirect(f'/admin/article/edit?id_article={id_article}')

@admin_declinaison_article.route('/admin/declinaison_article/delete')
def admin_delete_declinaison_article():
    """Supprime une déclinaison d'article."""
    id_declinaison_article = request.args.get('id_declinaison_article')
    id_article = request.args.get('id_article')

    if not id_declinaison_article or not id_article:
        flash(u"ID déclinaison ou article manquant.", 'alert-danger')
        return redirect('/admin/article')

    mycursor = get_db().cursor()

    # Supprimer les lignes de commande et la déclinaison en une transaction
    sql_delete = """
        DELETE lc, dc
        FROM declinaison_cable dc
        LEFT JOIN ligne_commande lc ON dc.id_declinaison_cable = lc.id_declinaison_cable
        WHERE dc.id_declinaison_cable = %s
    """
    mycursor.execute(sql_delete, (id_declinaison_article,))
    get_db().commit()

    flash(u'Déclinaison supprimée avec succès.', 'alert-success')
    mycursor.close()
    return redirect(f'/admin/article/edit?id_article={id_article}')
