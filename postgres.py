import csv
import re
from sets import Set

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

def sql_field_inject(query_template):
    return query_template.format(
        ",".join(programme_fields),
        ",".join(["'{" + field + "}'" for field in programme_fields]))


def tagstring_to_postgres_array(tagstring):
    return list_to_postgres_array(tagstring_to_list(tagstring))


def list_to_postgres_array(some_list):
    return replace_all(str(some_list), {
            '[': '{',
            ']': '}',
            "'": '"'
            })


def tagstring_to_list(tag_string):
    return tag_string.strip('[]').split('.')


def replace_all(text, dic):
    for target, replacement in dic.iteritems():
        text = text.replace(target, replacement)
    return text


programme_fields = {
    'pid': 'varchar(10) PRIMARY KEY',
    'complete_title': 'varchar(256)',
    'media_type': "media_type",
    'masterbrand': 'varchar(20)',
    'brand_pid': 'varchar(10)',
    'is_clip': 'boolean',
    'tags': 'varchar[]'}

print """
BEGIN TRANSACTION;

DROP TABLE IF EXISTS availability_window;
DROP TABLE IF EXISTS subcategory;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS programme;
DROP TYPE IF EXISTS media_type;

CREATE TABLE category (
  id    varchar PRIMARY KEY,
  title varchar
);

CREATE TABLE subcategory (
  parent category
) INHERITS (category);

CREATE TYPE media_type AS ENUM ('audio', 'video') ;
CREATE TABLE programme ("""

print ",\n".join(["\t{}\t{}".format(field_name, field_type)
                  for field_name, field_type
                  in programme_fields.iteritems()])
print """);
"""

categories = set()
subcategories = set()
programme_dicts = []

with open('twoweek_proglist.csv', 'rb') as csvfile:
    for row in csv.DictReader(csvfile):
        row['tags'] = tagstring_to_postgres_array(row['tags'])

        cat_strings = tagstring_to_list(row['categories'])
        row['categories'] = []
        row['subcategories'] = []

        print cat_strings
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
                    raise KeyError('Not expecting category level: ' + cat_level)

        programme_dicts.append(row)


for category in categories:
    print "INSERT INTO category (id, title) VALUES ('{}','{}')".format(
        category.id, category.title)

for subcategory in subcategories:
    print "INSERT INTO subcategory (id, title, parent) VALUES ('{}','{}','{}')".format(
        subcategory.id, subcategory.title, subcategory.parent.id)

for programme in programme_dicts:
    print sql_field_inject(
        "INSERT INTO programme ({}) VALUES ({});").format(**programme)
    print "INSERT INTO availability_window (start, end, service) VALUES (to_timestamp({}), to_timestamp({}), '{}');".format(
        int(programme['start_time']), int(programme['end_time']), programme['service'])

print "COMMIT;"
