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

This route has been tested !!
"""
@app.route('/mobile/signup', methods=['POST'])
def mobile_user_signup():
    error_msg = jsontree.jsontree()

    if (request.method == 'GET'):
        error_msg.status = 0
        error_msg.message = "Method Not Allowed !!"
        return json.dumps(error_msg)

    request.get_json(force=True)
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

This route has been tested !!
"""
@app.route('/mobile/login', methods=['POST'])
def mobile_user_login():

    request.get_json(force=True)
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
This route is to add a transaction
send the following

{
    fellow_username: "",
    amount:,
    sign:(positive or negetive)
}

This route has been tested !!
"""
@app.route('/mobile/add', methods=['POST'])
def mobile_add_balance():

    user = jsontree.jsontree()
    user_id = request.cookies.get('user')

    logged_in = con.is_logged(user_id, request.cookies.get('tea'))
    if(logged_in == 0):
        return not_logged_in()

    request.get_json(force=True)
    user.fellow_username = request.get_json().get('fellow_username', '')
    user.amount = request.get_json().get('amount', '')
    user.mod = request.get_json().get('sign', '')
    user.user_id = user_id

    #TODO: define the function below
    c = con.create_balance(user)

    return json.dumps(c)

"""
This route is to get all pending transactions
send the following

{
    unread: 0
}

This route has been tested !!
"""
@app.route('/mobile/notification', methods=['POST'])
def get_notification():

    notice = jsontree.jsontree()
    user_id = request.cookies.get('user')

    logged_in = con.is_logged(user_id, request.cookies.get('tea'))
    if(logged_in == 0):
        return not_logged_in()

    user_input = jsontree.jsontree()

    request.get_json(force=True)
    user_input.unread = request.get_json().get('unread', '')
    user_input.count = request.get_json().get('count', '')
    # user_input.last_sync = request.form['last_sync']
    user.api_key = request.headers['Authorization']

    is_valid = function.validate_user_input(user_input)

    if(is_valid == 0):
        return json.dumps(is_valid)

    #lets
    user_input.count = 0

    if(user_input.unread == 1):
        notice.positive = con.positive_notification(user_id, user_input.count)
        notice.negetive = con.negetive_notification(user_id, user_input.count)
        notice.track = con.tracking_notification(user_id, user_input.count)

    # else:
        # notice = con.all_notification(user_id, count, last_sync)
    notice.status = 1

    return json.dumps(notice)

"""
This route is to mark tracked notification as read
send the following

{
    notice_id: ""
}

This route has been tested !!
"""
@app.route('/mobile/notification/read', methods=['POST'])
def mobile_notification_read():

    user_id = request.cookies.get('user')

    logged_in = con.is_logged(user_id, request.cookies.get('tea'))
    if(logged_in == 0):
        return not_logged_in()

    request.get_json(force=True)
    notice_id = request.get_json().get('notice_id', '')
    mark_read = con.mark_notification_read(notice_id, user_id)

    return json.dumps(mark_read)



"""
This route is to accept the deal
send the following

{
    account_id: "",
    decision: "Accept"
}

This route has been tested !!
"""
@app.route('/mobile/notification/accept', methods=['POST'])
def mobile_notification_accept():

    user_id = request.cookies.get('user')

    logged_in = con.is_logged(user_id, request.cookies.get('tea'))
    if(logged_in == 0):
        return not_logged_in()

    user = jsontree.jsontree()

    user.user_id = user_id
    request.get_json(force=True)
    user.account_id = request.get_json().get('account_id', '')
    user.decision = request.get_json().get('decision', '')

    if(user.decision == 'Accept'):
        ac = con.mark_accept(user)
    else:
        ac = {"status": 0, "message": "cannot_recognise_command"}

    return json.dumps(ac)


"""
This route is to decline the deal
send the following

{
    account_id: "",
    decision: "Decline"
}

This route has been tested !!
"""
@app.route('/mobile/notification/decline', methods=['GET', 'POST'])
def mobile_notification_decline():

    user_id = request.cookies.get('user')

    logged_in = con.is_logged(user_id, request.cookies.get('tea'))
    if(logged_in == 0):
        return not_logged_in()

    user = jsontree.jsontree()
    user.user_id = user_id

    request.get_json(force=True)
    user.account_id = request.get_json().get('account_id', '')
    user.decision = request.get_json().get('decision', '')

    if(user.decision == 'Decline'):
        ac = con.mark_decline(user)
    else:
        ac = {"status": 0, "message": "cannot_recognise_command"}

    return json.dumps(ac)

"""
This route is to delete the transaction
send the following

{
    account_id: "",
    decision: "Delete"
}

This route has been tested !!
"""
@app.route('/mobile/notification/delete', methods=['GET', 'POST'])
def mobile_notification_delete():

    user_id = request.cookies.get('user')

    logged_in = con.is_logged(user_id, request.cookies.get('tea'))
    if(logged_in == 0):
        return not_logged_in()

    user = jsontree.jsontree()

    user.user_id = user_id
    request.get_json(force=True)
    user.account_id = request.get_json().get('account_id', '')
    user.decision = request.get_json().get('decision', '')

    if(user.decision == 'Delete'):
        ac = con.del_user_transaction(user)
    else:
        ac = {"status": 0, "message": "cannot_recognise_command"}

    return json.dumps(ac)

@app.route('/mobile/getall', methods=['POST'])
def getAll():

    user_id = request.cookies.get('user')

    logged_in = con.is_logged(user_id, request.cookies.get('tea'))
    if(logged_in == 0):
        return not_logged_in()

    return con.user_account_detail(user_id)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def not_logged_in():
    error_msg = jsontree.jsontree()
    error_msg.status = 0
    error_msg.message = "NOT_LOGGED_IN"
    return json.dumps(error_msg)

@app.route('/mobile/remove', methods= ['POST'])
def remove_balance():
    """
    user_id = request.cookies.get('user')

    logged_in = con.is_logged(user_id, request.cookies.get('tea'))
    if(logged_in == 0):
        return not_logged_in()

    user = jsontree.jsontree()
    user.account_id = request.form['account_id']
    decision = request.form['mod']
    """

    pass
