#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_commentaire = Blueprint('admin_commentaire', __name__,
                              template_folder='templates')


@admin_commentaire.route('/admin/article/commentaires', methods=['GET'])
def admin_article_commentaires():
    id_article = request.args.get('id_article', type=int)
    if id_article is None:
        abort(404, "Article non trouvé")
        
    mycursor = get_db().cursor()

    sql = '''
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
            WHEN com.id_commentaire_parent IS NULL THEN com.date_publication
            ELSE (SELECT parent.date_publication FROM commentaire parent WHERE parent.id_commentaire = com.id_commentaire_parent)
        END DESC,
        CASE
            WHEN com.id_commentaire_parent IS NULL THEN 0
            ELSE 1
        END,
        com.date_publication ASC;
    '''
    mycursor.execute(sql, (id_article,))
    commentaires = mycursor.fetchall()

    sql = '''
    SELECT 
        c.id_cable AS id_article,
        c.nom_cable AS nom,
        c.image_cable AS image,
        (SELECT CAST(AVG(note) AS DECIMAL(10,2)) FROM note WHERE id_cable = c.id_cable) AS note_moyenne,
        (SELECT COUNT(*) FROM note WHERE id_cable = c.id_cable) AS nb_notes
    FROM cable c
    WHERE c.id_cable = %s;
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    # S'assurer que note_moyenne est un float
    if article and article['note_moyenne'] is not None:
        article['note_moyenne'] = float(article['note_moyenne'])

    sql = '''
    SELECT 
        COUNT(*) AS nb_commentaires_total,
        SUM(CASE WHEN valider = 1 THEN 1 ELSE 0 END) AS nb_commentaires_valider
    FROM commentaire
    WHERE id_cable = %s;
    '''
    mycursor.execute(sql, (id_article,))
    nb_commentaires = mycursor.fetchone()

    return render_template('admin/article/show_article_commentaires.html',
                           commentaires=commentaires,
                           article=article,
                           nb_commentaires=nb_commentaires
                           )


@admin_commentaire.route('/admin/article/commentaires/delete', methods=['POST'])
def admin_commentaire_delete():
    mycursor = get_db().cursor()
    id_commentaire = request.form.get('id_commentaire', None)
    id_article = request.form.get('id_article', None)

    # Vérifier que le commentaire existe
    sql_check = '''
    SELECT COUNT(*) AS nb_commentaires
    FROM commentaire
    WHERE id_commentaire = %s;
    '''
    mycursor.execute(sql_check, (id_commentaire,))
    result = mycursor.fetchone()

    if not result or result['nb_commentaires'] == 0:
        flash(u'Ce commentaire n\'existe pas.', 'alert-warning')
        return redirect(f'/admin/article/commentaires?id_article={id_article}')

    sql = '''
    DELETE FROM commentaire
    WHERE id_commentaire = %s;
    '''
    mycursor.execute(sql, (id_commentaire,))
    get_db().commit()

    flash(u'Commentaire supprimé avec succès.', 'alert-success')
    return redirect(f'/admin/article/commentaires?id_article={id_article}')


@admin_commentaire.route('/admin/article/commentaires/repondre', methods=['GET'])
def admin_repondre_commentaire():
    id_utilisateur = request.args.get('id_utilisateur', None)
    id_article = request.args.get('id_article', None)
    id_commentaire = request.args.get('id_commentaire', None)
    date_publication = request.args.get('date_publication', None)
    return render_template('admin/article/add_commentaire.html',
                           id_utilisateur=id_utilisateur,
                           id_article=id_article,
                           id_commentaire=id_commentaire,
                           date_publication=date_publication)


@admin_commentaire.route('/admin/article/commentaires/add', methods=['POST'])
def admin_add_commentaire():
    mycursor = get_db().cursor()
    id_utilisateur = session['id_user']  # 1 admin
    id_article = request.form.get('id_article', None)
    id_commentaire_parent = request.form.get('id_commentaire_parent', None)
    commentaire = request.form.get('commentaire', None)

    sql = '''
    INSERT INTO commentaire (id_utilisateur, id_cable, date_publication, commentaire, valider, id_commentaire_parent)
    VALUES (%s, %s, NOW(), %s, 1, %s);
    '''
    mycursor.execute(sql, (id_utilisateur, id_article, commentaire, id_commentaire_parent))
    get_db().commit()

    flash(u'Réponse ajoutée avec succès.', 'alert-success')
    return redirect(f'/admin/article/commentaires?id_article={id_article}')


@admin_commentaire.route('/admin/article/commentaires/valider', methods=['GET'])
def admin_comment_valider():
    id_article = request.args.get('id_article', type=int)
    if id_article is None:
        abort(404, "Article non trouvé")
        
    mycursor = get_db().cursor()

    sql = '''
    UPDATE commentaire
    SET valider = 1
    WHERE id_cable = %s AND valider = 0;
    '''
    mycursor.execute(sql, (id_article,))
    get_db().commit()

    flash(u'Commentaires validés avec succès.', 'alert-success')
    return redirect(f'/admin/article/commentaires?id_article={id_article}')


@admin_commentaire.route('/admin/article/commentaire/valider', methods=['GET'])
def admin_comment_valider_individuel():
    id_commentaire = request.args.get('id_commentaire', type=int)
    id_article = request.args.get('id_article', type=int)
    if id_commentaire is None or id_article is None:
        abort(404, "Commentaire ou article non trouvé")
        
    mycursor = get_db().cursor()

    sql = '''
    UPDATE commentaire
    SET valider = 1
    WHERE id_commentaire = %s;
    '''
    mycursor.execute(sql, (id_commentaire,))
    get_db().commit()

    flash(u'Commentaire validé avec succès.', 'alert-success')
    return redirect(f'/admin/article/commentaires?id_article={id_article}')


@admin_commentaire.route('/admin/article/show', methods=['GET'])
def admin_article_show():
    mycursor = get_db().cursor()

    sql = '''
    SELECT 
        c.id_cable AS id_article,
        c.nom_cable AS nom,
        c.image_cable AS image,
        MIN(dc.prix_declinaison) AS prix,
        SUM(dc.stock) AS stock_total,
        COUNT(dc.id_declinaison_cable) AS nb_declinaisons,
        c.id_type_prise,
        (SELECT COUNT(*) FROM commentaire WHERE id_cable = c.id_cable) AS nb_commentaires_total,
        (SELECT COUNT(*) FROM commentaire WHERE id_cable = c.id_cable AND valider = 0) AS nb_commentaires_non_valides,
        (SELECT COUNT(*) FROM commentaire WHERE id_cable = c.id_cable AND valider = 1) AS nb_commentaires_valides
    FROM
        cable c
    JOIN
        declinaison_cable dc ON c.id_cable = dc.id_cable
    GROUP BY c.id_cable, c.nom_cable, c.image_cable, c.id_type_prise
    ORDER BY c.nom_cable;
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()

    return render_template('admin/article/show_article.html',
                           articles=articles)