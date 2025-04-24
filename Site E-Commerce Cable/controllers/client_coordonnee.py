#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash, session
from connexion_db import get_db

client_coordonnee = Blueprint('client_coordonnee', __name__, template_folder='templates')

@client_coordonnee.route('/client/coordonnee/show')
def client_coordonnee_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql_utilisateur = '''
    SELECT login, nom, email 
    FROM utilisateur 
    WHERE id_utilisateur = %s;
    '''
    mycursor.execute(sql_utilisateur, (id_client,))
    utilisateur = mycursor.fetchone()

    sql_adresses = '''
    SELECT 
        a.*, 
        COUNT(DISTINCT c.id_commande) AS nbr_commandes,
        a.est_favorite,
        a.est_valide
    FROM adresse a
    LEFT JOIN commande c ON a.id_adresse = c.adresse_id_livr OR a.id_adresse = c.adresse_id_fact
    WHERE a.id_utilisateur = %s
    GROUP BY a.id_adresse;
    '''
    mycursor.execute(sql_adresses, (id_client,))
    adresses = mycursor.fetchall()


    sql_count_valid_adresses = '''
    SELECT COUNT(*) AS nb_adresses
    FROM adresse
    WHERE id_utilisateur = %s AND est_valide = 1;
    '''
    mycursor.execute(sql_count_valid_adresses, (id_client,))
    nb_adresses = mycursor.fetchone()['nb_adresses']


    sql_count_total_adresses = '''
    SELECT COUNT(*) AS nb_adresses_tot
    FROM adresse
    WHERE id_utilisateur = %s;
    '''
    mycursor.execute(sql_count_total_adresses, (id_client,))
    nb_adresses_tot = mycursor.fetchone()['nb_adresses_tot']

    return render_template('client/coordonnee/show_coordonnee.html',
                           utilisateur=utilisateur,
                           adresses=adresses,
                           nb_adresses=nb_adresses,
                           nb_adresses_tot=nb_adresses_tot)

@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_coordonnee_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']


    sql_utilisateur = '''
    SELECT * 
    FROM utilisateur 
    WHERE id_utilisateur = %s;
    '''
    mycursor.execute(sql_utilisateur, (id_client,))
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/edit_coordonnee.html',
                           utilisateur=utilisateur)

@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_coordonnee_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')


    sql_check = '''
    SELECT * 
    FROM utilisateur 
    WHERE (email = %s OR login = %s) AND id_utilisateur != %s;
    '''
    mycursor.execute(sql_check, (email, login, id_client))
    utilisateur = mycursor.fetchone()

    if utilisateur:
        flash(u'Cet Email ou ce Login existe déjà pour un autre utilisateur', 'alert-warning')
        return redirect('/client/coordonnee/edit')


    sql_update = '''
    UPDATE utilisateur 
    SET nom = %s, login = %s, email = %s 
    WHERE id_utilisateur = %s;
    '''
    mycursor.execute(sql_update, (nom, login, email, id_client))
    get_db().commit()

    flash(u'Vos informations ont été mises à jour avec succès', 'alert-success')
    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/delete_adresse', methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.form.get('id_adresse')

    # Vérifier si l'adresse est utilisée dans des commandes
    sql_check_usage = '''
    SELECT COUNT(*) AS usage_count
    FROM commande
    WHERE (adresse_id_livr = %s OR adresse_id_fact = %s);
    '''
    mycursor.execute(sql_check_usage, (id_adresse, id_adresse))
    usage_count = mycursor.fetchone()['usage_count']

    if usage_count > 0:
        # Si l'adresse est utilisée, la marquer comme non valide
        sql_update = '''
        UPDATE adresse 
        SET est_valide = 0
        WHERE id_adresse = %s AND id_utilisateur = %s;
        '''
        mycursor.execute(sql_update, (id_adresse, id_client))
        flash(u'Adresse marquée comme non valide car elle a été utilisée dans des commandes', 'alert-warning')
    else:
        # Si l'adresse n'est pas utilisée, la supprimer
        sql_delete = '''
        DELETE FROM adresse 
        WHERE id_adresse = %s AND id_utilisateur = %s;
        '''
        mycursor.execute(sql_delete, (id_adresse, id_client))
        flash(u'Adresse supprimée avec succès', 'alert-success')

    # Si l'adresse supprimée était favorite, définir une nouvelle adresse favorite
    sql_check_favorite = '''
    SELECT COUNT(*) AS has_favorite
    FROM adresse
    WHERE id_utilisateur = %s AND est_favorite = 1 AND est_valide = 1;
    '''
    mycursor.execute(sql_check_favorite, (id_client,))
    has_favorite = mycursor.fetchone()['has_favorite'] > 0

    if not has_favorite:
        # Trouver la dernière adresse utilisée valide
        sql_set_new_favorite = '''
        UPDATE adresse a
        SET est_favorite = 1
        WHERE a.id_adresse = (
            SELECT c.adresse_id_livr
            FROM commande c
            JOIN adresse a2 ON c.adresse_id_livr = a2.id_adresse
            WHERE c.id_utilisateur = %s AND a2.est_valide = 1
            ORDER BY c.date_achat DESC
            LIMIT 1
        );
        '''
        mycursor.execute(sql_set_new_favorite, (id_client,))

    get_db().commit()
    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/add_adresse')
def client_coordonnee_add_adresse():
    id_client = session.get('id_user')
    mycursor = get_db().cursor()


    sql_user = '''
    SELECT nom, login 
    FROM utilisateur 
    WHERE id_utilisateur = %s;
    '''
    mycursor.execute(sql_user, (id_client,))
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/add_adresse.html', utilisateur=utilisateur)

@client_coordonnee.route('/client/coordonnee/add_adresse', methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    nom_adresse = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')

    # Vérification du code postal
    if not code_postal.isdigit() or len(code_postal) != 5:
        flash(u'Le code postal doit contenir exactement 5 chiffres', 'alert-warning')
        return render_template('client/coordonnee/add_adresse.html',
                             utilisateur={'nom': nom_adresse, 'login': session.get('login')},
                             adresse={'nom_client': nom_adresse, 'rue': rue, 'code_postal': code_postal, 'ville': ville})

    # Vérification du nombre d'adresses valides
    sql_count_valid = '''
    SELECT COUNT(*) AS nb_adresses
    FROM adresse
    WHERE id_utilisateur = %s AND est_valide = 1;
    '''
    mycursor.execute(sql_count_valid, (id_client,))
    nb_adresses = mycursor.fetchone()['nb_adresses']

    if nb_adresses >= 4:
        flash(u'Vous avez atteint la limite de 4 adresses valides', 'alert-warning')
        return redirect('/client/coordonnee/show')

    # Vérifier s'il y a déjà une adresse favorite
    sql_check_favorite = '''
    SELECT COUNT(*) AS has_favorite
    FROM adresse
    WHERE id_utilisateur = %s AND est_favorite = 1;
    '''
    mycursor.execute(sql_check_favorite, (id_client,))
    has_favorite = mycursor.fetchone()['has_favorite'] > 0

    # Insérer la nouvelle adresse
    sql_insert = '''
    INSERT INTO adresse (nom_client, rue, code_postal, ville, id_utilisateur, est_favorite, est_valide)
    VALUES (%s, %s, %s, %s, %s, %s, 1);
    '''
    mycursor.execute(sql_insert, (nom_adresse, rue, code_postal, ville, id_client, not has_favorite))
    get_db().commit()

    flash(u'Adresse ajoutée avec succès', 'alert-success')
    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/edit_adresse', methods=['GET'])
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.args.get('id_adresse')


    sql_adresse = '''
    SELECT * 
    FROM adresse 
    WHERE id_adresse = %s AND id_utilisateur = %s;
    '''
    mycursor.execute(sql_adresse, (id_adresse, id_client))
    adresse = mycursor.fetchone()

    if not adresse:
        flash(u"Adresse non trouvée ou vous n'avez pas l'autorisation de la modifier", 'alert-danger')
        return redirect('/client/coordonnee/show')


    sql_user = '''
    SELECT nom, login 
    FROM utilisateur 
    WHERE id_utilisateur = %s;
    '''
    mycursor.execute(sql_user, (id_client,))
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/edit_adresse.html', adresse=adresse, utilisateur=utilisateur)

@client_coordonnee.route('/client/coordonnee/edit_adresse', methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    nom_client = request.form.get('nom_client', '').strip()
    rue = request.form.get('rue', '').strip()
    code_postal = request.form.get('code_postal', '').strip()
    ville = request.form.get('ville', '').strip()
    id_adresse = request.form.get('id_adresse')

    if not nom_client or not rue or not code_postal or not ville:
        flash(u'Information : Tous les champs doivent être remplis', 'alert-warning')
        return redirect('/client/coordonnee/edit_adresse?id_adresse=' + id_adresse)

    # Vérification du code postal
    if not code_postal.isdigit() or len(code_postal) != 5:
        flash(u'Le code postal doit contenir exactement 5 chiffres', 'alert-warning')
        return redirect('/client/coordonnee/edit_adresse?id_adresse=' + id_adresse)

    # Vérifier si l'adresse est utilisée dans des commandes
    sql_check_usage = '''
    SELECT COUNT(*) AS usage_count
    FROM commande
    WHERE (adresse_id_livr = %s OR adresse_id_fact = %s);
    '''
    mycursor.execute(sql_check_usage, (id_adresse, id_adresse))
    usage_count = mycursor.fetchone()['usage_count']

    if usage_count > 0:
        # Si l'adresse est utilisée, la marquer comme non valide
        sql_update_old = '''
        UPDATE adresse 
        SET est_valide = 0
        WHERE id_adresse = %s AND id_utilisateur = %s;
        '''
        mycursor.execute(sql_update_old, (id_adresse, id_client))

        # Créer une nouvelle adresse avec les nouvelles informations
        sql_insert_new = '''
        INSERT INTO adresse (nom_client, rue, code_postal, ville, id_utilisateur, est_favorite, est_valide)
        SELECT %s, %s, %s, %s, %s, est_favorite, 1
        FROM adresse
        WHERE id_adresse = %s;
        '''
        mycursor.execute(sql_insert_new, (nom_client, rue, code_postal, ville, id_client, id_adresse))
        flash(u'Adresse mise à jour avec succès (une nouvelle adresse a été créée car l\'ancienne était utilisée dans des commandes)', 'alert-success')
    else:
        # Si l'adresse n'est pas utilisée, la mettre à jour normalement
        sql_update = '''
        UPDATE adresse
        SET nom_client = %s, rue = %s, code_postal = %s, ville = %s
        WHERE id_adresse = %s AND id_utilisateur = %s;
        '''
        mycursor.execute(sql_update, (nom_client, rue, code_postal, ville, id_adresse, id_client))
        flash(u'Adresse mise à jour avec succès', 'alert-success')

    get_db().commit()
    return redirect('/client/coordonnee/show')