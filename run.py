import argparse
import psycopg2

import plpgsql
import java

class Table ( object ):
    def __init__(self,name,schema):
        self.name = name
        self.schema = schema
        self.fields = []

    def addField(f):
        self.fields.append(f)
    

class Association ( object ):
    def __init__(self, tableFrom, tableTo , colMap , doFollow = False):
        self.tableFrom = tableFrom
        self.talbeTo = tableTo
        self.colMap = colMap        
        self.doFollow = doFollow

class Field(object):
    def __init__(self, name, t, isSerial = False, isPk = False, isEnum = False, isArray = False, isComplex = False, isFk = False, doFollow = False):
        self.isFk = isFk
        self.isPk = isPk
        self.type = t
        self.name = name
        self.isEnum = isEnum
        self.isArray = isArray
        self.isComplex = isComplex
        self.doFollow = doFollow
        self.isSerial = isSerial

        self.associations = []

    def addAssociation(a):
        self.associations.append(a)

def get_fields(schema,name):
    return [Field('p_id','integer',isPk=True,isSerial=True), Field('p_name','text'), Field('p_first_name','text') ]

def create_for_table(schema,name):
  fields = get_fields(schema,name)
  
  print plpgsql.create_pg_type ( name + "Type" , fields )
  print java.create_java_type ( name + "Type" , fields )
  print plpgsql.create_sprocs(schema, name, name + "Type", fields)

def main():
  create_for_table('public','parent')

if __name__ == "__main__":
    main()
