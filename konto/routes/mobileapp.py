from konto import app
from flask import Flask, jsonify, request, render_template
from flask import make_response, url_for, redirect

import config
import uuid
import jsontree, json

from user import user
from mobile import mobileApi

from function import functions

configuration = config.config()
api_key = configuration['API']

con = mobileApi.Mobile(configuration)
con.connect()

user_db = user.User(configuration)

function = functions.Function(api_key)
@app.route('/mobile', methods=['POST'])
def mobile_home_page():
    return "Hello Cruel World!!"


"""
This route for signup.

send the following:

    in form:
        username
        firstname
        lastname
        password
        phone

    in header:
        Authorization

It will response as:

{
    status: 1
}

or

{
    status: 0,
    message: "REASON_FOR_THIS"
}

"""
@app.route('/mobile/signup', methods=['POST'])
def mobile_user_signup():
    error_msg = jsontree.jsontree()

    if (request.method == 'GET'):
        error_msg.status = 0
        error_msg.message = "Method Not Allowed !!"
        return json.dumps(error_msg)

    user = function.define_user_signup(request)

    if(user.phone == ''):
        user.phone = None

    error_msg = function.signup_text_security(user)

    if(error_msg.status == 0):
        return json.dumps(error_msg)

    c = con.create_user(user)
    c = json.loads(c)

    if(c['status'] == 0):
        return json.dumps(c)
    else:
        return json.dumps(c)

"""
-------------------------------
-------------------------------
"""

"""
This route for login
send the following:

    in form:
        username
        password

    in header:
        Authorization

    it will return the json of userdata as

    {   
        status: 1,
        username: "nkman",
        firstname: "Nairitya",
        lastname: "Khilari"
    } 

    or

    {
        status: 0,
        message: "USER_NOT_FOUND"
    }

"""
@app.route('/mobile/login', methods=['POST'])
def mobile_user_login():

    user = function.define_user_login(request)

    error_msg = function.login_text_security(user)

    if(error_msg.status == 0):
        return json.dumps(error_msg)

    c = con.verify_user(user)

    if(c.status == 0):
        return json.dumps(c)

    result = con.user_login(c.user_id)
    result = json.dumps(result)
    resp = make_response(result)

    cookie = con.set_cookie_to_user(c.user_id)

    if(cookie.status == 0):
        resp.set_cookie("tea", "Temporary account access !")
    else:
        resp.set_cookie('tea', cookie.cookie)

    resp.set_cookie('user', c.user_id)
    return resp


"""
Notification API's

GET:
    unread: 0
    count: 0
    # last_sync: timestamp

"""
@app.route('/mobile/notification', methods=['POST'])
def get_notification():

    notice = jsontree.jsontree()
    user_id = request.cookies.get('user')

    logged_in = con.is_logged(user_id, request.cookies.get('tea'))
    if(logged_in == 0):
        return self.not_logged_in()

    user_input = jsontree.jsontree()
    user_input.unread = request.form['unread']
    user_input.count = request.form['count']
    # user_input.last_sync = request.form['last_sync']
    user.api_key = request.headers['Authorization']

    is_valid = function.validate_user_input(user_input)

    if(is_valid == 0):
        return json.dumps(is_valid)

    if(user_input.unread == 1):
        notice.positive = con.positive_notification(user_id, count)
        notice.negetive = con.negetive_notification(user_id, count)
        notice.track = con.tracking_notification(user_id, count)

    # else:
        # notice = con.all_notification(user_id, count, last_sync)
    notice.status = 1

    return notice

@app.route('/mobile/add')
def add_balance():

    user = jsontree.jsontree()
    user_id = request.cookies.get('user')

    logged_in = con.is_logged(user_id, request.cookies.get('tea'))
    if(logged_in == 0):
        return self.not_logged_in()

    user.fellow_username = request.form['fellow_username']
    user.amount = request.form['amount']
    user.mod = request.form['sign']

    #TODO: define the function below
    c = con.add_balance(user)

    return json.dumps(c)

def not_logged_in():
    error_msg = jsontree.jsontree()
    error_msg.status = 0
    error_msg.message = "NOT_LOGGED_IN"
    return json.dumps(error_msg)