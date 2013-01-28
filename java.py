import os
import sys
import jinja2
from jinja2 import FileSystemLoader

e = jinja2.Environment(loader = FileSystemLoader('tpls/java'))

def camel_case(s):
    return ''.join([ word.capitalize() for word in s.split('_')])

def camel_back(s):
    c = camel_case(s)
    return c[0].lower() + c[1:]

def getJavaFieldName( colName ):
    return camel_back(colName[colName.index('_'):])

def getJavaMethodName( colName ):
    return camel_case(colName[colName.index('_'):])

def getJavaType(field):
    return field.get_java_type()

def create_java_getter(fieldName, fieldType, methodName):
  return """  public """ + fieldType + """ get"""+methodName+"""() {
      return """ + fieldName + """;
  }"""

def create_java_setter(fieldName, fieldType, methodName):
  
  return """  public void set""" + methodName + """(""" + fieldType + """ """ + fieldName + """) {
      this.""" + fieldName+""" = """ + fieldName + """;
  }"""

def create_class_name ( table ) :
    return camel_case ( table.name )

def create_field_name ( table ) :
    return camel_back ( table.name )

type_package = 'domain'
iface_package = 'persistence'
impl_package = iface_package + '.impl'
service_sfx = 'SProcService'

def create_java_type ( table, package ):
  package += type_package;

  source = "package " + package + ";\n\nclass " + table.getClassName() + " {\n"

  cols = []
  funcs = []

  for f in table.fields:
    fieldName = getJavaFieldName(f.name)
    methodName = getJavaMethodName(f.name)
    fieldAnn = "  @DatabaseField\n" 
    col = fieldAnn
    if not f.isNullable:
        col += "  @NotNull\n"
    if f.maxLength is not None and f.maxLength > 0:
        col += "  @Max(" + str(f.maxLength) + ")\n"
    col += "  private " +getJavaType(f) + " " + fieldName + ";\n"
    cols.append ( col )
    funcs.append ( create_java_getter ( fieldName , getJavaType(f), methodName ) )
    funcs.append ( create_java_setter ( fieldName , getJavaType(f), methodName ) )

  for a in table.associations:
    if a.tableFrom == table: # single item
        fieldName = create_field_name(a.tableTo)
        className = create_class_name(a.tableTo)
        cols.append ( fieldAnn + "  private " + className + " " + fieldName + ";\n" )
        funcs.append ( create_java_getter ( fieldName , className, className ) )
        funcs.append ( create_java_setter ( fieldName , className, className ) )
    elif a.tableTo == table: # collection
        cols.append ( fieldAnn + "  private List<" + create_class_name(a.tableFrom) + "> " + create_field_name ( a.tableFrom ) + "s;\n" )

  source += "\n".join(cols)
  source += "\n"
 
  source += "\n\n".join(funcs)
  
  source += "\n}\n"

  return source

def get_signatures_for_table ( table ):
    signatures = []
    
    signatures.append ( ( table.getClassName() , "insert", table.getClassName() ) )
    signatures.append ( ( table.getClassName() , "delete", table.getClassName() ) )
    signatures.append ( ( table.getClassName() , "update", table.getClassName() ) )
#    signatures.append ( ( table.getClassName() , "selectPk" + table.getClassName() , table.getClassName() ) )

    return signatures

def create_sproc_service_interface( table, package ):
    t = e.get_template('sproc_interface.java')

    import_list = "\nimport " + package + type_package + "." + table.getClassName() + ";\n"
    package = "package " + package + iface_package + ";\n\n"

    sproc_list = []
    l = get_signatures_for_table ( table )
    for (field_name, method_name, p) in l:
        lower_field_name = field_name[0].lower() + field_name[1:]
        sproc_list.append( "  public " + field_name + " " + method_name + "(" + field_name + " "+lower_field_name+");" )

    keys = []
    for f in table.fields:
      if True == f.isPk:
        keys.append( getJavaType(f) + " " + getJavaFieldName(f.name) )
    sproc_list.append( "  public " + table.getClassName() + " getById(" + ", ".join(keys) + ");" )

    return t.render(interfaceName=table.getClassName()+service_sfx,
                    sprocList="\n".join( sproc_list ),
                    importList=import_list,
                    package=package,
                    prefix=table.name)

def create_sproc_service_implementation( table, package ):
    t = e.get_template('sproc_implementation.java')

    import_list = "\nimport " + package + type_package + "." + table.getClassName() + ";\n"
    import_list += "import " + package + iface_package + "." + table.getClassName() + service_sfx + ";\n"
    package = "package " + package + impl_package + ";\n\n"

    sproc_list = []
    l = get_signatures_for_table ( table )

    for (field_name, method_name, p) in l:
        lower_field_name = field_name[0].lower() + field_name[1:]
        sproc_list.append( "    @Override\n    public " + field_name + " " + method_name + "(" + field_name + " " + lower_field_name + """) {
        return sproc."""+method_name+"""(""" + lower_field_name + """);
    }""" )

    keys = []
    types = []
    for f in table.fields:
      if True == f.isPk:
        types.append( getJavaType(f) + " " + getJavaFieldName(f.name) )
        keys.append( getJavaFieldName(f.name) )

    sproc_list.append( "    @Override\n    public " + table.getClassName() + " getById(" + ", ".join(types) + """) {
        return sproc.getById(""" + ", ".join(keys) + """);
    }""" )

    return t.render(interfaceName=table.getClassName()+service_sfx,
                    functionImplementations="\n\n".join( sproc_list ),
                    datasourceProvider='DatasourceProvider',
                    importList=import_list,
                    package=package)

def get_package_path( package ):
    path = ['src', 'main', 'java']
    for word in package.split('.'):
        path.append( word )
    return os.sep.join(path)

def save_file( path, class_name, data ):
    if not os.path.isdir(path):
      os.makedirs(path, 0755)
    fd = open(path + os.sep + class_name + ".java", "w")
    fd.write(data)
    fd.close()

def generate_code( table, package, path ):
  if package != '':
    package += '.'

  pp = get_package_path(package + type_package)
  class_name = table.getClassName();
  src = create_java_type ( table, package )
  save_file( path + os.sep + pp, class_name, src )

  pp = get_package_path(package + iface_package)
  class_name += service_sfx;
  src = create_sproc_service_interface( table, package )
  save_file( path + os.sep + pp, class_name, src )

  pp = get_package_path(package + impl_package)
  class_name += 'Impl';
  src = create_sproc_service_implementation( table, package )
  save_file( path + os.sep + pp, class_name, src )
