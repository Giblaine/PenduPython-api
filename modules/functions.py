#! /usr/bin/python
# -*- coding:utf-8 -*-

from modules import db
from flask import Response
import uuid
import json

def nouveauJeu(length):
    mot_id = nouveauMot(length)
    uuid = generationUUID()
    mot = getMot(mot_id)
    etat_mot = "_" * len(mot)

    # On stocke le nouveau jeu
    sauvegardeNouvellePartie(uuid, mot_id, 8, etat_mot, 0)

    # On créé le JSON
    data = {}
    data["uuid"] = uuid.__str__()
    data["mot_id"] = mot_id
    data["coup_restant"] = 8
    data["etat_mot"] = etat_mot
    data["statut"] = 0 # 0: EN COURS / 1: TERMINÉ
    jsonData = json.dumps(data)

    response = Response(response=jsonData, status=200, mimetype="application/json")

    return response

def getJeu(uuid):
    connection = db.connect()

    # On récupère un mot de la longueur souhaitée
    req = "SELECT * FROM jeu WHERE uuid = %s"

    try:
        cursor = connection.cursor()
        cursor.execute(req, uuid)
        return json.dumps(cursor.fetchone())

    finally:
        connection.close()

def nouveauMot(length):
    connection = db.connect()

    # On récupère un mot de la longueur souhaitée
    req = "SELECT * FROM mot WHERE RAND() > 0.9 AND longueur = %s ORDER BY RAND() LIMIT 1"

    try:
        cursor = connection.cursor()
        cursor.execute(req, length)
        return cursor.fetchone()['id']

    finally:
        connection.close()

def getMot(mot_id):
    connection = db.connect()

    # On récupère un mot de la longueur souhaitée
    req = "SELECT * FROM mot WHERE id = %s"

    try:
        cursor = connection.cursor()
        cursor.execute(req, mot_id)
        return cursor.fetchone()['mot']

    finally:
        connection.close()

def jouer(uuid, lettre):

    jeu = json.loads(getJeu(uuid))

    # On vérifie le statut du jeu
    if jeu['statut'] == 1:
        data = {}
        data["message"] = "La partie est terminée. Vous avez perdu :( Le mot était : " + getMot(jeu["mot_id"]) + "."
        data["code"] = 1000
        
        jsonData = json.dumps(data)
        response = Response(response=jsonData, status=200, mimetype="application/json")
        return response

    if jeu['statut'] == 2:
        data = {}
        data["message"] = "La partie est terminée. Vous avez gagné :) Le mot était : " + getMot(jeu["mot_id"]) + "."
        data["code"] = 1000
        jsonData = json.dumps(data)
        response = Response(response=jsonData, status=200, mimetype="application/json")
        return response 

    # On regarde si la lettre a déjà été proposée
    if getLettreTrouvee(uuid, lettre) > 0:
        data = {}
        data["message"] = "La lettre a déjà été proposée."
        data["code"] = 1001

        # On décrémente la partie
        decrementePartie(uuid)

        jsonData = json.dumps(data)
        response = Response(response=jsonData, status=200, mimetype="application/json")
        return response 

    mot = getMot(jeu['mot_id'])
    motSplit = list(mot)
    lettreTrouvee = False

    for char in motSplit:
        # On a trouvé la lettre
        if(lettre == char):
            addLettre(uuid, char)
            updateMot(uuid, char)
            lettreTrouvee = True
            break

    if lettreTrouvee == False:
        decrementePartie(uuid)
        jeu = json.loads(getJeu(uuid))

        if jeu['coup_restant'] == 0:
            data = {}
            data["message"] = "La partie est terminée. Vous avez perdu :( Le mot était : " + getMot(jeu["mot_id"]) + "."
            data["code"] = 1000
            jsonData = json.dumps(data)
            response = Response(response=jsonData, status=200, mimetype="application/json")
            return response 

        else:
            data = {}
            data["message"] = "Le mot ne contient pas la lettre proposée. Il vous reste " + str(jeu["coup_restant"]) + " essai(s) restant(s)"
            data["mot"] = jeu['etat_mot']
            data["code"] = 1002
            jsonData = json.dumps(data)
            response = Response(response=jsonData, status=200, mimetype="application/json")
            return response 

    else:
        jeu = json.loads(getJeu(uuid))

        print(jeu["etat_mot"].count("_"))
        print(jeu["coup_restant"])

        if jeu["etat_mot"].count('_') == 0:
            terminePartie(uuid, 2)
            data = {}
            data["message"] = "La partie est terminée. Vous avez gagné. Le mot était : " + jeu["etat_mot"] + "."
            data["code"] = 1000
            jsonData = json.dumps(data)
            response = Response(response=jsonData, status=200, mimetype="application/json")
            return response 

        else:
            data = {}
            data["message"] = "La lettre a bien été trouvée. Il vous reste " + str(jeu["coup_restant"]) + " essai(s) restant(s)"
            data["mot"] = jeu['etat_mot']
            data["code"] = 1003
            jsonData = json.dumps(data)
            response = Response(response=jsonData, status=200, mimetype="application/json")
            return response 

def addLettre(uuid, char):
    connection = db.connect()

    # On insert le nouveau jeu
    req = "INSERT INTO lettre_trouve(uuid, lettre) VALUES(%s, %s)"

    try:
        cursor = connection.cursor()
        cursor.execute(req, (uuid, char))
        connection.commit()

    finally:
        connection.close()

def updateMot(uuid, lettre):
    jeu = json.loads(getJeu(uuid))
    mot = getMot(jeu["mot_id"])

    splitEtat = list(jeu["etat_mot"])
    splitMot = list(mot)

    for index, char in enumerate(splitMot):
        if char == lettre:
            splitEtat[index] = char

    updateMot = ''.join(splitEtat)

    connection = db.connect()

    # On insert le nouveau jeu
    req = "UPDATE jeu SET etat_mot = %s WHERE uuid = %s"

    try:
        cursor = connection.cursor()
        cursor.execute(req, (updateMot, uuid))
        connection.commit()

    finally:
        connection.close()

def terminePartie(uuid, statut):
    connection = db.connect()

    # On insert le nouveau jeu
    req = "UPDATE jeu SET statut = %s WHERE uuid = %s"

    try:
        cursor = connection.cursor()
        cursor.execute(req, (statut, uuid))
        connection.commit()

    finally:
        connection.close()

def decrementePartie(uuid):
    connection = db.connect()

    # On insert le nouveau jeu
    req = "UPDATE jeu SET coup_restant = coup_restant - 1 WHERE uuid = %s"
    req1 = "SELECT coup_restant FROM jeu WHERE uuid = %s"

    try:
        cursor = connection.cursor()
        cursor.execute(req, uuid)
        connection.commit()

        cursor.execute(req1, uuid)

        if cursor.fetchone()['coup_restant'] == 0:
            terminePartie(uuid, 1)

    finally:
        connection.close()

def sauvegardeNouvellePartie(uuid, mot_id, coup_restant, etat_mot, statut):
    connection = db.connect()

    # On insert le nouveau jeu
    req = "INSERT INTO jeu(uuid, mot_id, coup_restant, etat_mot, statut) VALUES(%s, %s, %s, %s, %s)"

    try:
        cursor = connection.cursor()
        cursor.execute(req, (uuid, mot_id, coup_restant, etat_mot, statut))
        connection.commit()

    finally:
        connection.close()

def getLettreTrouvee(uuid, lettre):
    connection = db.connect()

    # On récupère un mot de la longueur souhaitée
    req = "SELECT COUNT(*) AS count FROM lettre_trouve WHERE uuid = %s AND lettre = %s"

    try:
        cursor = connection.cursor()
        cursor.execute(req, (uuid, lettre))
        return cursor.fetchone()["count"]

    finally:
        connection.close()

def generationUUID():
    return uuid.uuid4().__str__()