#! /usr/bin/python
# -*- coding:utf-8 -*-

from modules import functions
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "PenduAPI 1.0"

@app.route('/jeu/nouveau/<length>')
def nouveauJeu(length):
    return functions.nouveauJeu(length)

@app.route('/jeu/<uuid>')
def jeu(uuid):
    return functions.getJeu(uuid)

@app.route('/jeu/jouer/<uuid>/<lettre>')
def jouer(uuid, lettre):
    return functions.jouer(uuid, lettre.upper())

if __name__ == '__main__':
    app.run(debug=True)