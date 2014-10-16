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

