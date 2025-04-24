#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, Flask, request, render_template, redirect, abort, flash, session, g
from connexion_db import get_db

client_commentaire = Blueprint('client_commentaire', __name__, template_folder='templates')


@client_commentaire.route('/client/article/details', methods=['GET'])
def client_article_details():
    id_article = request.args.get('id_article', type=int)
    if id_article is None:
        abort(404, "Article non trouvé")
        
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Récupérer les détails de l'article
    sql_article = '''
    SELECT 
        c.id_cable AS id_article,
        c.nom_cable AS nom,
        c.image_cable AS image,
        dc.prix_declinaison AS prix,
        dc.stock AS stock,
        c.id_type_prise,
        (SELECT AVG(note) FROM note WHERE id_cable = c.id_cable) AS note_moyenne,
        (SELECT COUNT(*) FROM note WHERE id_cable = c.id_cable) AS nb_notes
    FROM cable c
    JOIN declinaison_cable dc ON c.id_cable = dc.id_cable
    WHERE c.id_cable = %s;
    '''
    mycursor.execute(sql_article, (id_article,))
    article = mycursor.fetchone()

    if article is None:
        abort(404, "Article non trouvé")

    # S'assurer que note_moyenne est un float
    if article['note_moyenne'] is not None:
        article['note_moyenne'] = float(article['note_moyenne'])

    # Récupérer les commentaires de l'article
    sql_commentaires = '''
    SELECT 
        com.id_commentaire,
        com.id_cable AS id_article,
        com.id_utilisateur,
        com.commentaire,
        com.date_publication,
        com.valider,
        com.id_commentaire_parent,
        u.nom AS nom_utilisateur,
        u.login
    FROM commentaire com
    JOIN utilisateur u ON com.id_utilisateur = u.id_utilisateur
    WHERE com.id_cable = %s
    ORDER BY 
        CASE 
            WHEN com.id_commentaire_parent IS NULL THEN 0
            ELSE 1
        END,
        CASE WHEN com.id_utilisateur = 1 THEN 1 ELSE 0 END,
        com.date_publication DESC;
    '''
    mycursor.execute(sql_commentaires, (id_article,))
    commentaires = mycursor.fetchall()

    # Récupérer les commandes de l'utilisateur pour cet article
    sql_commandes_articles = '''
    SELECT 
        COUNT(DISTINCT lc.id_commande) AS nb_commandes_article
    FROM ligne_commande lc
    JOIN declinaison_cable dc ON lc.id_declinaison_cable = dc.id_declinaison_cable
    JOIN cable c ON dc.id_cable = c.id_cable
    JOIN commande cmd ON lc.id_commande = cmd.id_commande
    WHERE cmd.id_utilisateur = %s AND c.id_cable = %s;
    '''
    mycursor.execute(sql_commandes_articles, (id_client, id_article))
    commandes_articles = mycursor.fetchone()

    # Récupérer la note de l'utilisateur pour cet article
    sql_note = '''
    SELECT note
    FROM note
    WHERE id_utilisateur = %s AND id_cable = %s;
    '''
    mycursor.execute(sql_note, (id_client, id_article))
    note = mycursor.fetchone()
    note = int(note['note']) if note else None

    # Récupérer les statistiques des commentaires
    sql_nb_commentaires = '''
    SELECT 
        COUNT(*) AS nb_commentaires_total,
        SUM(CASE WHEN valider = 1 THEN 1 ELSE 0 END) AS nb_commentaires_total_valide,
        (SELECT COUNT(*) FROM commentaire WHERE id_utilisateur = %s AND id_cable = %s) AS nb_commentaires_utilisateur,
        (SELECT COUNT(*) FROM commentaire WHERE id_utilisateur = %s AND id_cable = %s AND valider = 1) AS nb_commentaires_utilisateur_valide
    FROM commentaire
    WHERE id_cable = %s;
    '''
    mycursor.execute(sql_nb_commentaires, (id_client, id_article, id_client, id_article, id_article))
    nb_commentaires = mycursor.fetchone()

    return render_template('client/article_info/article_details.html',
                           article=article,
                           commentaires=commentaires,
                           commandes_articles=commandes_articles,
                           note=note,
                           nb_commentaires=nb_commentaires)


@client_commentaire.route('/client/commentaire/add', methods=['POST'])
def client_commentaire_add():
    mycursor = get_db().cursor()
    commentaire = request.form.get('commentaire', None)
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)

    if not commentaire or len(commentaire) < 3:
        flash(u'Le commentaire doit contenir au moins 3 caractères.', 'alert-warning')
        return redirect(f'/client/article/details?id_article={id_article}')

    # Vérifier si l'utilisateur a acheté l'article
    sql_check_achat = '''
    SELECT COUNT(DISTINCT lc.id_commande) AS nb_commandes
    FROM ligne_commande lc
    JOIN declinaison_cable dc ON lc.id_declinaison_cable = dc.id_declinaison_cable
    JOIN cable c ON dc.id_cable = c.id_cable
    JOIN commande cmd ON lc.id_commande = cmd.id_commande
    WHERE cmd.id_utilisateur = %s AND c.id_cable = %s;
    '''
    mycursor.execute(sql_check_achat, (id_client, id_article))
    result = mycursor.fetchone()

    if not result or result['nb_commandes'] == 0:
        flash(u'Vous devez avoir acheté cet article pour pouvoir le commenter.', 'alert-warning')
        return redirect(f'/client/article/details?id_article={id_article}')

    # Vérifier si l'utilisateur a déjà atteint le quota de 3 commentaires pour cet article
    sql_check_quota = '''
    SELECT COUNT(*) AS nb_commentaires
    FROM commentaire
    WHERE id_utilisateur = %s AND id_cable = %s;
    '''
    mycursor.execute(sql_check_quota, (id_client, id_article))
    result = mycursor.fetchone()

    if result and result['nb_commentaires'] >= 3:
        flash(u'Vous avez atteint le quota de 3 commentaires pour cet article.', 'alert-danger')
        return redirect(f'/client/article/details?id_article={id_article}')

    sql_insert_commentaire = '''
    INSERT INTO commentaire (commentaire, id_utilisateur, id_cable, date_publication, valider)
    VALUES (%s, %s, %s, NOW(), 0);
    '''
    mycursor.execute(sql_insert_commentaire, (commentaire, id_client, id_article))
    get_db().commit()

    flash(u'Commentaire ajouté avec succès.', 'alert-success')
    return redirect(f'/client/article/details?id_article={id_article}')


@client_commentaire.route('/client/commentaire/delete', methods=['POST'])
def client_commentaire_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    id_commentaire = request.form.get('id_commentaire', None)

    # Vérifier que le commentaire existe et appartient à l'utilisateur
    sql_check = '''
    SELECT COUNT(*) AS nb_commentaires
    FROM commentaire
    WHERE id_commentaire = %s AND id_utilisateur = %s;
    '''
    mycursor.execute(sql_check, (id_commentaire, id_client))
    result = mycursor.fetchone()

    if not result or result['nb_commentaires'] == 0:
        flash(u'Ce commentaire n\'existe pas ou ne vous appartient pas.', 'alert-warning')
        return redirect(f'/client/article/details?id_article={id_article}')

    sql_delete_commentaire = '''
    DELETE FROM commentaire
    WHERE id_commentaire = %s AND id_utilisateur = %s;
    '''
    mycursor.execute(sql_delete_commentaire, (id_commentaire, id_client))
    get_db().commit()

    flash(u'Commentaire supprimé avec succès.', 'alert-success')
    return redirect(f'/client/article/details?id_article={id_article}')


@client_commentaire.route('/client/note/add', methods=['POST'])
def client_note_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)

    if not note:
        flash(u'Veuillez sélectionner une note.', 'alert-warning')
        return redirect(f'/client/article/details?id_article={id_article}')

    # Vérifier si l'utilisateur a acheté l'article
    sql_check_achat = '''
    SELECT COUNT(DISTINCT lc.id_commande) AS nb_commandes
    FROM ligne_commande lc
    JOIN declinaison_cable dc ON lc.id_declinaison_cable = dc.id_declinaison_cable
    JOIN cable c ON dc.id_cable = c.id_cable
    JOIN commande cmd ON lc.id_commande = cmd.id_commande
    WHERE cmd.id_utilisateur = %s AND c.id_cable = %s;
    '''
    mycursor.execute(sql_check_achat, (id_client, id_article))
    result = mycursor.fetchone()

    if not result or result['nb_commandes'] == 0:
        flash(u'Vous devez avoir acheté cet article pour pouvoir le noter.', 'alert-warning')
        return redirect(f'/client/article/details?id_article={id_article}')

    sql_insert_note = '''
    INSERT INTO note (note, id_utilisateur, id_cable)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE note = %s;
    '''
    mycursor.execute(sql_insert_note, (note, id_client, id_article, note))
    get_db().commit()

    flash(u'Note ajoutée avec succès.', 'alert-success')
    return redirect(f'/client/article/details?id_article={id_article}')


@client_commentaire.route('/client/note/delete', methods=['POST'])
def client_note_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)

    print(f"Tentative de suppression de note - id_client: {id_client}, id_article: {id_article}")

    # Vérifier que l'utilisateur a bien une note pour cet article
    sql_check = '''
    SELECT COUNT(*) AS nb_notes 
    FROM note 
    WHERE id_utilisateur = %s AND id_cable = %s;
    '''
    mycursor.execute(sql_check, (id_client, id_article))
    result = mycursor.fetchone()

    if not result or result['nb_notes'] == 0:
        flash(u'Vous n\'avez pas de note pour cet article.', 'alert-warning')
        return redirect(f'/client/article/details?id_article={id_article}')

    sql_delete_note = '''
    DELETE FROM note
    WHERE id_utilisateur = %s AND id_cable = %s;
    '''
    mycursor.execute(sql_delete_note, (id_client, id_article))
    get_db().commit()

    flash(u'Note supprimée avec succès.', 'alert-success')
    return redirect(f'/client/article/details?id_article={id_article}')


@client_commentaire.route('/client/note/edit', methods=['POST'])
def client_note_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)

    if not note:
        flash(u'Veuillez sélectionner une note.', 'alert-warning')
        return redirect(f'/client/article/details?id_article={id_article}')

    # Vérifier si l'utilisateur a acheté l'article
    sql_check_achat = '''
    SELECT COUNT(DISTINCT lc.id_commande) AS nb_commandes
    FROM ligne_commande lc
    JOIN declinaison_cable dc ON lc.id_declinaison_cable = dc.id_declinaison_cable
    JOIN cable c ON dc.id_cable = c.id_cable
    JOIN commande cmd ON lc.id_commande = cmd.id_commande
    WHERE cmd.id_utilisateur = %s AND c.id_cable = %s;
    '''
    mycursor.execute(sql_check_achat, (id_client, id_article))
    result = mycursor.fetchone()

    if not result or result['nb_commandes'] == 0:
        flash(u'Vous devez avoir acheté cet article pour pouvoir le noter.', 'alert-warning')
        return redirect(f'/client/article/details?id_article={id_article}')

    sql_update_note = '''
    UPDATE note
    SET note = %s
    WHERE id_utilisateur = %s AND id_cable = %s;
    '''
    mycursor.execute(sql_update_note, (note, id_client, id_article))
    get_db().commit()

    flash(u'Note modifiée avec succès.', 'alert-success')
    return redirect(f'/client/article/details?id_article={id_article}')