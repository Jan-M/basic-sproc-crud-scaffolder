import jinja2
from jinja2 import FileSystemLoader

e = jinja2.Environment(loader = FileSystemLoader('tpls'))

def getPGTypeFieldName ( colName ):
  return colName[2:]

def getSProcName(schema,table):
  return schema[0:1].upper() + schema[1:] + table[0:1].upper() + table[1:]

def getTypeName(table):
  return table.name[0:1].upper() + table.name[1:]

def getFieldNameForTable(table):
  return table.name  

def create_pg_type ( table ):
  t = e.get_template('sql/type_definition.sql')

  colSource = []

  for f in table.fields:
    colSource.append("""  """ + getPGTypeFieldName ( f.name ) + """ """ + f.type )

  for a in table.associations:
    colSource.append("""  """ + getFieldNameForTable ( a.tableTo ) + """ """ + getTypeName(a.tableTo) )
  
  return t.render( name = getTypeName(table) ,columns = ",\n".join(colSource))

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

def create_select_pk(table, schema,tableName,pgTypeName,fields):
  t = e.get_template('sql/select_pk.sql')

  cols = []
  for f in fields:
      cols.append ("    " + f.name )

  for a in table.associations:
    if a.doFollow and a.tableFrom == table:
      cols.append ( """    CASE WHEN ("""+a.getSourceTuple()+""") IS NOT NULL THEN 
      (SELECT """+ a.tableTo.getSelectFieldListForType() +"""
         FROM """ + a.tableTo.schema+"."+a.tableTo.name+"""
        WHERE ("""+a.getSourceTuple()+") = ("+a.getTargetTuple()+")) ELSE NULL END" )
    elif a.doFollow:
        cols.append ( """ ARRAY ( SELECT """ + a.tableFrom.getSelectFieldListForType() + """ FROM """ + a.tableFrom.schema+"."+a.tableFrom.name+ """ WHERE (""" + a.getSourceTuple() + """) = (""" + a.getTargetTuple() + """) ) """ )

  selectColumns = ",\n".join(cols)

  cols = []
  for f in table.fields:
    if True == f.isPk:
      cols.append ( "    " + f.name + " = p_in." + getPGTypeFieldName ( f.name ) )



  whereColumns = ",\n".join(cols)

  return t.render(sprocName  = getSProcName(schema,tableName),
           returnType = pgTypeName,
           schema=schema,
           tableName=tableName,
           whereColumns=whereColumns,
           selectColumns=selectColumns)


def create_sprocs(table, pgTypeName,fields):
  print create_insert(table.schema,table.name,pgTypeName,fields)
  print create_delete(table.schema,table.name,pgTypeName,fields)
  print create_update(table.schema,table.name,pgTypeName,fields)
  print create_select_pk(table, table.schema,table.name,pgTypeName,fields)
