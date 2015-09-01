import os
import jinja2
from jinja2 import FileSystemLoader

e = jinja2.Environment(loader=FileSystemLoader('tpls/java'))


def camel_case(s):
    return ''.join([word.capitalize() for word in s.split('_')])


def camel_back(s):
    c = camel_case(s)
    return c[0].lower() + c[1:]


def getJavaFieldName(colName):
    try:
        return camel_back(colName[colName.index('_'):])
    except ValueError:
        return camel_back(colName)


def getJavaMethodName(colName):
    try:
        return camel_case(colName[colName.index('_'):])
    except ValueError:
        return camel_case(colName)


def getJavaType(field):
    return field.get_java_type()
    
def getTypeName(table):
    return "t_" + table.name
        

def create_java_getter(fieldName, fieldType, methodName):
    return """    public """ + fieldType + """ get""" + methodName + """() {
        return """ + fieldName + """;
    }"""


def create_java_setter(fieldName, fieldType, methodName):
    return """    public void set""" + methodName + """(""" + fieldType + """ """ + fieldName + """) {
        this.""" + fieldName + """ = """ + fieldName + """;
    }"""


def create_class_name(table):
    return camel_case(table.name)


def create_field_name(table):
    return camel_back(table.name)


type_package = 'domain'
iface_package = 'persistence'
impl_package = iface_package + '.impl'
service_sfx = 'SProcService'


def create_java_enum(table, package):
    out = "package " + package + ";\n\n"
    out += "public enum " + table.getClassName() + " {\n"
    values = []
    for v in table.values:
        values.append("    " + v)
    out += ",\n".join(values)
    out += "\n}\n"
    return out


def create_java_type(table, package):
    cols = []
    funcs = []
    fieldAnn = "    @DatabaseField\n"
    imports = {'de.zalando.typemapper.annotations.DatabaseField': 1,
		'de.zalando.typemapper.annotations.DatabaseType': 2}

    for f in table.fields:
        fieldName = getJavaFieldName(f.name)
        methodName = getJavaMethodName(f.name)
        typeName = getJavaType(f)
        col = fieldAnn
        if not f.isNullable:
            if typeName == 'String':
                col += "    @NotBlank\n"
                imports['org.hibernate.validator.constraints.NotBlank'] = 1
            else:
                col += "    @NotNull\n"
                imports['javax.validation.constraints.NotNull'] = 1
        if f.maxLength is not None and f.maxLength > 0:
            col += "    @Max(" + str(f.maxLength) + ")\n"
            imports['javax.validation.constraints.Max'] = 1
        col += "    private " + getJavaType(f) + " " + fieldName + ";\n"
        cols.append(col)
        funcs.append(create_java_getter(fieldName, getJavaType(f), methodName))
        funcs.append(create_java_setter(fieldName, getJavaType(f), methodName))

    for a in table.associations:
        if a.tableFrom == table:
            # single item
            fieldName = create_field_name(a.tableTo)
            className = create_class_name(a.tableTo)
            cols.append(fieldAnn + "    private " + className + " " + fieldName + ";\n")
            funcs.append(create_java_getter(fieldName, className, className))
            funcs.append(create_java_setter(fieldName, className, className))
        elif a.tableTo == table:
            # collection
            cols.append(fieldAnn + "    private List<" + create_class_name(a.tableFrom) + "> " + create_field_name(
                a.tableFrom) + "s;\n")

    source = "package " + package + ";\n"
    for k, v in imports.iteritems():
        source += "\nimport " + k + ";"
        
    source += "\n\n" + "@DatabaseType(name = " + getTypeName(table)  +", inheritance = true)"  + "\nclass " + table.getClassName() + " {\n"

    source += "\n".join(cols)
    source += "\n"

    source += "\n\n".join(funcs)

    source += "\n}\n"

    return source


def get_signatures_for_table(table):
    signatures = [(table.getClassName(), "create", table.getClassName()),
                  (table.getClassName(), "delete", table.getClassName()),
                  (table.getClassName(), "update", table.getClassName())]

    return signatures


def create_sproc_service_interface(table, package):
    t = e.get_template('sproc_interface.java')

    import_list = "\nimport " + package + type_package + "." + table.getClassName() + ";\n"
    package = "package " + package + iface_package + ";\n\n"

    sproc_list = []
    l = get_signatures_for_table(table)
    for (field_name, method_name, p) in l:
        lower_field_name = field_name[0].lower() + field_name[1:]
        sproc_list.append(
            "    public " + field_name + " " + method_name + "(" + field_name + " " + lower_field_name + ");")

    for ui in table.indexes:
        keys = []
        names = []
        for i in ui:
            f = table.fields[int(i) - 1]
            keys.append(getJavaType(f) + " " + getJavaFieldName(f.name))
            names.append(getJavaMethodName(f.name))
        sproc_list.append(
            "    public " + table.getClassName() + " getBy" + "".join(names) + "(" + ", ".join(keys) + ");")

    return t.render(interfaceName=table.getClassName() + service_sfx,
                    sprocList="\n".join(sproc_list),
                    importList=import_list,
                    package=package,
                    prefix=table.name)


def create_sproc_service_implementation(table, package):
    t = e.get_template('sproc_implementation.java')

    import_list = "\nimport " + package + type_package + "." + table.getClassName() + ";\n"
    import_list += "import " + package + iface_package + "." + table.getClassName() + service_sfx + ";\n"
    package = "package " + package + impl_package + ";\n\n"

    sproc_list = []
    l = get_signatures_for_table(table)

    for (field_name, method_name, p) in l:
        lower_field_name = field_name[0].lower() + field_name[1:]
        sproc_list.append(
            "    @Override\n    public " + field_name + " " + method_name + "(" + field_name + " " + lower_field_name + """) {
        return sproc.""" + method_name + """(""" + lower_field_name + """);
    }""")

    for ui in table.indexes:
        keys = []
        names = []
        types = []
        for i in ui:
            f = table.fields[int(i) - 1]
            types.append(getJavaType(f) + " " + getJavaFieldName(f.name))
            keys.append(getJavaFieldName(f.name))
            names.append(getJavaMethodName(f.name))
        sproc_list.append(
            "    @Override\n    public " + table.getClassName() + " getBy" + "".join(names) + "(" + ", ".join(types) + """) {
        return sproc.getBy""" + "".join(names) + "(" + ", ".join(keys) + """);
    }""")

    return t.render(interfaceName=table.getClassName() + service_sfx,
                    functionImplementations="\n\n".join(sproc_list),
                    datasourceProvider='SingleDataSourceProvider',
                    importList=import_list,
                    package=package)


def get_package_path(package):
    path = ['src', 'main', 'java']
    for word in package.split('.'):
        path.append(word)
    return os.sep.join(path)


def save_file(path, class_name, data):
    if not os.path.isdir(path):
        os.makedirs(path, 0755)
    fd = open(path + os.sep + class_name + ".java", "w")
    fd.write(data)
    fd.close()


def generate_code(table, package, path):
    if package != '':
        package += '.'

    pp = get_package_path(package + type_package)

    for k, v in table.complexTypes.iteritems():
        class_name = v.getClassName()
        if v.isEnum():
            src = create_java_enum(v, package + type_package)
        else:
            src = create_java_type(v, package + type_package)
        save_file(path + os.sep + pp, class_name, src)

    class_name = table.getClassName()
    src = create_java_type(table, package + type_package)
    save_file(path + os.sep + pp, class_name, src)

    pp = get_package_path(package + iface_package)
    class_name += service_sfx
    src = create_sproc_service_interface(table, package)
    save_file(path + os.sep + pp, class_name, src)

    pp = get_package_path(package + impl_package)
    class_name += 'Impl'
    src = create_sproc_service_implementation(table, package)
    save_file(path + os.sep + pp, class_name, src)
