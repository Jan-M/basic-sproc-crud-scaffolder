import jinja2
from jinja2 import FileSystemLoader

e = jinja2.Environment(loader = FileSystemLoader('tpls/java'))

def getJavaFieldName( colName ):
    return colName[2:]

pg2javaMap = { 'text': 'String', 'integer': 'Integer' }

def getJavaType(field):
    return pg2javaMap[field.type]

def create_java_getter(fieldName,fieldType):
  return """  public """ + fieldType + """ get"""+fieldName+"""() {
      return """+fieldName+""";
  }"""

def create_java_setter(fieldName,fieldType):
  return """  public void set"""+fieldName+"""("""+fieldType+""" a"""+fieldType+""") {
      """+fieldName+""" = a"""+fieldType+""";
  }"""

def create_class_name ( table ) :
    return table.name[0:1].upper() + table.name[1:]

def create_field_name ( table ) :
    return table.name

def create_java_type ( table ):
  source = "@DatabaseType\nclass " + create_class_name(table) + " {\n"
  
  cols = []
  funcs = []

  for f in table.fields:
    cols.append ( "  @DatabaseField\n  private " +getJavaType(f) + " " + getJavaFieldName(f.name) + ";" )
    funcs.append ( create_java_getter ( getJavaFieldName(f.name) , getJavaType(f) ) )
    funcs.append ( create_java_setter ( getJavaFieldName(f.name) , getJavaType(f) ) )

  for a in table.associations:
    if a.tableFrom == table: # single item
        cols.append ( "@DatabaseField\n  private " + create_class_name(a.tableTo) + " " + create_field_name ( a.tableTo ) + ";" )
        funcs.append ( create_java_getter ( create_field_name ( a.tableTo ) , create_class_name(a.tableTo) ) )
        funcs.append ( create_java_setter ( create_field_name ( a.tableTo ) , create_class_name(a.tableTo) ) )
    elif a.tableTo == table: # collection
        cols.append ( "@DatabaseField\n  private List<" + create_class_name(a.tableFrom) + "> " + create_field_name ( a.tableFrom ) + "s;" )

  source += "\n".join(cols)
  source += "\n"
 
  source += "\n".join(funcs)
  
  source += "\n}\n"

  return source

def create_sproc_service_interface():
    pass

def create_sproc_service_implementation():
    pass
