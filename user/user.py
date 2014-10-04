import sys
import jsontree, json
from db import database

class User:

    def __init__(self, config):
        self.connection = database.Database(config)
        self.con = self.connection.connect()

    def user_detail(self, user_id):
        user = jsontree.jsontree()

        firstname_lastname = self.firstname_lastname(user_id)

        if(firstname_lastname.status == 1):
            user.firstname = firstname_lastname.firstname
            user.lastname = firstname_lastname.lastname
            user.user_id = user_id

        username = self.username(user_id)

        if(username.status == 1):
            user.username = username.username

        return json.dumps(user)

    def firstname_lastname(self, user_id):
        """
        firstname:
        lastname:
        """

        con = self.con
        user = jsontree.jsontree()

        query = """
            SELECT firstname, lastname FROM address WHERE
            userId=\'%s\'
        """ % (user_id)

        cursor = con.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

        except Exception, e:
            user.status = 0
            user.message = e
            return user

        user.status = 1
        user.user_id = user_id
        user.firstname = result[0]
        user.lastname = result[1]

        return user

    def username(self, user_id):
        con = self.con
        user = jsontree.jsontree()

        query = """
            SELECT username FROM users WHERE 
            userId=\'%s\'
        """ % (user_id)
        cursor = con.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

        except Exception, e:
            user.status = 0
            user.message = e
            return user

        user.status = 1
        user.username = result[0]

        return user

    def modify_user(self, user):

        username = user.username
        firstname = user.firstname
        lastname = user.lastname
        password = user.password
        current_password = user.current_password
        user_id = user.user_id

        query = """
            SELECT username, password FROM users WHERE
            userId=\'%s\'
        """ % (user_id)

        cursor = self.con.cursor()
        msg = jsontree.jsontree()

        try:
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
         
        except Exception, e:
            msg.status = 0
            msg.phase = 1
            msg.message = e
            return msg

        if(result == None):
            msg.status = 0
            msg.message = "This user does not exists !!"
            return msg

        if(current_password != result[1]):
            msg.status = 0
            msg.message = "Password does not match!!\nAuthentication failed !"
            return msg

        if(self.connection.user_found(username) == 1 and username != result[0]):
            msg.status = 0
            msg.message = "This username already exists !!"
            return msg

        if(password != ''):
            query = """
                UPDATE users SET
                username = \'%s\', password = \'%s\'
                WHERE userId = \'%s\'
            """ % (username, password, user_id)

        else:
            query = """
                UPDATE users SET
                username = \'%s\'
                WHERE userId = \'%s\'
            """ % (username, user_id)

        con = self.con
        cursor = con.cursor()

        try:
            cursor.execute(query)
            con.commit()
            cursor.close()

        except Exception, e:
            msg.status = 0
            msg.phase = 2
            msg.message = e
            return msg

        query = """
            UPDATE address SET
            firstname = \'%s\', lastname = \'%s\'
            WHERE useId = \'%s\'
        """ % (firstname, lastname, user_id)

        cursor = ccon.cursor()

        try:
            cursor.execute(query)
            con.commit()
            cursor.close()

        except Exception, e:
            msg.status = 0
            msg.phase = 2
            msg.message = e
            return msg

        msg.status = 1
        return msg
