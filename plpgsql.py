import os
import jinja2
from jinja2 import FileSystemLoader

e = jinja2.Environment(loader=FileSystemLoader('tpls'))


def getPGTypeFieldName(colName):
    return colName[colName.find('_') + 1:]


def getSProcName(schema, table):
    return table


def getTypeName(table):
    return "t_" + table.name


def getFieldNameForTable(table):
    return table.name


def create_pg_type(table):
    t = e.get_template('sql/type_definition.sql')

    colSource = []

    for f in table.fields:
        type = f.type
        if f.maxLength is not None and f.maxLength > 0:
            type += "(" + str(f.maxLength) + ")"
        colSource.append("""  """ + getPGTypeFieldName(f.name) + """ """ + type)

    for a in table.associations:
        colSource.append("""  """ + getFieldNameForTable(a.tableTo) + """ """ + getTypeName(a.tableTo))

    return t.render(name=getTypeName(table), columns=",\n".join(colSource))


def create_insert(table):
    t = e.get_template('sql/insert.sql')

    cols = []
    ins = []
    rets = []
    for f in table.fields:
        rets.append("    " + f.name)
        if not f.isSerial:
            cols.append("    " + f.name)
            ins.append("    p_in." + getPGTypeFieldName(f.name))

    columns = ",\n".join(cols)
    insertValues = ",\n".join(ins)
    returnColumns = ",\n".join(rets)

    return t.render(sprocName=getSProcName(table.schema, table.name),
                    returnType=getTypeName(table),
                    schema=table.schema,
                    tableName=table.name,
                    columns=columns,
                    insertValues=insertValues,
                    returnColumns=returnColumns)


def create_update(table):
    t = e.get_template('sql/update.sql')

    cols = []
    wheres = []
    rets = []
    for f in table.fields:
        rets.append("    " + f.name)
        if f.isSerial:
            cols.append("    " + f.name + " = COALESCE ( p_in." + getPGTypeFieldName(f.name) + ", " + f.name + " )")
            wheres.append("    " + f.name + " = p_in." + getPGTypeFieldName(f.name))

    updateColumns = ",\n".join(cols)
    whereColumns = ",\n".join(wheres)
    returnColumns = ",\n".join(rets)

    return t.render(sprocName=getSProcName(table.schema, table.name),
                    returnType=getTypeName(table),
                    schema=table.schema,
                    tableName=table.name,
                    updateColumns=updateColumns,
                    whereColumns=whereColumns,
                    returnColumns=returnColumns)


def create_delete(table):
    t = e.get_template('sql/delete.sql')

    cols = []
    rets = []
    for f in table.fields:
        rets.append("    " + f.name)
        if f.isSerial:
            cols.append("    " + f.name + " = p_in." + getPGTypeFieldName(f.name))

    whereColumns = ",\n".join(cols)
    returnColumns = ",\n".join(rets)

    return t.render(sprocName=getSProcName(table.schema, table.name),
                    returnType=getTypeName(table),
                    schema=table.schema,
                    tableName=table.name,
                    whereColumns=whereColumns,
                    returnColumns=returnColumns)


def create_select_pk(table):
    t = e.get_template('sql/select_using_uk.sql')

    cols = []
    wheres = []
    keys = []
    for f in table.fields:
        cols.append("    " + f.name)
        if f.isPk:
            wheres.append("    " + f.name + " = p_" + getPGTypeFieldName(f.name))
            keys.append("p_" + getPGTypeFieldName(f.name) + " " + f.type)

    for a in table.associations:
        if a.doFollow and a.tableFrom == table:
            cols.append("""    CASE WHEN (""" + a.getSourceTuple() + """) IS NOT NULL THEN
      (SELECT """ + a.tableTo.getSelectFieldListForType() + """
         FROM """ + a.tableTo.schema + "." + a.tableTo.name + """
        WHERE (""" + a.getSourceTuple() + ") = (" + a.getTargetTuple() + ")) ELSE NULL END")
        elif a.doFollow:
            cols.append(
                """ ARRAY ( SELECT """ + a.tableFrom.getSelectFieldListForType() + """ FROM """ + a.tableFrom.schema + "." + a.tableFrom.name + """ WHERE (""" + a.getSourceTuple() + """) = (""" + a.getTargetTuple() + """) ) """)

    selectColumns = ",\n".join(cols)
    whereColumns = ",\n".join(wheres)

    return t.render(sprocName=getSProcName(table.schema, table.name),
                    keyColumns=", ".join(keys),
                    returnType=getTypeName(table),
                    schema=table.schema,
                    tableName=table.name,
                    whereColumns=whereColumns,
                    selectColumns=selectColumns)


def generate_selects(sp, table):
    t = e.get_template('sql/select_using_uk.sql')
    file_name = getTypeName(table)

    cols = []
    for f in table.fields:
        cols.append("    " + f.name)
    selectColumns = ",\n".join(cols)

    for ui in table.indexes:
        keys = []
        wheres = []
        names = []
        for i in ui:
            f = table.fields[int(i) - 1]
            wheres.append("    " + f.name + " = p_" + getPGTypeFieldName(f.name))
            keys.append("p_" + getPGTypeFieldName(f.name) + " " + f.type)
            names.append(getPGTypeFieldName(f.name))
        proc_name = "_".join(names)
        src = t.render(sprocName=getSProcName(table.schema, table.name),
                       keyColumns=", ".join(keys),
                       uniqueKeyName=proc_name,
                       returnType=getTypeName(table),
                       schema=table.schema,
                       tableName=table.name,
                       whereColumns=",\n".join(wheres),
                       selectColumns=selectColumns)
        save_file(sp, file_name + '_get_by_' + proc_name, src)


def create_sprocs(table):
    ret = create_insert(table)
    ret += create_delete(table)
    ret += create_update(table)
    ret += create_select_pk(table)
    return ret


def save_file(path, file_name, data):
    if not os.path.isdir(path):
        os.makedirs(path, 0755)
    fd = open(path + os.sep + "20_" + file_name + ".sql", "w")
    fd.write(data)
    fd.close()


def generate_code(table, path):
    src = create_pg_type(table)
    file_name = getTypeName(table)
    save_file(path + os.sep + '03_types', file_name, src)

    sp = path + os.sep + '05_stored_procedures'
    src = create_insert(table)
    save_file(sp, file_name + '_create', src)
    src = create_update(table)
    save_file(sp, file_name + '_update', src)
    src = create_delete(table)
    save_file(sp, file_name + '_delete', src)
    generate_selects(sp, table)

