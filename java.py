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

def create_java_type ( name, fields ):
  source = "@DatabaseType\nclass " + name + " {\n"
  
  cols = []
  funcs = []

  for f in fields:
    cols.append ( "  @DatabaseField\n  private " +getJavaType(f) + " " + getJavaFieldName(f.name) + ";" )
    funcs.append ( create_java_getter ( getJavaFieldName(name) , getJavaType(f) ) )
    funcs.append ( create_java_setter ( getJavaFieldName(name) , getJavaType(f) ) )

  source += "\n".join(cols)
  source += "\n"
 
  source += "\n".join(funcs)
  
  source += "\n}\n"

  return source
