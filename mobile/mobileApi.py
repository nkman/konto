import psycopg2

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
            error_msg.userId = result[1]
            error_msg.username = username

        else:
            error_msg.status = 0
            error_msg.message = "Wrong password."

        return msg

    def create_user(self, user):

        username = user['username']
        password = user['password']

        msg = jsontree.jsontree()

        if(self.user_found(username) == 1):
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
            conn.commit()
            sys.stdout.write("New user created")
            cursor.close()

        except Exception, e:
            self.debug_InternalError(e)

            sys.stdout.write(e)
            cursor.close()
            msg.status = 0
            msg.message = "user creation failed !!"
            return json.dumps(msg)

        try:
            msg = self.create_address(user)

        except Exception, e:
            self.debug_InternalError(e)
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
            self.debug_InternalError(e)

            msg.status = 0
            msg.message = str(e)
            return msg

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
            return msg

        except Exception, e:
            self.debug_InternalError(e)
            cursor.close()
            msg.status = 0
            sys.stdout.write(e)
            msg.message = str(e)
            return msg

