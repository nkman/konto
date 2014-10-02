from konto import app
from flask import Flask, jsonify, request, render_template
from flask import make_response

import config
import uuid
import jsontree, json

from db import database

configuration = config.config()
con = database.Database(configuration)
con.connect()

@app.route('/')

def home():
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')

    if(con.is_logged(user) == 0):
        return render_template('home.html')

    return render_template('home.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    try:
        con.connect()
        con.user_table()
        con.address_table()
        con.account_table()
        con.Med_table()
        return "Done"

    except Exception, e:
        print e
        raise e
    

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

    if(user.phone == ''):
        user.phone = None

    return json.dumps(con.create_user(user))

@app.route('/login', methods=['GET', 'POST'])
def login():

    if (request.method == 'GET'):
        return "Method Not Allowed !!"

    user = jsontree.jsontree()
    user.username = request.form['username']
    user.password = request.form['password']

