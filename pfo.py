import sqlite3
import inspect

# test dummy
class TestModel:
	def __init__(self, num):
		self.number = num
	def setNumber(self, num):
		self.number = num
	def getNumber(self):
		return self.number

# mem = inspect.getmembers(TestModel(1))


# for member in mem:
# 	if inspect.ismethod(member[1]) and member[0][:3] == "set":
# 		print member[0]

# Now assume every attribute belongs to simple type

class Database:
	def __init__(self, name = None):
		if (name is None):
			name = "database.db"
		self.connector = sqlite3.connect(name)
		self.cursor = self.connector["__conn"].cursor()
	def createTable(self, object):
		setGetPairs = Database.__getSetGetPairs(object)
		primaryKey = Database.__getPrimaryKey(object)
