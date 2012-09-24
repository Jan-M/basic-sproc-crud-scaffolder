import argparse
import psycopg2

pg2javaMap = { 'text': 'String', 'integer': 'Integer' }

def getJavaType(pgType,isEnum,isArray,isAssociation):
    return pg2javaMap[pgType]

def getPGTypeFieldName ( colName ):
    return colName[2:]

def getJavaFieldName( colName ):
    return colName[2:]

def getSProcName(schema,table):
  return schema[0:1].upper() + schema[1:] + table[0:1].upper() + table[1:]

def create_pg_type ( name, fields ):
  source = ""
  source += """CREATE TYPE """ + name + """ AS ( \n"""

  colSource = []

  for name,cType,isPk,isSerial in fields:
    colSource.append("""  """ + getPGTypeFieldName ( name ) + """ """ + cType )
  
  source += ",\n".join(colSource)
  
  source += """\n);\n"""
  
  return source

def create_java_getter(fieldName,fieldType):
  return """  public """ + fieldType + """ get"""+fieldName+"""() {
      return """+fieldName+""";
  }"""

def create_java_setter(fieldName,fieldType):
  return """  public void set"""+fieldName+"""("""+fieldType+""" a"""+fieldType+""") {
      """+fieldName+""" = a"""+fieldType+""";
  }"""

def create_java_type ( name, fields ):
  source = "class " + name + " {\n"
  
  cols = []
  funcs = []

  for name,cType,isPk,isSerial in fields:
    cols.append ( "  private " +getJavaType(cType,False,False,False) + " " + getJavaFieldName(name) + ";" )
    funcs.append ( create_java_getter ( getJavaFieldName(name) , getJavaType(cType,False,False,False) ) )
    funcs.append ( create_java_setter ( getJavaFieldName(name) , getJavaType(cType,False,False,False) ) )

  source += "\n".join(cols)
  source += "\n"
 
  source += "\n".join(funcs)
  
  source += "\n}\n"
  return source

def create_insert(schema,tableName,pgTypeName,fields):
  source = """CREATE OR REPLACE FUNCTION insert"""+getSProcName(schema,tableName)+"""(p_in """+pgTypeName+""") RETURNS SETOF """+pgTypeName+""" AS
$$
DECLARE """

  source += """
BEGIN
  RETURN QUERY INSERT INTO """+schema+"""."""+tableName+"""(  
"""

  cols = []
  for name,cType,isPk,isSerial in fields:
    if False == isSerial:
      cols.append ("    " + name )

  source += ",\n".join(cols)

  source += """) 
  SELECT
"""

  cols = []
  for name,cType,isPk,isSerial in fields:
    if False == isSerial:
      cols.append ( "    p_in." + getPGTypeFieldName ( name ) )

  source += ",\n".join(cols)
  
  source += """
  RETURNING
"""

  cols = []
  for name,cType,isPk,isSerial in fields:
      cols.append ( "    " + name )

  source += ",\n".join(cols)
  source += ";"

  source += """
END;
"""

  source += """$$ LANGUAGE 'plpgsql' SECURITY DEFINER;
"""
  return source

def create_update(schema,tableName,pgTypeName,fields):
  source = """CREATE OR REPLACE FUNCTION update"""+getSProcName(schema,tableName)+"""(p_in """+pgTypeName+""") RETURNS SETOF """+pgTypeName+""" AS
$$
DECLARE """

  source += """
BEGIN
  RETURN QUERY UPDATE """+schema+"""."""+tableName+""" SET 
"""

  cols = []
  for name,cType,isPk,isSerial in fields:
    if False == isSerial:
      cols.append ("    " + name + " = COALESCE ( p_in." + getPGTypeFieldName ( name ) + ", " + name + " )" )

  source += ",\n".join(cols)

  source += """
  WHERE
"""

  cols = []
  for name,cType,isPk,isSerial in fields:
    if True == isSerial:
      cols.append ( "    " + name + " = p_in." + getPGTypeFieldName ( name ) )

  source += ",\n".join(cols)
  
  source += """
  RETURNING
"""

  cols = []
  for name,cType,isPk,isSerial in fields:
      cols.append ( "    " + name )

  source += ",\n".join(cols)
  source += ";"

  source += """
END;
"""

  source += """$$ LANGUAGE 'plpgsql' SECURITY DEFINER;
"""

  return source

def create_delete(schema,tableName,pgTypeName,fields):
  source = """CREATE OR REPLACE FUNCTION delete"""+getSProcName(schema,tableName)+"""(p_in """+pgTypeName+""") RETURNS SETOF """+pgTypeName+""" AS
$$
DECLARE """

  source += """
BEGIN
  RETURN DELETE FROM """+schema+"""."""+tableName+""" """

  source += """
  WHERE
"""

  cols = []
  for name,cType,isPk,isSerial in fields:
    if True == isSerial:
      cols.append ( "    " + name + " = p_in." + getPGTypeFieldName ( name ) )

  source += ",\n".join(cols)
  
  source += """
  RETURNING
"""

  cols = []
  for name,cType,isPk,isSerial in fields:
      cols.append ( "    " + name )

  source += ",\n".join(cols)
  source += ";"

  source += """
END;
"""

  source += """$$ LANGUAGE 'plpgsql' SECURITY DEFINER;
""";

  return source

def create_select_pk(schema,tableName,pgTypeName,fields):
  source = """CREATE OR REPLACE FUNCTION select"""+getSProcName(schema,tableName)+"""(p_in """+pgTypeName+""") RETURNS SETOF """+pgTypeName+""" AS
$$
DECLARE """

  source += """
BEGIN
  RETURN QUERY SELECT
"""

  cols = []
  for name,cType,isPk,isSerial in fields:
      cols.append ("    " + name )

  source += ",\n".join(cols)

  source += """
  FROM
    """+schema+"""."""+tableName+""" 
"""

  source += """  WHERE
"""

  cols = []
  for name,cType,isPk,isSerial in fields:
    if True == isPk:
      cols.append ( "    " + name + " = p_in." + getPGTypeFieldName ( name ) )

  source += ",\n".join(cols)
  
  source += """;
"""

  source += """
END;
"""
  source += """$$ LANGUAGE 'plpgsql' SECURITY DEFINER;
"""
  return source


def create_sprocs(schema,tableName,pgTypeName,fields):
  print create_insert(schema,tableName,pgTypeName,fields)
  print create_delete(schema,tableName,pgTypeName,fields)
  print create_update(schema,tableName,pgTypeName,fields)
  print create_select_pk(schema,tableName,pgTypeName,fields)

def get_fields(schema,name):
    return [('p_id','integer',True,True),('p_name','text',False,False),('p_first_name','text',False,False)]

def create_for_table(schema,name):
  fields = get_fields(schema,name)
  
  print create_pg_type ( name + "Type" , fields )
  print create_java_type ( name + "Type" , fields )
  print create_sprocs(schema, name, name + "Type", fields)
  
  pass

def main():
  create_for_table('public','parent')

if __name__ == "__main__":
    main()
