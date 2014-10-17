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
@app.route('/mobile/login')
def mobile_user_login():

    user = define_user_login(request)

    error_msg = login_text_security(user)

    if(error_msg.status == 0):
        return json.dumps(error_msg)

    c = con.create_user(user)
    c = json.loads(c)

    if(c['status'] == 0):
        return json.dumps(c)
    else:
        return json.dumps(c)


def define_user_login(request):

    user = jsontree.jsontree()
    user.username = request.form['username']
    user.password = request.form['password']
    user.api = request.headers['Authorization']

    return user

def login_text_security(text):
    
    TEXTS = ["SELECT", "UPDATE", "DROP", "MODIFY",
            "ALTER", "!", "#", "%", "&", "(", ")"]

    username = text.username
    password = text.password
    api = text.api

    error_msg = jsontree.jsontree()
    error_msg.status = 1

    if(username == ''):
        error_msg.status = 0
        error_msg.message = "Username missing"
        return error_msg

    elif(password == ''):
        error_msg.status = 0
        error_msg.message = "Password missing"
        return error_msg

    if(api != api_key):
        error_msg.status = 0
        error_msg.message = "You should not be here !!"
        return error_msg

    for i in TEXTS:
        if (username.count(i) > 0):
            error_msg.status = 0
            error_msg.message = "Restricted text in username"
            break

        if(password.count(i) > 0):
            error_msg.status = 0
            error_msg.message = "Restricted text in firstname"
            break

    return error_msg
