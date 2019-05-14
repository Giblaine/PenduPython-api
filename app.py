#! /usr/bin/python
# -*- coding:utf-8 -*-

import functions
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "PenduAPI 1.0"

@app.route('/jeu/nouveau/<length>')
def nouveauJeu(length):
    return functions.nouveauJeu(length)

if __name__ == '__main__':
    app.run(debug=True)