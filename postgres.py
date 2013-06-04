import csv
import re


class Category(object):
    def __init__(self, cid, level, title):
        self.id = cid
        self.level = level
        self.title = title


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
    'pid': 'varchar(10)',
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
  id    varchar,
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

programme_dicts = []

with open('twoweek_proglist.csv', 'rb') as csvfile:
    for row in csv.DictReader(csvfile):
        row['tags'] = tagstring_to_postgres_array(row['tags'])
        row['categories'] = [Category(*cat.split(':'))
                             for cat
                             in tagstring_to_list(rows['categories'])]
        programme_dicts.append(row)



for programme in programme_dicts:
    print sql_field_inject(
        "INSERT INTO programme ({}) VALUES ({});").format(**programme)
    
    break

print "COMMIT;"
