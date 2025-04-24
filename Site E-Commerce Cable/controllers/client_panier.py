#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, abort, flash, session
from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__, template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session.get('id_user')

    if not id_client:
        return redirect('/client/login')

    id_declinaison = request.form.get('id_declinaison_article', None)
    quantite = int(request.form.get('quantite', 1))

    if not id_declinaison:
        flash('Veuillez sélectionner une déclinaison', 'danger')
        return redirect('/client/article/show')

    # Vérifier le stock disponible
    sql_check_stock = '''
    SELECT stock FROM declinaison_cable 
    WHERE id_declinaison_cable = %s
    '''
    mycursor.execute(sql_check_stock, (id_declinaison,))
    result = mycursor.fetchone()

    if not result or result['stock'] < quantite:
        flash('Stock insuffisant pour cette déclinaison', 'danger')
        return redirect(request.referrer or '/client/article/show')

    # Vérifier si l'article est déjà dans le panier
    sql_check_panier = '''
    SELECT quantite FROM ligne_panier 
    WHERE id_utilisateur = %s AND id_declinaison_cable = %s
    '''
    mycursor.execute(sql_check_panier, (id_client, id_declinaison))
    panier_item = mycursor.fetchone()

    # Mettre à jour la base de données
    if panier_item:
        # Mettre à jour la quantité si l'article est déjà dans le panier
        nouvelle_quantite = panier_item['quantite'] + quantite

        # Vérifier si la nouvelle quantité est disponible en stock
        if nouvelle_quantite > result['stock'] + panier_item['quantite']:
            flash('Stock insuffisant pour cette quantité', 'danger')
            return redirect(request.referrer or '/client/article/show')

        sql_update_panier = '''
        UPDATE ligne_panier 
        SET quantite = %s 
        WHERE id_utilisateur = %s AND id_declinaison_cable = %s
        '''
        mycursor.execute(sql_update_panier, (nouvelle_quantite, id_client, id_declinaison))
    else:
        # Ajouter l'article au panier s'il n'y est pas déjà
        sql_add_panier = '''
        INSERT INTO ligne_panier (id_utilisateur, id_declinaison_cable, quantite) 
        VALUES (%s, %s, %s)
        '''
        mycursor.execute(sql_add_panier, (id_client, id_declinaison, quantite))

    # Mettre à jour le stock
    sql_update_stock = '''
    UPDATE declinaison_cable 
    SET stock = stock - %s 
    WHERE id_declinaison_cable = %s
    '''
    mycursor.execute(sql_update_stock, (quantite, id_declinaison))

    get_db().commit()
    flash('Article ajouté au panier avec succès', 'success')

    return redirect('/client/article/show')

@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_article = request.form.get('id_declinaison_article')

    sql_get_quantite = '''
    SELECT quantite 
    FROM ligne_panier 
    WHERE id_utilisateur = %s AND id_declinaison_cable = %s;
    '''
    mycursor.execute(sql_get_quantite, (id_client, id_declinaison_article))
    quantite_info = mycursor.fetchone()

    if not quantite_info:
        flash("Article non trouvé dans le panier.", "error")
        return redirect(request.referrer or '/client/article/show')

    quantite = quantite_info['quantite']

    if quantite > 1:
        sql_update_panier = '''
        UPDATE ligne_panier 
        SET quantite = quantite - 1 
        WHERE id_utilisateur = %s AND id_declinaison_cable = %s;
        '''
        quantite_to_restore = 1
    else:
        sql_update_panier = '''
        DELETE FROM ligne_panier 
        WHERE id_utilisateur = %s AND id_declinaison_cable = %s;
        '''
        quantite_to_restore = quantite

    mycursor.execute(sql_update_panier, (id_client, id_declinaison_article))

    sql_restore_stock = '''
    UPDATE declinaison_cable 
    SET stock = stock + %s 
    WHERE id_declinaison_cable = %s;
    '''
    mycursor.execute(sql_restore_stock, (quantite_to_restore, id_declinaison_article))

    get_db().commit()
    flash("Article retiré du panier.", "success")
    return redirect(request.referrer or '/client/article/show')

@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Mettre à jour le stock en une seule requête SQL
    sql_restore_stock = '''
    UPDATE declinaison_cable dc
    JOIN ligne_panier lp ON dc.id_declinaison_cable = lp.id_declinaison_cable
    SET dc.stock = dc.stock + lp.quantite
    WHERE lp.id_utilisateur = %s;
    '''
    mycursor.execute(sql_restore_stock, (id_client,))

    # Supprimer toutes les lignes du panier en une seule requête
    sql_delete_panier = '''
    DELETE FROM ligne_panier 
    WHERE id_utilisateur = %s;
    '''
    mycursor.execute(sql_delete_panier, (id_client,))

    get_db().commit()
    flash("Panier vidé avec succès.", "success")
    return redirect('/client/article/show')

@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_article = request.form.get('id_declinaison_article')

    sql_get_quantite = '''
    SELECT quantite 
    FROM ligne_panier 
    WHERE id_utilisateur = %s AND id_declinaison_cable = %s;
    '''
    mycursor.execute(sql_get_quantite, (id_client, id_declinaison_article))
    quantite_info = mycursor.fetchone()

    if not quantite_info:
        flash("Article non trouvé dans le panier.", "error")
        return redirect(request.referrer or '/client/article/show')

    quantite = quantite_info['quantite']

    sql_delete_panier = '''
    DELETE FROM ligne_panier 
    WHERE id_utilisateur = %s AND id_declinaison_cable = %s;
    '''
    mycursor.execute(sql_delete_panier, (id_client, id_declinaison_article))

    sql_restore_stock = '''
    UPDATE declinaison_cable 
    SET stock = stock + %s 
    WHERE id_declinaison_cable = %s;
    '''
    mycursor.execute(sql_restore_stock, (quantite, id_declinaison_article))

    get_db().commit()
    flash("Article supprimé du panier.", "success")
    return redirect(request.referrer or '/client/article/show')

@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    """
    Filtrer les articles du panier
    """
    filter_word = request.form.get('filter_word', '')
    filter_prix_min = request.form.get('filter_prix_min', '')
    filter_prix_max = request.form.get('filter_prix_max', '')
    filter_types = request.form.getlist('filter_types')

    session_filter = {}

    if filter_word or filter_prix_min or filter_prix_max or filter_types:
        if filter_word:
            if len(filter_word) > 1 and filter_word.isalpha():
                session_filter['filter_word'] = filter_word
                flash(f"Votre mot recherché est : {filter_word}")
            else:
                if len(filter_word) == 1:
                    flash('Le mot doit contenir au moins 2 lettres')
                elif not filter_word.isalpha():
                    flash('Le mot doit être composé de lettres uniquement')
        else:
            session_filter.pop('filter_word', None)

        if filter_prix_min or filter_prix_max:
            if filter_prix_min and filter_prix_max:
                if filter_prix_min.isdecimal() and filter_prix_max.isdecimal():
                    if int(filter_prix_min) > int(filter_prix_max):
                        flash("Le prix minimum doit être inférieur au prix maximum")
                    else:
                        session_filter['filter_prix_min'] = filter_prix_min
                        session_filter['filter_prix_max'] = filter_prix_max
                        flash(f"Votre prix minimum est : {filter_prix_min} et votre prix maximum est : {filter_prix_max}")
                else:
                    flash('Les prix doivent être des nombres entiers')
            elif filter_prix_min:
                if filter_prix_min.isdecimal():
                    session_filter['filter_prix_min'] = filter_prix_min
                    flash(f"Votre prix minimum est : {filter_prix_min}")
                else:
                    flash('Le prix minimum doit être un nombre entier')
            elif filter_prix_max:
                if filter_prix_max.isdecimal():
                    session_filter['filter_prix_max'] = filter_prix_max
                    flash(f"Votre prix maximum est : {filter_prix_max}")
                else:
                    flash('Le prix maximum doit être un nombre entier')
        else:
            session_filter.pop('filter_prix_min', None)
            session_filter.pop('filter_prix_max', None)

        if filter_types:
            session_filter['filter_types'] = filter_types
            flash(f"Votre type d'article est : {filter_types}")
        else:
            session_filter.pop('filter_types', None)

    session.update(session_filter)

    return redirect('/client/article/show')

@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    """
    Supprimer les filtres appliqués
    """
    session.pop('filter_word', None)
    session.pop('filter_types', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    flash("Les filtres ont été supprimés")
    return redirect('/client/article/show')