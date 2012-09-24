import jinja2
from jinja2 import FileSystemLoader

e = jinja2.Environment(loader = FileSystemLoader('tpls'))

def getPGTypeFieldName ( colName ):
  return colName[2:]

def getSProcName(schema,table):
  return schema[0:1].upper() + schema[1:] + table[0:1].upper() + table[1:]

def create_pg_type ( name, fields ):
  t = e.get_template('sql/type_definition.sql')

  colSource = []

  for f in fields:
    colSource.append("""  """ + getPGTypeFieldName ( f.name ) + """ """ + f.type )
  
  return t.render(name=name,columns = ",\n".join(colSource))

def create_insert(schema,tableName,pgTypeName,fields):
  t = e.get_template('sql/insert.sql')

  cols = []
  for f in fields:
    if False == f.isSerial:
      cols.append ("    " + f.name )

  columns = ",\n".join(cols)

  cols = []
  for f in fields:
    if False == f.isSerial:
      cols.append ( "    p_in." + getPGTypeFieldName ( f.name ) )

  insertValues = ",\n".join(cols)

  cols = []
  for f in fields:
      cols.append ( "    " + f.name )

  returnColumns = ",\n".join(cols)

  return t.render(sprocName  = getSProcName(schema,tableName),
           returnType = pgTypeName,
           schema=schema,
           tableName=tableName,
           columns=columns,
           insertValues=insertValues,
           returnColumns=returnColumns)

def create_update(schema,tableName,pgTypeName,fields):
  t = e.get_template('sql/update.sql')

  cols = []
  for f in fields:
    if False == f.isSerial:
      cols.append ("    " + f.name + " = COALESCE ( p_in." + getPGTypeFieldName ( f.name ) + ", " + f.name + " )" )

  updateColumns = ",\n".join(cols)

  cols = []
  for f in fields:
    if True == f.isSerial:
      cols.append ( "    " + f.name + " = p_in." + getPGTypeFieldName ( f.name ) )

  whereColumns = ",\n".join(cols)
  

  cols = []
  for f in fields:
      cols.append ( "    " + f.name )

  returnColumns = ",\n".join(cols)

  return t.render(sprocName  = getSProcName(schema,tableName),
           returnType = pgTypeName,
           schema=schema,
           tableName=tableName,
           updateColumns=updateColumns,
           whereColumns=whereColumns,
           returnColumns=returnColumns)

def create_delete(schema,tableName,pgTypeName,fields):
  t = e.get_template('sql/delete.sql')
  
  cols = []
  for f in fields:
    if True == f.isSerial:
      cols.append ( "    " + f.name + " = p_in." + getPGTypeFieldName ( f.name ) )

  whereColumns = ",\n".join(cols)
  
  cols = []
  for f in fields:
      cols.append ( "    " + f.name )

  returnColumns = ",\n".join(cols)

  return t.render(sprocName  = getSProcName(schema,tableName),
           returnType = pgTypeName,
           schema=schema,
           tableName=tableName,
           whereColumns=whereColumns,
           returnColumns=returnColumns)

def create_select_pk(schema,tableName,pgTypeName,fields):
  t = e.get_template('sql/select_pk.sql')

  cols = []
  for f in fields:
      cols.append ("    " + f.name )

  selectColumns = ",\n".join(cols)

  cols = []
  for f in fields:
    if True == f.isPk:
      cols.append ( "    " + f.name + " = p_in." + getPGTypeFieldName ( f.name ) )

  whereColumns = ",\n".join(cols)

  return t.render(sprocName  = getSProcName(schema,tableName),
           returnType = pgTypeName,
           schema=schema,
           tableName=tableName,
           whereColumns=whereColumns,
           selectColumns=selectColumns)


def create_sprocs(schema,tableName,pgTypeName,fields):
  print create_insert(schema,tableName,pgTypeName,fields)
  print create_delete(schema,tableName,pgTypeName,fields)
  print create_update(schema,tableName,pgTypeName,fields)
  print create_select_pk(schema,tableName,pgTypeName,fields)
