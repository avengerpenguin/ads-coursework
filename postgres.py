import csv
import re


class Category(object):
    def __init__(self, cid, title):
        self.id = cid
        self.title = title

    def __eq__(self, other_category):
        return self.id == other_category.id

    def __hash__(self):
        return hash(self.id)


class Subcategory(Category):
    def __init__(self, cid, title, parent):
        self.id = cid
        self.title = title
        self.parent = parent


def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield dict(
            [(key, unicode(value, 'utf-8'
                           ).encode('UTF-8').decode('string_escape'))
             for key, value in row.iteritems()])


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


def tagstring_to_list(tag_string):
    return tag_string.strip('[]').split('.')


def replace_all(text, dic):
    for target, replacement in dic.iteritems():
        text = text.replace(target, replacement)
    return text


programme_fields = {
    'pid': 'varchar(12) PRIMARY KEY',
    'complete_title': 'varchar(256)',
    'media_type': "media_type",
    'masterbrand': 'varchar(40)',
    'brand_pid': 'varchar(12)',
    'is_clip': 'boolean',
    'tags': 'varchar[]'}

print u"""
BEGIN TRANSACTION;

DROP TABLE IF EXISTS availability_window;
DROP TABLE IF EXISTS subcategory;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS programme;
DROP TYPE IF EXISTS media_type;

CREATE TABLE category (
  id    varchar(40) PRIMARY KEY,
  title varchar(50)
);

CREATE TABLE subcategory (
  parent varchar(40) REFERENCES category(id)
) INHERITS (category);

CREATE TYPE media_type AS ENUM ('audio', 'video');
CREATE TABLE programme ("""

print ",\n".join(["\t{}\t{}".format(field_name, field_type)
                  for field_name, field_type
                  in programme_fields.iteritems()])
print """);

CREATE TABLE availability_window (
  pid        varchar(12) REFERENCES programme(pid),
  start_time timestamp,
  end_time   timestamp,
  service    varchar(40),
  PRIMARY KEY (pid, start_time, service)
);
"""

categories = set()
subcategories = set()
programme_dicts = []

with open('twoweek_proglist_utf8.csv', 'rb') as csvfile:
    for row in UnicodeDictReader(csvfile):
        row['tags'] = tagstring_to_postgres_array(row['tags'])
        if row['tags'] == u'{""}':
            row['tags'] = u'{}'

        cat_strings = tagstring_to_list(row['categories'])
        row['categories'] = []
        row['subcategories'] = []

        for cat_string in cat_strings:
            if cat_string:
                cat_id, cat_level, cat_title = cat_string.split(':')

                if cat_level == '1':
                    category = Category(cat_id, cat_title)
                    categories.add(category)
                    row['categories'].append(category)

                elif cat_level == '2':
                    subcategory = Subcategory(cat_id, cat_title, category)
                    subcategories.add(subcategory)
                    row['subcategories'].append(subcategory)

                else:
                    raise KeyError(
                        'Not expecting category level: ' + cat_level)

        programme_dicts.append(row)


for category in categories:
    print u"INSERT INTO category (id, title) VALUES ('{}','{}');".format(
        category.id, category.title)

for subcategory in subcategories:
    print u"INSERT INTO subcategory (id, title, parent) " +\
        "VALUES ('{}','{}','{}');".format(
        subcategory.id, subcategory.title, subcategory.parent.id)

for programme in programme_dicts:
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

print "COMMIT;"
