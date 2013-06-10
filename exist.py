from datetime import datetime
from parse import parse_csv, tagstring_to_list, replace_all
from lxml.builder import E
import lxml.etree as ET


def xs_datetime(timestamp_string):
    return datetime.fromtimestamp(int(timestamp_string)).isoformat()


def category_structure(programme):
    node = E.categories()
    for category in programme['categories']:

        category_node = E.category(
            E.id(category.id),
            E.title(category.title)
        )

        subcategories = [E.category(
                E.id(subcategory.id),
                E.title(subcategory.title)
                )
                         for subcategory in programme['subcategories']
                         if subcategory.parent is category]

        if subcategories:
            category_node.append(E.categories(*subcategories))

        node.append(category_node)

    return node


programme_dicts, categories, subcategories = parse_csv()


for programme in programme_dicts:
    with open('xml/{}.xml'.format(programme['pid']), 'w') as xml_file:
        xml = ET.tostring(
            E.programme(
                E.pid(programme['pid']),
                E.complete_title(
                    unicode(
                        programme['complete_title'], 'utf-8'
                        )),
                E.media_type(programme['media_type']),
                E.masterbrand(programme['masterbrand']),
                E.brand_pid(programme['brand_pid']),
                E.is_clip(programme['is_clip']),
                E.availability(
                    E.window(
                        E.start_time(
                            xs_datetime(programme['start_time'])),
                        E.end_time(
                            xs_datetime(programme['end_time'])),
                        E.service(programme['service']))
                    ),
                category_structure(programme),
                E.tags(
                    *[E.tag(unicode(tag_value, 'utf-8'))
                      for tag_value
                      in tagstring_to_list(programme['tags'])]
                     )
                ),
            encoding='UTF-8',
            pretty_print=True,
            standalone=True)
        #print xml
        xml_file.write(xml)
