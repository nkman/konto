from konto import app
from flask import Flask, jsonify, request, render_template

import config
from db import database

import jsontree

configuration = config.config()
con = database.Database(configuration)

@app.route('/')

def home():

	print configuration
	return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():

	if (request.method == 'GET'):
		return "Method Not Allowed !!"

	user = jsontree.jsontree()
	user.username = request.form['username']
	user.password = request.form['password']
	user.firstname = request.form['firstname']
	user.lastname = request.form['lastname']
	user.phone = request.form['phone']

	if(user.username == '' or user.password == '' or user.firstname == ''):
		return "Some credentials missing"
	elif(user.lastname == ''):
		return "Some credentials missing"

	if user.phone == '':
		print "No"
	return "LOL"