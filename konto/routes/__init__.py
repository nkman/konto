from konto import app
from flask import Flask, jsonify, request, render_template
from flask import make_response, url_for, redirect

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

    _user = json.loads(user_db.user_detail(user.user_id))
    _account = json.loads(user_db.user_account_detail(user.user_id))

    return render_template('konto.html', user=_user, account=_account)


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

    error_msg = jsontree.jsontree()

    if (request.method == 'GET'):
        error_msg.status = 0
        error_msg.message = "Method Not Allowed !!"
        return render_template("error.html", msg=error_msg)

    user = jsontree.jsontree()

    try:
        user.username = request.form['username']
        user.password = request.form['password']
        user.firstname = request.form['firstname']
        user.lastname = request.form['lastname']
        user.phone = request.form['phone']

    except Exception, TypeError:
        error_msg.status = 0
        error_msg.message = "Unexpected buffer data encountered !!"
        return render_template('error.html', msg=error_msg)

    if(user.username == '' or user.password == '' or user.firstname == ''):
        error_msg.status = 0
        error_msg.message = "Some credentials missing"
        return render_template('error.html', msg=error_msg)

    elif(user.lastname == ''):
        error_msg.status = 0
        error_msg.message = "Lastname is missing"
        return render_template('error.html', msg=error_msg)

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
        _user = json.loads(user_db.user_detail(user.user_id))
        resp = make_response(render_template('konto.html', user=_user))
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

    return redirect(url_for('home'))

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')
    is_logged = con.is_logged(user)

    if(user.user_id == '' or user.user_cookie == '' or is_logged == 0):
        return render_template('home.html')

    else:
        _user = json.loads(user_db.user_detail(user.user_id))
        return render_template('profile.html', user=_user)

@app.route('/profile/modify', methods=['GET', 'POST'])
def modify():
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')
    is_logged = con.is_logged(user)

    if(user.user_id == '' or user.user_cookie == '' or is_logged == 0):
        return render_template('home.html')

    error_msg = jsontree.jsontree()

    try:
        user.username = request.form['username']
        user.firstname = request.form['firstname']
        user.lastname = request.form['lastname']
        user.password = request.form['password']
        user.current_password = request.form['current_password']

    except Exception, e:
        error_msg.status = 0
        error_msg.message = e
        return render_template('error.html', msg=error_msg)

    if(user.current_password == ''):
        error_msg.status = 0
        error_msg.message = "Current password is required !!\nAuthentication failed !!"
        return render_template('error.html', msg=error_msg)

    if(user.username == '' or user.firstname == ''):
        error_msg.status = 0
        error_msg.message = "Some credentials missing"
        return render_template('error.html', msg=error_msg)

    elif(user.lastname == ''):
        error_msg.status = 0
        error_msg.message = "Lastname is missing"
        return render_template('error.html', msg=error_msg)

    is_changed = user_db.modify_user(user)

    if(is_changed.status == 0):
        error_msg.status = 0
        error_msg.message = is_changed.message
        return render_template('error.html', msg=error_msg)

    else:
        return redirect(url_for('home'))
        pass

@app.route('/add', methods=['GET', 'POST'])
def add_front():
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')
    is_logged = con.is_logged(user)

    if(user.user_id == '' or user.user_cookie == '' or is_logged == 0):
        return render_template('home.html')

    _user = json.loads(user_db.user_detail(user.user_id))
    return render_template('add.html', user=_user)

@app.route('/add/<user_id>', methods=['GET', 'POST'])
def add_back(user_id):
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')
    is_logged = con.is_logged(user)

    if(user.user_id == '' or user.user_cookie == '' or is_logged == 0):
        return render_template('home.html')

    user_id_user1 = user.user_id
    user_id_user2 = user_id
