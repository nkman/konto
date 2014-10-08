import sys
import jsontree, json
from db import database
from datetime import datetime
import uuid

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

        else:
            user.status = 0
            return json.dumps(user)

        username = self.username(user_id)

        if(username.status == 1):
            user.username = username.username

        else:
            user.status = 0
            return json.dumps(user)

        user.status = 1
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
            msg.message = str(e)
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
            msg.message = str(e)
            return msg

        query = """
            UPDATE address SET
            firstname = \'%s\', lastname = \'%s\'
            WHERE userId = \'%s\'
        """ % (firstname, lastname, user_id)

        cursor = con.cursor()

        try:
            cursor.execute(query)
            con.commit()
            cursor.close()

        except Exception, e:
            msg.status = 0
            msg.phase = 2
            msg.message = str(e)
            return msg

        msg.status = 1
        return msg

    def user_account_detail(self, user_id):

        error_msg = jsontree.jsontree()
        account_detail = jsontree.jsontree()

        query = """
            SELECT accountId, userId1, userId2, balance
            FROM account
            WHERE userId1 = \'%s\' AND
            confirmed_by_user1 = True AND 
            confirmed_by_user2 = True
        """ % (user_id)

        cursor = self.con.cursor()

        try:
            cursor.execute(query)
            result1 = cursor.fetchall()
            print result1

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            sys.stdout.write('USER PHASE I')
            return json.dumps(error_msg)

        query = """
            SELECT accountId, userId1, userId2, balance
            FROM account
            WHERE userId2 = \'%s\' AND
            confirmed_by_user1 = True AND 
            confirmed_by_user2 = True
        """ % (user_id)

        try:
            cursor.execute(query)
            result2 = cursor.fetchall()
            cursor.close()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            sys.stdout.write('USER PHASE II')
            return json.dumps(error_msg)

        account_detail.current_balance = 0
        account_detail.positive_name = []
        account_detail.negetive_name = []

        for acc in result1:
            account_detail.current_balance += int(acc[3])
            name = self.firstname_lastname(acc[2])
            account_detail.positive_name.append(name.firstname+" "+name.lastname)

        for acc in result2:
            account_detail.current_balance -= int(acc[3])
            name = self.firstname_lastname(acc[1])
            account_detail.negetive_name.append(name.firstname+" "+name.lastname)

        account_detail.status = 1
        account_detail.positive = result1
        account_detail.negetive = result2

        return json.dumps(account_detail)

    def matching_names(self, name):

        error_msg = jsontree.jsontree()

        query = """
            SELECT username FROM users
            WHERE username LIKE \'%s%%\'
        """ % (name)

        cursor = self.con.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            return json.dumps(error_msg)
        
        return result

    def create_balance(self, user):

        return self.connection.create_balance(user)

    def notification(self, user_id):
        
        #Get notifications from mid
        #Get notifications from notification

        error_msg = jsontree.jsontree()
        notice = jsontree.jsontree()
        name = jsontree.jsontree()

        name.positive = []
        name.negetive = []
        name.unread = []

        query = """
            SELECT accountId, userId1,
            userId2, balance
            FROM account WHERE
            userId1 = \'%s\' AND 
            confirmed_by_user1 = \'%s\'
        """ % (user_id, False)

        cursor = self.con.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchall()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            return json.dumps(error_msg)

        notice.positive = result

        for res in result:

            query = """
                SELECT firstname, lastname from address
                WHERE userId = \'%s\'
            """ % (res[2])

            try:
                cursor.execute(query)
                result_name = cursor.fetchone()

            except Exception, e:
                error_msg.status = 0
                error_msg.message = str(e)
                return json.dumps(error_msg)

            name.positive.append(result_name[0]+" "+result_name[1])

        query = """
            SELECT accountId, userId1,
            userId2, balance
            FROM account WHERE
            userId2 = \'%s\' AND 
            confirmed_by_user2 = \'%s\'
        """ % (user_id, False)

        try:
            cursor.execute(query)
            result = cursor.fetchall()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            return json.dumps(error_msg)

        notice.negetive = result

        for res in result:

            query = """
                SELECT firstname, lastname from address
                WHERE userId = \'%s\'
            """ % (res[1])

            try:
                cursor.execute(query)
                result_name = cursor.fetchone()

            except Exception, e:
                error_msg.status = 0
                error_msg.message = str(e)
                return json.dumps(error_msg)

            name.negetive.append(result_name[0]+" "+result_name[1])

        query = """
            SELECT noticeId, userId,
            notice FROM notification WHERE
            userId = \'%s\' AND 
            unread = \'%s\'
        """ % (user_id, True)

        try:
            cursor.execute(query)
            result = cursor.fetchall()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            return json.dumps(error_msg)

        cursor.close()
        notice.unread = result
        notice.name = name
        notice.status = 1

        notice = json.dumps(notice)
        return notice

    def mark_notification_read(self, notice_id):

        query = """
            UPDATE notification SET
            unread = \'%s\' WHERE
            noticeId = \'%s\'
        """ % (False, notice_id)

        con = self.con
        cursor = con.cursor()

        try:
            cursor.execute(query)
            con.commit()

        except Exception, e:
            raise e

        return 1

    def mark_accept(self, user):

        error_msg = jsontree.jsontree()

        account_id = user.account_id
        user_id = user.user_id

        query = """
            SELECT userId1, userId2 FROM account
            WHERE accountId = \'%s\'
        """ % (account_id)

        con = self.con
        cursor = con.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            error_msg = json.dumps(error_msg)
            return error_msg

        if(result == None):
            error_msg.status = 0
            error_msg.message = "Transaction not found."
            error_msg = json.dumps(error_msg)
            return error_msg

        if(result[0] == user_id):

            userId = result[1]
            update_db_query = """
                UPDATE account SET confirmed_by_user1 = \'%s\' WHERE
                accountId = \'%s\'
            """ % (True, account_id)

        else:

            userId = result[0]
            update_db_query = """
                UPDATE account SET confirmed_by_user2 = \'%s\' WHERE
                accountId = \'%s\'
            """ % (True, account_id)

        name = self.firstname_lastname(user_id)
        notice = name.firstname+" "+name.lastname+" accepted the deal" #Modi--fy this line.
        date_added = datetime.now()
        noticeId = str(uuid.uuid1())

        query = """
            INSERT INTO notification (
            noticeId, userId, notice, date_added)
            VALUES (\'%s\', \'%s\', \'%s\', \'%s\')
        """ % (noticeId, userId, notice, date_added)

        try:
            cursor.execute(query)
            con.commit()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            error_msg = json.dumps(error_msg)
            return error_msg

        try:
            cursor.execute(update_db_query)
            con.commit()
            cursor.close()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            error_msg = json.dumps(error_msg)
            return error_msg

        error_msg.status = 1
        error_msg = json.dumps(error_msg)
        return error_msg

    def mark_decline(self, user):

        error_msg = jsontree.jsontree()

        account_id = user.account_id
        user_id = user.user_id

        query = """
            SELECT userId1, userId2 FROM account
            WHERE accountId = \'%s\'
        """ % (account_id)

        con = self.con
        cursor = con.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            error_msg = json.dumps(error_msg)
            return error_msg

        if(result == None):
            error_msg.status = 0
            error_msg.message = "Transaction not found."
            error_msg = json.dumps(error_msg)
            return error_msg

        if(result[0] == user_id):
            userId = result[1]
        else:
            userId = result[0]

        update_db_query = """
                DELETE FROM account WHERE
                accountId = \'%s\'
            """ % (account_id)

        name = self.firstname_lastname(user_id)
        notice = name.firstname+" "+name.lastname+" Deleted the deal" #Modi--fy this line.
        date_added = datetime.now()
        noticeId = str(uuid.uuid1())

        query = """
            INSERT INTO notification (
            noticeId, userId, notice, date_added)
            VALUES (\'%s\', \'%s\', \'%s\', \'%s\')
        """ % (noticeId, userId, notice, date_added)

        try:
            cursor.execute(query)
            con.commit()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            error_msg = json.dumps(error_msg)
            return error_msg

        try:
            cursor.execute(update_db_query)
            con.commit()
            cursor.close()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = str(e)
            error_msg = json.dumps(error_msg)
            return error_msg

        error_msg.status = 1
        error_msg = json.dumps(error_msg)
        return error_msg
