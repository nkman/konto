import jsontree

class Function:

    def __init__(self, api_key):

        self.api_key = api_key
        pass

    def define_user_signup(self, request):

        user = jsontree.jsontree()
        user.username = request.form['username']
        user.password = request.form['password']
        user.firstname = request.form['firstname']
        user.lastname = request.form['lastname']
        user.phone = request.form['phone']
        user.api = request.headers['Authorization']

        return user

    def signup_text_security(self, text):

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

        if(api != self.api_key):
            error_msg.status = 0
            error_msg.message = "You should not be here !!"
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

    def define_user_login(self, request):

        user = jsontree.jsontree()
        user.username = request.form['username']
        user.password = request.form['password']
        user.api = request.headers['Authorization']

        return user

    def login_text_security(self, text):
        
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
