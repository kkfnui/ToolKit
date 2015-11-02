#!/usr/bin/python
# -*- coding:utf-8
__author__ = 'lvfei'


# id int(8) not null primary key auto_increment,
# rec_algorithm_test_id int(8) not null,
#    package_name char(100) not null,
#    package_title char(255) not null,
#    package_icon Text not null,
#    package_info Text not null,
#    partin_num TINYINT not null,
#    score float not null,
#    create_by char(50) not null,
#    create_datetime datetime not null,
#    update_datetime datetime not null

def get_lines(filename):
    with open(filename) as f:
        return f.readlines()


def parse_feild(lines):
    class Item:
        pass

    feilds = []
    for line in lines:
        raw = line.strip()
        keys = raw.split(" ")
        item = Item()
        item.sql_key = keys[0]
        item.sql_value = keys[1]
        item.key = get_feild_java_name(keys[0])
        item.value = get_java_type_from_sql(keys[1])
        feilds.append(item)

    return feilds


def get_java_type_from_sql(type):
    value = type.lower()
    if value == "float":
        return "Float"

    if value.startswith("char"):
        return "String"

    if value == "datetime":
        return "Timestamp"

    if value == "tinyint":
        return "Short"

    if value == "text":
        return "String"

    if value.startswith("int"):
        return "Long"


def get_feild_java_name(feild):
    words = feild.split("_")
    if len(words) == 1:
        return feild

    feild = words[0]
    for word in words[1:]:
        begin = word[0].upper()
        word = begin + word[1:]
        feild += word

    return feild


def generate_felid_java_code(name, type):
    java_type = type
    java_name = name
    declare = "private " + java_type + " " + java_name + ";"

    method_name = java_name[0].upper() + java_name[1:]
    getter = "public " + java_type + " get" + method_name + "(){\n"
    getter += "\t return this." + java_name + ";\n"
    getter += "}\n"

    setter = "public void set" + method_name + "(" + java_type + " " + java_name + ") {\n"
    setter += "\tthis." + java_name + " = " + java_name + ";\n"
    setter += "}\n"

    return declare + "\n" + getter + "\n" + setter + "\n"


def generate_entify(name, feilds):
    code = ""
    code += "import java.sql.Timestamp;\n"
    code += "\n"

    code += "public class " + name + "{\n"

    for item in feilds:
        tmp = generate_felid_java_code(item.key, item.value)
        code += tmp
    code += "}\n"

    return code


def generate_mapper(name, feilds):
    code = ""
    code += "import org.springframework.jdbc.core.RowMapper;\n"
    code += "import java.sql.ResultSet;\n"
    code += "import java.sql.SQLException;\n"

    code += "\n"
    code += "public class " + name + "Mapper implements RowMapper {\n"

    code += "\t@Override\n"
    code += "\tpublic Object mapRow(ResultSet rs, int rowNum) throws SQLException {\n"
    code += "\t\t" + name + " entity = new " + name + "();\n"
    for feild in feilds:
        code += "\t\tentity.set" + feild.key[0].upper() + feild.key[
                                                          1:] + "(rs.get" + feild.value + "(\"" + feild.sql_key + "\"));\n"

    code += "\t\treturn entity;\n"
    code += "\t}\n"
    code += "}\n"
    return code


def generate_get(name):
    code = "public " + name + " getById(long id) { \n"
    code += "\tString sql = \"select * from \"+ TABLE_NAME + \" where id = ?\";\n"
    code += "\treturn (" + name + ") jdbcTemplate.queryForObject(sql, new Object[]{id}, new " + name + "Mapper());\n"
    code += "}\n"
    return code


def generate_add(name, feilds):
    code = "public long add(" + name + " entity) {\n"
    code += "String sql = \"insert into \"+ TABLE_NAME + \" (\" +\n"

    keys = ""
    placeholders = ""
    values = ""
    for item in feilds[:len(feilds) - 2]:
        if item.sql_key != "id":
            keys += "\t\"" + item.sql_key + ", \" +\n"
            placeholders += "?, "
            getter = "get" + item.key[0].upper() + item.key[1:] + "()"
            values += "\tentity." + getter + ",\n"

    item = feilds[len(feilds) - 1]
    keys += "\t\"" + item.sql_key
    placeholders += "?"
    getter = "get" + item.key[0].upper() + item.key[1:] + "()"
    values += "\tentity." + getter

    code += keys + ")\" +\n"
    code += "\t\" values\"+\n"
    code += "\t\"(" + placeholders + ")\";\n"

    code += "\n"
    code += "jdbcTemplate.update(sql, new Object[]{\n"
    code += values
    code += "});\n"
    code += "\n"

    code += "String queryId = \"select max(id) from \"+TABLE_NAME+\" where create_by =?\";\n"

    code += "long id = jdbcTemplate.queryForObject(\n"
    code += "\t\tqueryId, new Object[]{entity.getCreateBy()}, Long.class);\n"
    code += "return id;\n"

    code += "}\n"
    return code


def generate_update(name, feilds):
    code = "public boolean update(" + name + " entity) {\n"
    sql = "\t String sql = \"update \"+ TABLE_NAME +\n"
    java = "\tint rows = jdbcTemplate.update(sql, new Object[]{\n"
    for item in feilds:
        if item.sql_key != "id":
            sql += "\t\t\"set " + item.sql_key + "=?, \"+\n"
            java += "\t\tentity.get" + item.key[0].upper() + item.key[1:] + "(),\n"

    sql += "\t\t\"where id = ?\";"
    java += "\t\tentity.getId()});\n"
    code += sql
    code += "\n"
    code += "\n"
    code += java
    code += "\n"
    code += "\treturn rows >= 1;\n"

    code += "}\n"
    return code


def generate_remove():
    code = "public boolean remove(long id) {\n"
    code += "\tString sql = \"delete from \"+ TABLE_NAME +\" where id = ?\";\n"
    code += "\tint rows = jdbcTemplate.update(sql, new Object[]{id});\n"
    code += "\treturn rows >= 1;\n"
    code += "}\n"
    return code


def generate_list(name):
    code = ""
    code += "public QueryResult<" + name + "> getList(int page, int rowNum, String sortBy, String order) {\n"
    code += "\tint pos = Math.max((page - 1) * rowNum, 0);\n"
    code += "\tString sql = \"select * from \"+ TABLE_NAME +\" order by \" + sortBy + \" \" + order +" \
            " \" limit \" + Integer.toString(pos) + \",\" + Integer.toString(rowNum);\n"

    code += "\tList<" + name + "> list = (List<" + name + ">) jdbcTemplate.query(sql, new " + name + "Mapper());"

    code += "\tString countSql = \"select count(*) from \"+ TABLE_NAME " + ";"
    code += "\tint count = jdbcTemplate.queryForObject(countSql, Integer.class);\n"
    code += "\n"

    code += "\tQueryResult<" + name + "> result = new QueryResult<" + name + ">(rowNum);\n"
    code += "\tint totalPage = (count + rowNum -1) / rowNum;\n"
    code += "\tresult.setTotal(totalPage);\n"
    code += "\tresult.setPage(page);\n"
    code += "\tresult.setRecords(count);\n"
    code += "\tresult.setRows(list);\n"
    code += "\n"
    code += "\treturn result;\n"
    code += "}\n"
    return code


def generate_dao(name, table, feilds):
    code = ""
    code += "import org.springframework.jdbc.core.JdbcTemplate;\n"
    code += "import com.xunlei.recommend.web.console.common.QueryResult;\n"
    code += "import java.util.List;\n"
    code += "\n"
    code += "public class " + name + "Dao {\n"
    code += "\tprivate JdbcTemplate jdbcTemplate;\n"
    code += "\tpublic void setJdbcTemplate(JdbcTemplate jdbcTemplate) {this.jdbcTemplate = jdbcTemplate;}\n"
    code += "\tprivate static String TABLE_NAME = \"" + table + "\";\n"

    code += "\n"
    code += generate_get(name)

    code += "\n"
    code += generate_add(name, feilds)

    code += "\n"
    code += generate_remove()

    code += "\n"
    code += generate_update(name, feilds)

    code += "\n"
    code += generate_list(name)

    code += "}\n"

    return code


def generate_jqgrid(feilds):
    code = ""

    for item in feilds:
        code += "{\n"
        code += "\tname: \'" + item.key + "\',\n"
        code += "\tindex: \'" + item.sql_key + "\',\n"
        code += "\twidth: 100,\n"
        code += "\talign: \'center\',\n"
        code += "\trequired: true,\n"
        code += "},\n"

    return code


def param_check():
    pass


def main():
    lines = get_lines("sql.txt")
    feilds = parse_feild(lines)
    name = "RecommendAlgorithmTestSample"
    dao = generate_dao(name, "test_package_sample", feilds)
    mapper = generate_mapper(name, feilds)
    entity = generate_entify(name, feilds)

    with open("./result/" + name + "Dao.java", "w") as fd:
        fd.write(dao)

    with open("./result/" + name + "Mapper.java", "w") as fm:
        fm.write(mapper)

    with open("./result/" + name + ".java", "w") as fe:
        fe.write(entity)

    with open("./result/" + name + ".jqgrid.txt", "w") as fj:
        jqgrid = generate_jqgrid(feilds)
        fj.write(jqgrid)


if __name__ == '__main__':
    main()
