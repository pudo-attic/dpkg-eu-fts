import csv
import sys
import sqlite3

LEVELS = ['title', 'chapter', 'article', 'item']

def read_codesheet(file_name):
    fh = open(file_name, 'r')
    codes = {}
    for row in csv.DictReader(fh):
        codes[row['name']] = dict([(k, r.decode('utf-8')) for (k, r) in \
            row.items()])
    fh.close()
    return codes

def merge(conn, table, codes):
    for level in LEVELS:
        for col in ["%s_name", "%s_label", "%s_description", "%s_legal_basis"]:
            n = col % level
            try:
                conn.execute("ALTER TABLE %s ADD COLUMN %s TEXT" % (table, n))
            except: pass
    for level in LEVELS:
        src_col = level 
        if level == 'item':
            src_col = 'budget_code'
        c = conn.cursor()
        c.execute("SELECT DISTINCT %s FROM %s" % (src_col, table))
        for row in c:
            value = row[0]
            if level == 'item' and len(value) < 11:
                continue
            if value not in codes:
                print value
                continue
            exp = codes.get(value)
            conn.execute("UPDATE %s SET %s_name = ?, %s_label = ?, "
                    "%s_description = ?, %s_legal_basis = ? WHERE %s = ?" % \
                        (table, level, level, level, level, src_col), 
                        (value, exp['label'], exp['description'],
                        exp['legal_basis'], value))
            conn.commit()

if __name__ == '__main__':
    assert len(sys.argv)==3, "Usage: %s [sqlite-db] [codesheet]"
    conn = sqlite3.connect(sys.argv[1])
    codes = read_codesheet(sys.argv[2])
    merge(conn, 'fts', codes)
