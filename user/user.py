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
