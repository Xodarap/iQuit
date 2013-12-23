# Creates db and tables

import rethinkdb as r

connection = r.connect('localhost', 28015)
r.db_create('iquit').run(connection)
r.db('iquit').table_create('people').run(connection)
connection.close()

