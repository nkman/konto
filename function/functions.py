import jsontree

class Function:

    def __init__(self, api_key):

        self.api_key = api_key
        self.restricted_text = [
            "SELECT", 
            "UPDATE", 
            "DROP", 
            "MODIFY",
            "ALTER", 
            "!", 
            "#", 
            "%", 
            "&", 
            "(", 
            ")"
        ]

    def define_user_signup(self, request):

        user = jsontree.jsontree()
        user.username = request.get_json().get('username', '')
        user.password = request.get_json().get('password', '')
        user.firstname = request.get_json().get('firstname', '')
        user.lastname = request.get_json().get('lastname', '')
        user.phone = request.get_json().get('phone', '')

        try:
            user.api = request.headers['Authorization']
        except Exception, e:
            user.api = None
        

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
            if (username.count(str(i)) > 0):
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

            # if(len(phone) > 0 and phone.count(i) > 0):
            #     error_msg.status = 0
            #     error_msg.message = "Restricted text in phone"
            #     break

        return error_msg

    def define_user_login(self, request):

        user = jsontree.jsontree()
        user.username = request.get_json().get('username', '')
        user.password = request.get_json().get('password', '')
        
        try:
            user.api = request.headers['Authorization']
        except Exception, e:
            user.api = None

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

        if(api != self.api_key):
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

    def validate_user_input(self, data):

        """
        data is jsontree.jsontree
        should not contain some keywords
        defined in TEXTS;
        """

        error_msg = jsontree.jsontree()
        for one in data:
            if one.upper() in self.restricted_text:
                error_msg.status = 0
                error_msg.message = "Restricted text encountered."
                return error_msg

        if(data.api_key != self.api_key):
            error_msg.status = 0
            error_msg.message = "ERROR"
            return error_msg

        error_msg.status = 1
        return error_msg
