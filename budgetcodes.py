import csv
import sys
import sqlite3

import util
import sqlaload as sl


LEVELS = ['title', 'chapter', 'article', 'item']


def read_codesheet(file_name):
    fh = open(file_name, 'r')
    codes = {}
    for row in csv.DictReader(fh):
        codes[row['name']] = dict([(k, r.decode('utf-8')) for (k, r) in \
            row.items()])
    fh.close()
    return codes


def merge(codes):
    engine = util.make_engine()
    table = sl.get_table(engine, 'fts')
    for level in LEVELS:
        src_col = 'budget_code' if level == 'item' else level
        for data in sl.distinct(engine, table, src_col):
            value = data[src_col]
            if level == 'item' and len(value) < 11:
                continue
            if value not in codes:
                print value
                continue
            code_data = codes.get(value)
            data['%s_name' % level] = value
            data['%s_label' % level] = code_data['label']
            data['%s_description' % level] = code_data['description']
            data['%s_legal_basis' % level] = code_data['legal_basis']
            sl.upsert(engine, table, data, [src_col])


if __name__ == '__main__':
    assert len(sys.argv) == 2, "Usage: %s [codesheet]"
    codes = read_codesheet(sys.argv[1])
    merge(codes)
