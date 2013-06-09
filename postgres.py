from parse import parse_csv, tagstring_to_list, replace_all


def sql_field_inject(query_template):
    return query_template.format(
        u",".join(programme_fields),
        u",".join([u"'{" + field + u"}'"
                   for field in programme_fields]))


def tagstring_to_postgres_array(tagstring):
    return list_to_postgres_array(tagstring_to_list(tagstring))


def list_to_postgres_array(some_list):
    return replace_all(unicode(some_list), {
            '[': '{',
            ']': '}',
            "'": '"',
            'u"': '"',
            "u'": "'"
            })


programme_fields = {
    'pid': 'varchar(12)',
    'complete_title': 'varchar(256)',
    'media_type': "media_type",
    'masterbrand': 'varchar(40)',
    'brand_pid': 'varchar(12)',
    'is_clip': 'boolean',
    'tags': 'varchar[]'}

print u"""
BEGIN TRANSACTION;

DROP TABLE IF EXISTS availability_window;
DROP TABLE IF EXISTS programme_category;
DROP TABLE IF EXISTS programme;
DROP TABLE IF EXISTS subcategory;
DROP TABLE IF EXISTS category;
DROP TYPE IF EXISTS media_type;

CREATE TABLE category (
\tid\t\tvarchar(40),
\ttitle\t\tvarchar(50),
\tparent\t\tvarchar(40),
\tPRIMARY KEY\t(id)
);

CREATE TYPE media_type AS ENUM ('audio', 'video');

CREATE TABLE programme ("""

print ",\n".join(["\t{}{}{}".format(
            field_name,
            '\t' if len(field_name) > 7 else '\t\t',
            field_type)
                  for field_name, field_type
                  in programme_fields.iteritems()]) + ','
print """\tPRIMARY KEY\t(pid)
);

CREATE TABLE programme_category (
\tpid\t\tvarchar(40)
\t\t\tREFERENCES programme(pid),
\tcategory_id\tvarchar(40)
\t\t\tREFERENCES category(id),
\tPRIMARY KEY\t(pid, category_id)
);

CREATE TABLE availability_window (
\tpid\t\tvarchar(12)
\t\t\tREFERENCES programme(pid),
\tstart_time\ttimestamp,
\tend_time\ttimestamp,
\tservice\t\tvarchar(40),
\tPRIMARY KEY\t(pid, start_time, service)
);
"""

programme_dicts, categories, subcategories = parse_csv()

for category in categories:
    print u"INSERT INTO category (id, title) VALUES ('{}','{}');".format(
        category.id, category.title)

for subcategory in subcategories:
    print u"INSERT INTO category (id, title, parent) " +\
        "VALUES ('{}','{}','{}');".format(
        subcategory.id, subcategory.title, subcategory.parent.id)

for programme in programme_dicts:
    programme['tags'] = tagstring_to_postgres_array(programme['tags'])
    if programme['tags'] == u'{""}':
        programme['tags'] = u'{}'

    print sql_field_inject(
        u"INSERT INTO programme ({}) VALUES ({});"
        ).encode('utf-8').format(**programme)

    print u"INSERT INTO availability_window " + \
        u"(pid, start_time, end_time, service)"\
        + " VALUES ('{}', to_timestamp({}), to_timestamp({}), '{}');".format(
        programme['pid'],
        int(programme['start_time']),
        int(programme['end_time']),
        programme['service'])

    for category in programme['categories']:
        print u"INSERT INTO programme_category (pid, category_id) " \
            + "VALUES ('{}','{}');".format(programme['pid'], category.id)

    for subcategory in programme['subcategories']:
        print u"INSERT INTO programme_category (pid, category_id) " \
            + "VALUES ('{}','{}');".format(programme['pid'], subcategory.id)


print "COMMIT;"
