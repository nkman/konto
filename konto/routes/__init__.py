from konto import app
from flask import Flask, jsonify, request, render_template
from flask import make_response

import config
import uuid
import jsontree, json

from db import database
from user import user

configuration = config.config()
con = database.Database(configuration)
con.connect()

user_db = user.User(configuration)

@app.route('/')

def home():
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')
    is_logged = con.is_logged(user)

    if(user.user_id == '' or user.user_cookie == '' or is_logged == 0):
        return render_template('home.html')

    else:
        return render_template('konto.html', user=user_db.user_detail(user.user_id))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    try:
        con.drop_all()
        con.user_table()
        con.address_table()
        con.account_table()
        con.Med_table()
        con.Cookie()
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

    msg = con.verify_user_credential(user)

    if(msg.status == 1):
        user.user_id = msg.userId
        user_detail = con.set_user_cookie(user)
        resp = make_response(render_template('konto.html', user=user_db.user_detail(user.user_id)))
        resp.set_cookie('user', user_detail.user_id)
        resp.set_cookie('tea', user_detail.cookie)
        return resp

    else:
        return json.dumps(msg)


@app.route('/logout', methods=['GET', 'POST'])
def logout():

    user = jsontree.jsontree()

    user.user_id = request.cookies.get('user')
    user.cookie = request.cookies.get('tea')

    msg = con.logout(user)

    render_template('logout.html', msg=msg)
