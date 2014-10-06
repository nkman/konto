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

    if( _user['status'] == 0):
        return render_template('error.html', msg=_user)

    _account = json.loads(user_db.user_account_detail(user.user_id))

    if(_account['status'] == 0):
        return render_template('error.html', msg=_account, user=_user)

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
        con.notification_table()
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
        _account = json.loads(user_db.user_account_detail(user.user_id))
        resp = make_response(render_template('konto.html', user=_user, account=_account))
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

@app.route('/add/<username>', methods=['GET', 'POST'])
def add_back(username=None):
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')
    is_logged = con.is_logged(user)

    if(user.user_id == '' or user.user_cookie == '' or is_logged == 0):
        return render_template('home.html')

    user.fellow_username = request.form['fellow_username']
    user.amount = request.form['amount']
    user.mod = request.form['sign']

    user_db.create_balance(user)

    return redirect(url_for('home'))

@app.route('/ajax/getname')
def ajax_api_getname():

    matching_names = {}
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')
    is_logged = con.is_logged(user)

    if(user.user_id == '' or user.user_cookie == '' or is_logged == 0):
        return matching_names

    name = request.forms['fellow_username']
    matching_names = user_db.matching_names(name)

    return matching_names

@app.route('/notification', methods=['GET', 'POST'])
def notification():
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')
    is_logged = con.is_logged(user)

    if(user.user_id == '' or user.user_cookie == '' or is_logged == 0):
        return redirect(url_for('home'))

    notice = user_db.notification(user.user_id)
    notice = json.loads(notice)

    _user = user_db.user_detail(user.user_id)
    _user = json.loads(_user)

    if( _user['status'] == 0):
        return render_template('error.html', msg=_user)

    if(notice['status'] == 0):
        return render_template('error.html', msg=notice)

    return render_template('notification.html', notice=notice, user=_user)

@app.route('/notification/read', methods=['GET', 'POST'])
def read():
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')
    is_logged = con.is_logged(user)

    if(user.user_id == '' or user.user_cookie == '' or is_logged == 0):
        return redirect(url_for('home'))

    notice_id = request.form['notice_id']
    user_db.mark_notification_read(notice_id)

    return redirect(url_for('notification'))

@app.route('/notification/accept', methods=['GET', 'POST'])
def notification_accept():
    user = jsontree.jsontree()
    user.user_id = request.cookies.get('user')
    user.user_cookie = request.cookies.get('tea')
    is_logged = con.is_logged(user)

    if(user.user_id == '' or user.user_cookie == '' or is_logged == 0):
        return redirect(url_for('home'))

    user.account_id = request.form['account_id']
    user.decision = request.form['decision']

    if(user.decision == 'Accept'):
        user_db.mark_accept(user)

    return redirect(url_for('notification'))
