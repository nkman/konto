from konto import app
from flask import Flask, jsonify, request, render_template
from flask import make_response, url_for, redirect

import config
import uuid
import jsontree, json

from db import database
from user import user

configuration = config.config()
api_key = configuration['API']

con = database.Database(configuration)
con.connect()

user_db = user.User(configuration)

@app.route('/mobile', methods=['POST'])
def mobile_home_page():
    return "Hello Cruel World!!"

@app.route('/mobile/signup', methods=['POST'])
def mobile_user_signup():
    error_msg = jsontree.jsontree()

    if (request.method == 'GET'):
        error_msg.status = 0
        error_msg.message = "Method Not Allowed !!"
        return json.dumps(error_msg)

    user = define_user(request)

    if(user.phone == ''):
        user.phone = None

    error_msg = text_security(user)

    if(error_msg.status == 0):
        return json.dumps(error_msg)

    c = con.create_user(user)
    c = json.loads(c)

    if(c['status'] == 0):
        return json.dumps(c)
    else:
        return json.dumps(c)

def define_user(request):

    user = jsontree.jsontree()
    user.username = request.form['username']
    user.password = request.form['password']
    user.firstname = request.form['firstname']
    user.lastname = request.form['lastname']
    user.phone = request.form['phone']
    user.api = request.headers['Authorization']

    return user

def text_security(text):

    TEXTS = ["SELECT", "UPDATE", "DROP", "MODIFY",
            "ALTER", "!", "#", "%", "&", "(", ")"]

    username = text.username
    firstname = text.firstname
    lastname = text.lastname
    phone = text.phone
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

    elif(firstname == ''):
        error_msg.status = 0
        error_msg.message = "Firstname missing"
        return error_msg

    elif(lastname == ''):
        error_msg.status = 0
        error_msg.message = "Lastname is missing"
        return error_msg

    if(api != api_key):
        error_msg.status = 0
        error_msg.message = "You are not allowed here !!"
        return error_msg

    for i in TEXTS:
        if (username.count(i) > 0):
            error_msg.status = 0
            error_msg.message = "Restricted text in username"
            break

        if(firstname.count(i) > 0):
            error_msg.status = 0
            error_msg.message = "Restricted text in firstname"
            break

        if(lastname.count(i) > 0):
            error_msg.status = 0
            error_msg.message = "Restricted text in lastname"
            break

        if(phone.count(i) > 0):
            error_msg.status = 0
            error_msg.message = "Restricted text in phone"
            break

    return error_msg


