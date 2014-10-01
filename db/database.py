import os
import psycopg2

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
                CREATE TABLE IF NOT EXISTS sers (
                    userId bigserial primary key,
                    username varchar(20) NOT NULL,
                    password varchar(20) NOT NULL,
                    date_added timestamp default NULL,
                    constraint u_constrainte unique (username)
                );
        """

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
        except Exception, e:
            raise e

    def address_table(self):

        """
        userId: (taken from User table)
        firstname:
        lastname:
        """

        query = """
                CREATE TABLE IF NOT EXISTS address (
                    addressId bigserial primary key,
                    userId varchar(20) NOT NULL,
                    firstname varchar(20) NOT NULL,
                    lastname varchar(20) NOT NULL,
                    phone varchar(20),
                    date_added timestamp default NULL
                );
        """

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
        except Exception, e:
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
                    accountId bigserial primary key,
                    userId1 varchar(20) NOT NULL,
                    userId2 varchar(20) NOT NULL,
                    balance int,
                    is_positive boolean,
                    confirmed_by_user1 boolean,
                    confirmed_by_user2 boolean,
                    date_added timestamp default NULL
                );
        """

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
        except Exception, e:
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
                    midId bigserial primary key,
                    made_by varchar(20),
                    made_to varchar(20),
                    accountId varchar(20)
                );
        """

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
        except Exception, e:
            raise e


    def user_found(self, username):

        query = 'SELECT * FROM User WHERE username=%s' % username

        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchone()

        if (len(result) == 0):
            return 0
        else:
            return 1


    def create_user(self, user):

        username = user['username']
        password = user['password']

        if(user_found(username)):
            return 0

        query = 'INSERT INTO users(username, password) VALUES (%s, %s)' % username, password

        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
        except Exception, e:
            print e
            return e

        return 1

    def create_address(self, user):

        username = user['username']
        firstname = user['firstname']
        lastname = user['lastname']
        bhawan = user['bhawan']
        roomno = user['roomno']

        query = 'SELECT userId FROM users WHERE username=%s' % username
        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
        except Exception, e:
            print e
            return e #how to handle this -> rollbacks ?

        userId = cursor.fetchone()
        print userId