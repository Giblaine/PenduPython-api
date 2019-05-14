#! /usr/bin/python
# -*- coding:utf-8 -*-

import db

def nouveauJeu(length):
    mot = nouveauMot(length)
    return 'LE MOT: ' + mot

def nouveauMot(length):
    connection = db.connect()

    # On récupère un mot de la longueur souhaitée
    req = "SELECT * FROM mot WHERE RAND() > 0.9 AND longueur = %s ORDER BY RAND() LIMIT 1"

    try:
        cursor = connection.cursor()
        cursor.execute(req, length)
        return cursor.fetchone()['mot']

    finally:
        connection.close()