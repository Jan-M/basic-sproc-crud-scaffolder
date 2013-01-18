import jinja2
from jinja2 import FileSystemLoader

e = jinja2.Environment(loader = FileSystemLoader('tpls/java'))

def camel_case(s):
    return ''.join([ word.capitalize() for word in s.split('_')])

def camel_back(s):
    c = camel_case(s)
    return c[0].lower() + c[1:]

def getJavaFieldName( colName ):
    return camel_back(colName[2:])

pg2javaMap = { 'text': 'String', 'integer': 'Integer', 'bigint' : 'Long', 'timestamp without time zone' : 'Date' , 'character varying' : 'String' , 'smallint' : 'Integer' , 'character' : 'String' }

def getJavaType(field):
    return field.get_java_type()

def create_java_getter(fieldName,fieldType):
  return """  public """ + fieldType + """ get"""+fieldName+"""() {
      return """+fieldName+""";
  }"""

def create_java_setter(fieldName,fieldType):
  return """  public void set"""+fieldName+"""("""+fieldType+""" a"""+fieldType+""") {
      """+fieldName+""" = a"""+fieldType+""";
  }"""

def create_class_name ( table ) :
    return camel_case ( table.name )

def create_field_name ( table ) :
    return camel_back ( table.name )

def create_java_type ( table ):
  source = "@DatabaseType\nclass " + table.getClassName() + " {\n"
  
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

def get_signatures_for_table ( table ):
    signatures = []
    
    signatures.append ( ( table.getClassName() , "insert" + table.getClassName() , table.getClassName() ) )
    signatures.append ( ( table.getClassName() , "delete" + table.getClassName() , table.getClassName() ) )
    signatures.append ( ( table.getClassName() , "update" + table.getClassName() , table.getClassName() ) )
    signatures.append ( ( table.getClassName() , "selectPk" + table.getClassName() , table.getClassName() ) )

    return signatures

def create_sproc_service_interface( table ):
    t = e.get_template('sproc_interface.java')

    sproc_list = ""
    l = get_signatures_for_table ( table )
    for (r,n,p) in l:
        sproc_list += "  public " + r + " " + n + "( " + r + " a"+r+" );\n"

    return t.render(interfaceName=table.getClassName()+"Service",
                    sprocList=sproc_list)

def create_sproc_service_implementation( table ):
    t = e.get_template('sproc_implementation.java')

    sproc_list = ""
    l = get_signatures_for_table ( table )

    for (r,n,p) in l:
        sproc_list += "    public " + r + " " + n + "( " + r + " a"+r+""" ) {
        return sproc."""+n+"""( a"""+r+""");
    }\n\n"""

    return t.render( interfaceName=table.getClassName()+"Service",
                     functionImplementations=sproc_list,
                     datasourceProvider='BitMapDatasourceProvider' )
