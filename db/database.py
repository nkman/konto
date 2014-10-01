import os
import psycopg2
import uuid
import jsontree

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

        self.connection = psycopg2.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.database)


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
            print "created table users\n"
            cursor.close()

        except Exception, e:
            cursor.close()
            raise e

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
            print "created table address\n"
            cursor.close()

        except Exception, e:
            cursor.close()
            raise e

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
            print "created table account\n"
            cursor.close()

        except Exception, e:
            cursor.close()
            raise e


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
                    constraint u_constrainte5 unique (accountId)
                );
        """

        cursor = self.connection.cursor()
        conn = self.connection

        try:
            cursor.execute(query)
            conn.commit()
            print "created table mid\n"
            cursor.close()

        except Exception, e:
            cursor.close()
            raise e

    def close_connection(self):
        self.connection.close()

    def user_found(self, username):

        query = 'SELECT * FROM users WHERE username=\'%s\'' % username

        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchone()
        cursor.close()

        if (result == None):
            return 0
        else:
            print "Username exists"
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
        query = """
            INSERT INTO users(username, password, userId)
            VALUES (\'%s\', \'%s\', \'%s\')
        """ % (username, password, str(_id))

        cursor = self.connection.cursor()
        conn = self.connection

        msg = jsontree.jsontree()

        try:
            cursor.execute(query)   
            conn.commit()
            print "New user created"
            cursor.close()

        except Exception, e:
            cursor.close()
            msg.status = 0
            msg.message = "user creation failed !!"
            return msg

        try:
            msg = self.create_address(user)

        except Exception, e:
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
            msg.status = 0
            # msg.message = "Unable to commit create address query !!"
            msg.message = str(e)
            return msg #how to handle this -> rollbacks ?

        userId = cursor.fetchone()[0]
        cursor.close()

        query = """
            INSERT INTO address(addressId, userId, firstname, lastname, phone)
            VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')
        """ % (str(_id), userId, firstname, lastname, phone)

        cursor = conn.cursor()

        try:
            cursor.execute(query)
            conn.commit()
            print "New adderss created !"
            cursor.close()
            msg.status = 1
            msg.message = "whatever"
            return msg

        except Exception, e:
            cursor.close()
            msg.status = 0
            # msg.message = "Unable to commit create address query !!"
            print e
            msg.message = str(e)
            return msg #how to handle this -> rollbacks ?
