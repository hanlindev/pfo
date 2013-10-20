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

class Faculty:
        def __init__(self, id="fid", name="soc"):
                self.Id = id
                self.Name = name
        def setId(self, id):
                self.Id = id
        def getId(self):
                return self.Id
        def setName(self, name):
                self.Name = name
        def getName(self):
                return self.Name
        def getPrimaryKey(self):
                return ["Id"]

class Student:
        def __init__(self, id = "id", name = "name", faculty = Faculty()):
                self.Id = id
                self.Name = name
                self.Faculty = faculty
        def setId(self, id):
                self.Id = id
        def setName(self, name):
                self.Name = name
        def setFaculty(self, faculty):
                self.Faculty = faculty
        def getId(self):
                return self.Id
        def getName(self):
                return self.Name
        def getFaculty(self):
                return self.Faculty
        def getPrimaryKey(self):
                return ["Id"]



# mem = inspect.getmembers(TestModel(1))


# for member in mem:
#       if inspect.ismethod(member[1]) and member[0][:3] == "set":
#               print member[0]

# Now assume every attribute belongs to simple type

PrimitiveTypes = [int, str, bool, float]
PythonTypeToSqlNameMap = {int: "INTEGER", str: "TEXT", float: "REAL", bool: "INTEGER"}

PrimaryKey = "PrimaryKey"
ForeignKey = "ForeignKey"
NotKey = "NotKey"

class QueryResult:
        def __init__(self, successful, msg, result = None):
                self.isSuccessful = successful
                self.message = msg
                self.result = result

class Database:
        def __init__(self, name = None):
                if (name is None):
                        name = "database.db"
                self.connector = sqlite3.connect(name)
                self.cursor = self.connector.cursor()
                self.tables = set()
        def createTable(self, model):
                if (self.__contains(model)):
                        return QueryResult(False, "Unable to create table - one already exists")
                else:
                        try:
                                columnAttributes = self.__getColumnAttributes(model)
                                combinedField = Database.__combineFieldToString(columnAttributes)
                                queryString = "CREATE TABLE %s(%s);" % (model.__class__.__name__, combinedField)
                                self.cursor.execute(queryString)
                                return QueryResult(True, "Table created")
                        except Exception as e:
                                return QueryResult(False, "Unable to create table: " + e.args[0])

        def __contains(self, model):
                return model.__class__.__name__ in self.tables

        def __getColumnAttributes(self, model):
                def getAttribute(method):
                        members = inspect.getmembers(model)
                        result = set()
                        for mem in members:
                                if (inspect.ismethod(mem[1]) and mem[0][:3] == method):
                                        print mem[0][0:3] #for debugging
                                        result.add(mem[0][3:])
                        return result

                result = {}

                #Get all column attribute names
                attributeNames = set()
                primary = model.getPrimaryKey()
                setMethods = getAttribute("set")
                getMethods = getAttribute("get")
                print setMethods #for debugging
                print getMethods #for debugging
                for attrName in setMethods:
                        if (attrName in getMethods):
                                attributeNames.add(attrName)
                print attributeNames#for debugging
                #Determine attribute type
                for attrName in attributeNames:
                        getattr(model, attrName)#for debugging
                        dummyData = getattr(model, attrName)
                        dummyType = type(dummyData)
                        if (attrName in primary):
                                if (dummyType in PrimitiveTypes):
                                        result[attrName] = (dummyType, PrimaryKey)
                                else:
                                        raise Exception("Complex primary key")
                        elif (dummyType not in PrimitiveTypes):
                                if (inspect.isclass(dummyType)):
                                        self.createTable(dummyData)
                                        foreignKeyNames = dummyData.getPrimaryKey()
                                        if (len(foreignKeyNames) == 0):
                                                raise Exception("No primary key in referenced table")
                                        for foreignKey in foreignKeyNames:
                                                keyType = type(getattr(dummyData, foreignKey))
                                                keyName = keyType.__name__
                                                result[keyName] = (keyType, ForeignKey, dummyType.__name__)
                                else:
                                        raise Exception("Unknown foreign key type")
                        else:
                                result[attrName] = (type(dummyData), NotKey)
                return result

        @staticmethod
        def __combineFieldToString(fields):
                result = ""
                FieldFormat = "%s %s"
                primaryKeys, foreignKeys = set(), set()
                comma = ""
                print fields #for debugging
                #Add fields
                for fieldName in fields:
                        print fieldName#for debugging
                        result += comma + (FieldFormat % (fieldName, PythonTypeToSqlNameMap[fields[fieldName][0]]))
                        comma = ","
                        fieldKeyType = fields[fieldName][1]
                        if (fieldKeyType == PrimaryKey):
                                primaryKeys.add(fieldName)
                        elif (fieldKeyType == ForeignKey):
                                foreignKeys.add(fieldName)
                #Add primary constraint
                if (len(primaryKeys) > 0):
                        pKeyFormat = ", PRIMARY KEY (%s)"
                        keyNameListString = ""
                        comma = ""
                        for keyName in primaryKeys:
                                keyNameListString += comma + keyName
                                comma = ","
                        result += pKeyFormat % (keyNameListString,)
                #Add foreign key constraint
                if (len(foreignKeys) > 0):
                        foundNew = True
                        foundTables = set()
                        while foundNew:
                                foundNew = False
                                foreignKeyFormat = ", FOREIGN KEY(%s) REFERENCES %s(%s)"
                                nameListString, referencedNameListString = "", ""
                                comma = ""
                                foreignTableName = ""
                                for keyName in foreignKeys:
                                        keyTuple = fields[keyName]
                                        if (foreignTableName == "" or foreignTableName == keyTuple[2]):
                                                foundTables.add(keyTuple[2])
                                                foreignTableName = keyTuple[2]
                                                foundNew = True
                                                nameListString += comma + keyName
                                                referencedNameListString += comma + keyName.split(":")[1]
                                                foreignTableName = keyName.split("")
                                                comma = ","
                                if (foundNew):
                                        result += foreignKeyFormat % (nameListString, foreignTableName, referencedNameListString)
                print result #for debugging
                return result

db = Database("test.db")
result = db.createTable(Student())
