def getPGTypeFieldName ( colName ):
  return colName[2:]

def getSProcName(schema,table):
  return schema[0:1].upper() + schema[1:] + table[0:1].upper() + table[1:]

def create_pg_type ( name, fields ):
  source = ""
  source += """CREATE TYPE """ + name + """ AS ( \n"""

  colSource = []

  for f in fields:
    colSource.append("""  """ + getPGTypeFieldName ( f.name ) + """ """ + f.type )
  
  source += ",\n".join(colSource)
  
  source += """\n);\n"""
  
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
  for f in fields:
    if False == f.isSerial:
      cols.append ("    " + f.name )

  source += ",\n".join(cols)

  source += """) 
  SELECT
"""

  cols = []
  for f in fields:
    if False == f.isSerial:
      cols.append ( "    p_in." + getPGTypeFieldName ( f.name ) )

  source += ",\n".join(cols)
  
  source += """
  RETURNING
"""

  cols = []
  for f in fields:
      cols.append ( "    " + f.name )

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
  for f in fields:
    if False == f.isSerial:
      cols.append ("    " + f.name + " = COALESCE ( p_in." + getPGTypeFieldName ( f.name ) + ", " + f.name + " )" )

  source += ",\n".join(cols)

  source += """
  WHERE
"""

  cols = []
  for f in fields:
    if True == f.isSerial:
      cols.append ( "    " + f.name + " = p_in." + getPGTypeFieldName ( f.name ) )

  source += ",\n".join(cols)
  
  source += """
  RETURNING
"""

  cols = []
  for f in fields:
      cols.append ( "    " + f.name )

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
  for f in fields:
    if True == f.isSerial:
      cols.append ( "    " + f.name + " = p_in." + getPGTypeFieldName ( f.name ) )

  source += ",\n".join(cols)
  
  source += """
  RETURNING
"""

  cols = []
  for f in fields:
      cols.append ( "    " + f.name )

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
  for f in fields:
      cols.append ("    " + f.name )

  source += ",\n".join(cols)

  source += """
  FROM
    """+schema+"""."""+tableName+""" 
"""

  source += """  WHERE
"""

  cols = []
  for f in fields:
    if True == f.isPk:
      cols.append ( "    " + f.name + " = p_in." + getPGTypeFieldName ( f.name ) )

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
