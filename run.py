import argparse
import psycopg2

import plpgsql
import java

import psycopg2
import psycopg2.extras

connection_string = ""

def setConnectionString(conn_string):
    global connection_string
    connection_string = conn_string

def getConnection():
    conn = psycopg2.connect(connection_string)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SET work_mem TO '64MB';")
    cur.close()
    return conn

def closeConnection(c):
    c.close()

def getAssociationsForTable(schema,table):
    conn = getConn()
    cursor = conn.cursor()

def getFieldsForTable(schame,table):
  conn = getConn();
  cursor = conn.cursor()
  cursor.execute("""select column_name, data_type, column_default, is_nullable,
                           (select column_name in ( select column_name
                                                      from information_schema.key_column_usage kcu,
                                                           information_schema.table_constraints tc
                                                     where tc.table_name = c.table_name
                                                       and tc.table_schema = c.table_schema
                                                       and kcu.constraint_name = tc.constraint_name
                                                       and tc.constraint_type = 'PRIMARY KEY' ) ) as is_primary_part
                      from information_schema.columns c
                     where table_name = '"""+table+"""'
                       and table_schema = '"""+schema+"""'
                     order by ordinal_position""")

  l = []
  for r in cursor:
    l.append(Field (r[0],r[1],isPk=r[4],isSerial=r[2][0:7]=='nextval') )

  return l


class Table ( object ):
    def __init__(self,schema,name,fields=[]):
        self.name = name
        self.schema = schema
        self.fields = fields
        self.associations = []
        self.children = []

    def addField(self, f):
        self.fields.append(f)

    def addAssociation (self, a ):
        self.associations.append(a)

    def addChild (self, c ):
        self.children.append(c)

    def getSelectFieldListForType(self):
        l = []
        for f in self.fields:
            l.append(f.name)
        return ",".join(l)

    def getClassName(self):
        return java.camel_case(self.name)

class Association ( object ):
    def __init__(self, tableFrom, tableTo , colMap , doFollow = False):
        self.tableFrom = tableFrom
        self.tableTo = tableTo
        self.colMap = colMap        
        self.doFollow = doFollow

    def getSourceTuple(self):
        l = []
        for k in self.colMap:
            l.append(k)
        return ",".join(l)

    def getTargetTuple(self):
        l = []
        for k in self.colMap:
            l.append(self.colMap[k])
        return ",".join(l)

class Field(object):
    def __init__(self, name, t, isSerial = False, isPk = False, isEnum = False, isArray = False, isComplex = False):
        self.isPk = isPk
        self.type = t
        self.name = name
        self.isEnum = isEnum
        self.isArray = isArray
        self.isComplex = isComplex
        self.isSerial = isSerial

class Enum(object):
    def __init__(self, schema, name, values = []):
        self.name = name
        self.schema = schema
        self.values = values

def get_fields(schema,name):
  pass

def create_for_table(schema,name):
  parentT = Table('public','parent',[Field('p_id','integer',isPk=True,isSerial=True), Field('p_name','text'), Field('p_first_name','text'), Field('p_parent_data_id','integer') ])
  parentDataT = Table('public','parent_data', [Field('pd_id','integer',isSerial=True,isPk=True),Field('pd_street','text'),Field('pd_city','text')])

  parentT.addAssociation( Association(parentT,parentDataT,{'p_parent_data_id':'pd_id'}, True) )

  m = { 'public.parent':parentT, 'public.parent_data':parentDataT }
  
  print plpgsql.create_pg_type ( parentT )
  print plpgsql.create_pg_type ( parentDataT )
  print java.create_java_type ( parentT )
  print java.create_java_type ( parentDataT )
  print plpgsql.create_sprocs( parentT, name + "Type", parentT.fields)
  print java.create_sproc_service_interface( parentT )
  print java.create_sproc_service_implementation( parentT )

def main():
  argp = argparse.ArgumentParser(description='Scaffolder')
  argp.add_argument('-H', '--host', dest='host', default='localhost')
  argp.add_argument('-U', '--user', dest='user')
  argp.add_argument('-D', '--database', dest='database')
  argp.add_argument('-T', '--table', dest='table')
  args = argp.parse_args()

  if args.table == None:
    create_for_table('public','parent')
  else:
    pass

if __name__ == "__main__":
    main()
