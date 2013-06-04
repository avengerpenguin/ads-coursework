import csv
import re

with open('twoweek_proglist.csv', 'rb') as csvfile:
    for row in csv.DictReader(csvfile):

        row['tags'] = str(row['tags'].lstrip('[').rstrip(']').split('.')).replace('[', '{').replace(']', '}').replace("'", '"')

        print """INSERT INTO programme
(pid, complete_title, media_type, masterbrand, brand_pid, is_clip, tags)
VALUES
('{pid}','{complete_title}','{media_type}','{masterbrand}','{brand_pid}','{is_clip}','{tags}')""".format(**row)

