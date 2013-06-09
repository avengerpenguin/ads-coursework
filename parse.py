import csv


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
                           ).encode('utf-8').decode('string_escape'))
             for key, value in row.iteritems()])


def tagstring_to_list(tag_string):
    return tag_string.strip('[]').split('.')


def replace_all(text, dic):
    for target, replacement in dic.iteritems():
        text = text.replace(target, replacement)
    return text


def parse_csv():

    categories = set()
    subcategories = set()
    programme_dicts = []

    with open('twoweek_proglist.csv', 'rb') as csvfile:
        for row in UnicodeDictReader(csvfile):

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

    return programme_dicts, categories, subcategories
