import os
import psycopg2

class Database:

	def __init__(self, config):

		self.host = config['host']
		self.port = config['port']
		self.user = config['user']
		self.password = config['password']
		self.database = config['database']


	def connect(self):

		self.connection = psycopg2.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.database)

	def create_table(self, table):

		