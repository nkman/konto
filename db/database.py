import os, sys
import psycopg2
import uuid
import jsontree
from datetime import datetime

"""
Five Tables:
    1. Users -> Contains user details:
        userId: (it will generate here)
        username:
        password:

    2. Address -> Contains user Name and Address:
        userId: (taken from User table)
        firstname:
        lastname:

    3. Account -> Contains user account details:
        accountId: (it will generate here)
        userId1: (taken from User table)
        userId2: (taken from User table)
        balance:
        is_positive: boolean (if positive => 2 owes 1)
        confirmed_by_user1: boolean
        confirmed_by_user2: boolean

    4. MId -> For Notifications:
        made_by: userId
        made_to: userId
        approved: boolean (will be approved by made_to user)

    5. Cokiees -> sessions
        userId: 
        cookie:

"""

class Database:

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

    def user_table(self):

        """
        userId: (it will generate here)
        username:
        password:
        """

        query = """
                CREATE TABLE IF NOT EXISTS users (
                    id bigserial primary key,
                    username varchar(20) NOT NULL,
                    password varchar(20) NOT NULL,
                    date_added timestamp default NULL,
                    userId varchar(36) NOT NULL,
                    constraint u_constrainte1 unique (username),
                    constraint u_constrainte2 unique (userId)
                );
        """

        cursor = self.connection.cursor()
        conn = self.connection

        try:
            cursor.execute(query)
            conn.commit()
            sys.stdout.write("created table users\n")
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)
            cursor.close()
            sys.stdout.write(e)

    def address_table(self):

        """
        userId: (taken from User table)
        firstname:
        lastname:
        """

        query = """
                CREATE TABLE IF NOT EXISTS address (
                    id bigserial primary key,
                    addressId varchar(36) NOT NULL,
                    userId varchar(36) NOT NULL,
                    firstname varchar(20) NOT NULL,
                    lastname varchar(20) NOT NULL,
                    phone varchar(20) default NULL,
                    date_added timestamp default NULL,
                    constraint u_constrainte3 unique (addressId)
                );
        """

        cursor = self.connection.cursor()
        conn = self.connection

        try:
            cursor.execute(query)
            conn.commit()
            sys.stdout.write("created table address\n")
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)
            cursor.close()
            sys.stdout.write(e)

    def account_table(self):

        """
        accountId: (it will generate here)
        userId1: (taken from User table)
        userId2: (taken from User table)
        balance:
        is_positive: boolean (if positive => 2 owes 1)
        confirmed_by_user1: boolean
        confirmed_by_user2: boolean
        """

        query = """
                CREATE TABLE IF NOT EXISTS account (
                    id bigserial primary key,
                    accountId varchar(36) NOT NULL,
                    userId1 varchar(36) NOT NULL,
                    userId2 varchar(36) NOT NULL,
                    balance int,
                    is_positive boolean,
                    confirmed_by_user1 boolean,
                    confirmed_by_user2 boolean,
                    date_added timestamp default NULL,
                    constraint u_constrainte4 unique (accountId)
                );
        """

        cursor = self.connection.cursor()
        conn = self.connection

        try:
            cursor.execute(query)
            conn.commit()
            sys.stdout.write("created table account\n")
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)
            cursor.close()
            sys.stdout.write(e)


    def Med_table(self):

        """
        made_by: userId
        made_to: userId
        approved: boolean (will be approved by made_to user)
        accountId: 
        """

        query = """
                CREATE TABLE IF NOT EXISTS mid (
                    id bigserial primary key,
                    midId varchar(36) NOT NULL,
                    made_by varchar(20),
                    made_to varchar(20),
                    accountId varchar(36),
                    date_added timestamp default NULL,
                    constraint u_constrainte5 unique (accountId)
                );
        """

        cursor = self.connection.cursor()
        conn = self.connection

        try:
            cursor.execute(query)
            conn.commit()
            sys.stdout.write("created table mid\n")
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)
            cursor.close()
            sys.stdout.write(e)

    def Cookie(self):

        """
        userId: 
        cookie:
        """

        query = """
                CREATE TABLE IF NOT EXISTS cookie (
                    id bigserial primary key,
                    userId varchar(36) NOT NULL,
                    cookie varchar(36) NOT NULL,
                    date_added timestamp default NULL
                );
        """

        cursor = self.connection.cursor()
        conn = self.connection

        try:
            cursor.execute(query)
            conn.commit()
            sys.stdout.write("created table cookie\n")
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)
            cursor.close()
            sys.stdout.write(e)

    def reset_connection(self):
        sys.stdout.write("Closing the connection.\n")
        self.connection.close()
        sys.stdout.write("Connection closed\nStarting connection to database")
        self.connect()
        sys.stdout.write("Connection has been established.")

    def close_connection(self):
        self.connection.close()

    def drop_all(self):
        
        query = [
            'DROP TABLE users', 
            'DROP TABLE account', 
            'DROP TABLE address',
            'DROP TABLE cookie',
            'DROP TABLE mid'
            ]

        conn = self.connection
        cursor = conn.cursor()

        for q in query:
            try:
                cursor.execute(q)
                sys.stdout.write("Deleted all tables !!")

            except Exception, e:
                self.debug_InternalError(e)
                sys.stdout.write(e)

        try:
            conn.commit()
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)
            sys.stdout.write(e)

    def user_found(self, username):

        query = 'SELECT * FROM users WHERE username=\'%s\'' % username
        cursor = self.connection.cursor()

        try:
            cursor.execute(query)

        except Exception, e:
            self.debug_InternalError(e)
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

        if(self.user_found(username) == 1):
            msg = jsontree.jsontree()
            msg.status = 0
            msg.message = "username exists !!"
            return msg

        _id = uuid.uuid1()
        date_added = datetime.now()

        query = """
            INSERT INTO users(username, password, userId, date_added)
            VALUES (\'%s\', \'%s\', \'%s\', \'%s\')
        """ % (username, password, str(_id), date_added)

        cursor = self.connection.cursor()
        conn = self.connection

        msg = jsontree.jsontree()

        try:
            cursor.execute(query)   
            conn.commit()
            sys.stdout.write("New user created")
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)

            sys.stdout.write(e)
            cursor.close()
            msg.status = 0
            msg.message = "user creation failed !!"
            return msg

        try:
            msg = self.create_address(user)

        except Exception, e:
            self.debug_InternalError(e)
            sys.stdout.write(e)
            msg.status = 0
            msg.message = "user address creation failed !!"
            return msg

        if (msg.status == 1):
            msg.message = "user and user address created successfully !!"
        else:
            msg.message = "user created but adderss creation failed !!"
            #delete_created_user()

        return msg

    def create_address(self, user):

        username = user['username']
        firstname = user['firstname']
        lastname = user['lastname']
        phone = user['phone']

        _id = uuid.uuid1()

        query = """
            SELECT userId FROM users WHERE username=\'%s\'
        """ % username

        cursor = self.connection.cursor()
        conn = self.connection

        msg = jsontree.jsontree()

        try:
            cursor.execute(query)
        except Exception, e:
            if (e == 'InternalError'):
                self.reset_connection()

            msg.status = 0
            # msg.message = "Unable to commit create address query !!"
            msg.message = str(e)
            return msg #how to handle this -> rollbacks ?

        date_added = datetime.now()
        userId = cursor.fetchone()[0]
        cursor.close()

        query = """
            INSERT INTO address(addressId, userId, firstname, lastname, phone, date_added)
            VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')
        """ % (str(_id), userId, firstname, lastname, phone, date_added)

        cursor = conn.cursor()

        try:
            cursor.execute(query)
            conn.commit()
            sys.stdout.write("New adderss created !")
            cursor.close()
            msg.status = 1
            msg.message = "whatever"
            return msg

        except Exception, e:
            self.debug_InternalError(e)
            cursor.close()
            msg.status = 0
            # msg.message = "Unable to commit create address query !!"
            sys.stdout.write(e)
            msg.message = str(e)
            return msg #how to handle this -> rollbacks ?

    def is_logged(self, user):

        query = """
            SELECT userId, cookie FROM cookie WHERE cookie=\'%s\'
        """ % (user.user_cookie)

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)
            sys.stdout.write(e)

        if(result == None):
            return 0

        elif (result[0] != user.user_id):
            return 0

        elif (result[0] == user.user_id):
            return 1

        else:
            return 0

    def verify_user_credential(self, user):

        username = user.username
        password = user.password

        query = """
            SELECT password, userId FROM users WHERE username=\'%s\'
        """ % (username)

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)
            sys.stdout.write(e)

        msg = jsontree.jsontree()
        if(result == None):
            msg.status = 0
            msg.message = "No such user exists !!"

        elif(result[0] == password):
            msg.status = 1
            msg.userId = result[1]
            msg.username = username

        else:
            msg.status = 0
            msg.message = "Wrong password."

        return msg

    def set_user_cookie(self, user):

        user_id = user.user_id
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

        except Exception, e:
            self.debug_InternalError(e)
            sys.stdout.write(e)

        return user

    def logout(self, user):

        user_id = user.user_id
        cookie = user.cookie

        query = """
            DELETE FROM cookie WHERE cookie=\'%s\'
        """ % (cookie)

        conn = self.connection
        cursor = conn.cursor()

        msg = jsontree.jsontree()

        try:
            cursor.execute(query)
            conn.commit()
            cursor.close()
            msg.status = 1
            msg.message = "Logged out."

        except Exception, e:
            self.debug_InternalError(e)
            msg.status = 0
            msg.message = e
            sys.stdout.write(e)

        return msg

    def insert_into_account_table(self, account):

        account.account_id = str(uuid.uuid1())

        account_id = account.account_id
        user_id1 = account.user_id1
        user_id2 = account.user_id2
        balance = account.balance
        is_positive = account.is_positive
        confirmed_by_user1 = account.confirmed_by_user1
        confirmed_by_user2 = account.confirmed_by_user2
        date_added = datetime.now()

        query = """
                INSERT INTO account (
                    accountId,  userId1,
                    userId2 ,   balance,
                    is_positive,    confirmed_by_user1,
                    confirmed_by_user2, date_added
                ) VALUES (
                    \'%s\', \'%s\', \'%s\', \'%s\', 
                    \'%s\', \'%s\', \'%s\', \'%s\'
                )
        """ % (account_id, user_id1, user_id2, balance, is_positive,
                confirmed_by_user1, confirmed_by_user2, date_added)

        conn = self.connection
        cursor = conn.cursor()

        msg = jsontree.jsontree()

        try:
            cursor.execute(query)
            conn.commit()
            cursor.close()
            msg.status = 1
            msg.message = "Inserted into account."

        except Exception, e:
            self.debug_InternalError(e)
            msg.status = 0
            msg.message = e
            sys.stdout.write()

        return msg

    def debug_InternalError(self, e):

        if(e == 'InternalError'):
            self.reset_connection()

        else:
            self.reset_connection()
            pass

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
            error_msg.status = 0
            error_msg.message = e
            return error_msg

        if(result == None):
            error_msg.status = 0
            error_msg.message = "THat username does not exists !!"
            return error_msg

        """
        accountId: (it will generate here)
        userId1: (taken from User table)
        userId2: (taken from User table)
        balance:
        is_positive: boolean (if positive => 2 owes 1)
        confirmed_by_user1: boolean
        confirmed_by_user2: boolean
        """

        account_id = str(uuid.uuid1())
        
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

        try:
            cursor.execute(query)
            conn.commit()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = e
            return error_msg

        """
        made_by: userId
        made_to: userId
        approved: boolean (will be approved by made_to user)
        """

        query = """
            INSERT INTO mid(made_by, made_to, approved)
            VALUES (\'%s\', \'%s\',\'%s\')
        """ % (user.user_id, result[0], False)

        try:
            cursor.execute(query)
            conn.commit()

        except Exception, e:
            error_msg.status = 0
            error_msg.message = e
            return error_msg

        error_msg.status = 1
        return error_msg
