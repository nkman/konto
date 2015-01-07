import sys, os
import psycopg2, uuid
import jsontree, json
from datetime import datetime

class Mobile:

    def __init__(self, config):

        self.host = config['host']
        self.port = config['port']
        self.user = config['user']
        self.password = config['password']
        self.database = config['database']



    def connect(self):

        connection = psycopg2.connect(host=self.host, 
            port=self.port, 
            user=self.user, 
            password=self.password, 
            database=self.database
        )
        self.connection = connection
        return connection



    def restart_connection(self):
        self.connection.close()
        self.connect()
        sys.stdout.write("Restarted the connection !!")



    def verify_user(self, user):

        username = user.username
        password = user.password

        query = """
            SELECT password, userId FROM users WHERE username=\'%s\'
        """ % (username)

        cursor = self.connection.cursor()
        error_msg = jsontree.jsontree()

        try:
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)
            sys.stdout.write(e)
            error_msg.status = 0
            error_msg.message = e
            return error_msg

        if(result == None):
            error_msg.status = 0
            error_msg.message = "No such user exists !!"

        elif(result[0] == password):
            error_msg.status = 1
            error_msg.user_id = result[1]
            error_msg.username = username

        else:
            error_msg.status = 0
            error_msg.message = "Wrong password."

        return error_msg



    def user_already_exists(self, username):

        query = 'SELECT * FROM users WHERE username=\'%s\'' % username
        cursor = self.connection.cursor()

        try:
            cursor.execute(query)

        except Exception, e:
            self.restart_connection()
            sys.stdout.write(e)

        result = cursor.fetchone()
        cursor.close()

        if (result == None):
            return 0

        else:
            sys.stdout.write("Username exists")
            return 1


    def create_user(self, user):

        username = user['username']
        password = user['password']

        msg = jsontree.jsontree()

        if(self.user_already_exists(username) == 1):
            msg.status = 0
            msg.message = "username exists !!"
            return json.dumps(msg)

        _id = uuid.uuid1()
        date_added = datetime.now()

        query = """
            INSERT INTO users(username, password, userId, date_added)
            VALUES (\'%s\', \'%s\', \'%s\', \'%s\')
        """ % (username, password, str(_id), date_added)

        cursor = self.connection.cursor()
        conn = self.connection

        try:
            cursor.execute(query)
            cursor.close()

        except Exception, e:
            self.restart_connection()

            sys.stdout.write(e)
            cursor.close()
            msg.status = 0
            msg.message = "user creation failed !!"
            return json.dumps(msg)

        try:
            msg = self.create_address(user, conn)

        except Exception, e:
            self.restart_connection()
            sys.stdout.write(e)
            msg.status = 0
            msg.message = "user address creation failed !!"
            return json.dumps(msg)

        # if (msg.status == 1):
        #     msg.message = "user and user address created successfully !!"
        # else:
        #     msg.message = "user created but adderss creation failed !!"
            #delete_created_user()

        return json.dumps(msg)



    def create_address(self, user, conn):

        username = user['username']
        firstname = user['firstname']
        lastname = user['lastname']
        phone = user['phone']

        _id = uuid.uuid1()

        query = """
            SELECT userId FROM users WHERE username=\'%s\'
        """ % username

        cursor = conn.cursor()

        msg = jsontree.jsontree()

        try:
            cursor.execute(query)
        except Exception, e:
            self.debug_InternalError(e)

            msg.status = 0
            msg.message = str(e)
            return msg

        date_added = datetime.now()
        userId = cursor.fetchone()[0]

        query = """
            INSERT INTO address(addressId, userId, firstname, lastname, phone, date_added)
            VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')
        """ % (str(_id), userId, firstname, lastname, phone, date_added)

        try:
            cursor.execute(query)
            conn.commit()
            sys.stdout.write("New adderss created !")
            msg.status = 1

        except Exception, e:
            self.restart_connection()
            msg.status = 0
            sys.stdout.write(e)
            msg.message = str(e)
        
        cursor.close()
        return msg



    def user_login(self, user_id):
        return self.user_detail(user_id)



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

        con = self.connection
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
        con = self.connection
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
            user.message = str(e)
            return user

        user.status = 1
        user.username = result[0]

        return user



    def set_cookie_to_user(self, user_id):

        user = jsontree.jsontree()
        date_added = datetime.now()
        user.cookie = str(uuid.uuid1())

        query = """
            INSERT INTO cookie (userId, cookie, date_added) 
            VALUES (\'%s\', \'%s\', \'%s\')
        """ % (user_id, user.cookie, date_added)

        conn = self.connection
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            conn.commit()
            cursor.close()
            user.status = 1

        except Exception, e:
            self.restart_connection()
            sys.stdout.write(str(e))
            user.status = 0

        return user



    def is_logged(self, user_id, user_cookie):

        query = """
            SELECT userId, cookie FROM cookie WHERE cookie=\'%s\'
        """ % (user_cookie)

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

        except Exception, e:
            self.restart_connection()
            sys.stdout.write(e)
            return 0

        if(result == None):
            return 0

        elif (result[0] != user_id):
            return 0

        elif (result[0] == user_id):
            return 1

        else:
            return 0


    """
    Functions to return notification:

        1. positive_notification:

            returns the jsontree data of user_id which contains
            {
                "positive": [
                    {accoutnId, userId1, userId2, balance},
                    {},
                    {},
                    ... (10 max)
                ], 
                "name": [
                    {firstname lastname},
                    {},
                    {},
                    ... (10 max)
                ]
            }

        2. negetive_notification

            returns the jsontree data of user_id as
            {
                "negetive": [
                    {accoutnId, userId1, userId2, balance},
                    {},
                    {},
                    ... (10 max)
                ], 
                "name": [
                    {firstname lastname},
                    {},
                    {},
                    ... (10 max)
                ]
            }

        3. tracking_notification

            returns the jsontree data of user_id as
            {
                "unread":[
                    {noticeId, userId, notice},
                    {},
                    {},
                    ... (10 max)
                ]
            }
    """

    def positive_notification(self, user_id, count):

        error_msg = jsontree.jsontree()
        notice = jsontree.jsontree()

        notice.name = []

        # count = int(count)
        query = """
            SELECT accountId, userId1,
            userId2, balance
            FROM account WHERE
            userId1 = \'%s\' AND 
            confirmed_by_user1 = \'%s\' LIMIT 10 OFFSET \'%s\'
        """ % (user_id, False, count*10)

        cursor = self.connection.cursor()

        """
        size of notice.positive will be 10.
        """

        try:
            cursor.execute(query)
            notice.positive = cursor.fetchall()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        # notice.positive = result

        for res in notice.positive:

            query = """
                SELECT firstname, lastname from address
                WHERE userId = \'%s\'
            """ % (res[2])

            try:
                cursor.execute(query)
                result_name = cursor.fetchone()

            except Exception, e:
                self.restart_connection()
                error_msg.status = 0
                error_msg.message = str(e)
                return error_msg

            notice.name.append(result_name[0]+" "+result_name[1])

        cursor.close()
        notice.status = 1

        return notice



    def negetive_notification(self, user_id, count):

        error_msg = jsontree.jsontree()
        notice = jsontree.jsontree()

        notice.name = []
        # count = int(count)

        query = """
            SELECT accountId, userId1,
            userId2, balance
            FROM account WHERE
            userId2 = \'%s\' AND 
            confirmed_by_user2 = \'%s\' LIMIT 10 OFFSET \'%s\'
        """ % (user_id, False, count*10)

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
            notice.negetive = cursor.fetchall()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        for res in notice.negetive:

            query = """
                SELECT firstname, lastname from address
                WHERE userId = \'%s\'
            """ % (res[1])

            try:
                cursor.execute(query)
                result_name = cursor.fetchone()

            except Exception, e:
                self.restart_connection()
                error_msg.status = 0
                error_msg.message = str(e)
                return error_msg

            notice.name.append(result_name[0]+" "+result_name[1])

        cursor.close()
        notice.status = 1

        return notice



    def tracking_notification(self, user_id, count):

        error_msg = jsontree.jsontree()
        notice = jsontree.jsontree()
        # count = int(count)

        query = """
            SELECT noticeId, userId,
            notice FROM notification WHERE
            userId = \'%s\' AND 
            unread = \'%s\' LIMIT 10 OFFSET \'%s\'
        """ % (user_id, True, count)

        print query
        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
            notice.unread = cursor.fetchall()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        cursor.close()
        notice.status = 1

        return notice



    def create_balance(self, user):

        amount = user.amount
        mod = user.mod

        if (mod == 'positive'):
            positive = True

        else:
            positive = False

        fellow_username = user.fellow_username

        query = """
            SELECT userId FROM users
            WHERE username = \'%s\'
        """ % (fellow_username)

        conn = self.connection
        cursor = conn.cursor()

        error_msg = jsontree.jsontree()

        try:
            cursor.execute(query)
            result = cursor.fetchone()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            sys.stdout.write(e)
            return error_msg

        # print result

        if(result == None):
            error_msg.status = 0
            error_msg.message = "USERNAME_NOT_EXIST"
            return error_msg

        account_id = str(uuid.uuid1())
        
        ##TODO:
        ##If userid1 and userid2 already exists then
        ##Update table accordingly.

        if(positive):
            query = """
                INSERT INTO account (accountId,
                userId1, userId2, balance, is_positive,
                confirmed_by_user1, confirmed_by_user2)
                VALUES (\'%s\', \'%s\', \'%s\', \'%s\', 
                \'%s\', \'%s\', \'%s\')
            """ % (account_id, user.user_id, result[0], 
                amount, True, True, False)

        else:
            query = """
                INSERT INTO account (accountId,
                userId1, userId2, balance, is_positive,
                confirmed_by_user1, confirmed_by_user2)
                VALUES (\'%s\', \'%s\', \'%s\', \'%s\', 
                \'%s\', \'%s\', \'%s\')
            """ % (account_id, result[0], user.user_id, 
                amount, True, False, True)

        print query
        try:
            cursor.execute(query)
            conn.commit()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            sys.stdout.write(str(e))
            return error_msg

        error_msg.status = 1
        return error_msg



    def mark_notification_read(self, notice_id, user_id):

        error_msg = jsontree.jsontree()
        query = """
            UPDATE notification SET
            unread = \'%s\' WHERE
            noticeId = \'%s\' AND userId = \'%s\'
        """ % (False, notice_id, user_id)

        con = self.connection
        cursor = con.cursor()

        try:
            cursor.execute(query)
            con.commit()
            cursor.close()
            error_msg.status = 1

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)

        return error_msg



    def mark_accept(self, user):

        error_msg = jsontree.jsontree()

        account_id = user.account_id
        user_id = user.user_id

        query = """
            SELECT userId1, userId2 FROM account
            WHERE accountId = \'%s\'
        """ % (account_id)

        con = self.connection
        cursor = con.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        if(result == None):
            error_msg.status = 0
            error_msg.message = "Transaction not found."
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
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        try:
            cursor.execute(update_db_query)
            con.commit()
            cursor.close()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        error_msg.status = 1
        return error_msg



    def mark_decline(self, user):

        error_msg = jsontree.jsontree()

        account_id = user.account_id
        user_id = user.user_id

        query = """
            SELECT userId1, userId2 FROM account
            WHERE accountId = \'%s\'
        """ % (account_id)

        con = self.connection
        cursor = con.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        if(result == None):
            error_msg.status = 0
            error_msg.message = "Transaction not found."
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
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        try:
            cursor.execute(update_db_query)
            con.commit()
            cursor.close()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        error_msg.status = 1
        return error_msg



    def del_user_transaction(self, user):

        error_msg = jsontree.jsontree()
        account_id = user.account_id
        user_id = user.user_id

        query = """
            SELECT userId1 FROM account
            WHERE accountId = \'%s\'
        """ % (account_id)

        con = self.connection
        cursor = con.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        query = """
            DELETE FROM account
            WHERE accountId = \'%s\'
        """ % (account_id)

        if(result[0] != user_id):
            error_msg.status = 0
            error_msg.message = "You do not have right to modify that !!"
            return error_msg

        try:
            cursor.execute(query)
            con.commit()
            cursor.close()

        except Exception, e:
            self.restart_connection()
            error_msg.status = 0
            error_msg.message = str(e)
            return error_msg

        error_msg.status = 1
        return error_msg
