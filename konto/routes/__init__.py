from konto import app
from flask import Flask, jsonify, request, render_template

import config
from db import database

configuration = config.config()
con = database.Database(configuration)

@app.route('/')

def home():

	print configuration
	return "Hello"

@app.route('/signup', methods='POST')
def signup():

	return "Sinup"