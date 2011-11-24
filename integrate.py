import sqlite3
import sys
from urllib import urlopen

from recon import company, public_body
from recon.interactive import interactive, SQLiteMemory
from recon.local import CSVLocalEndpoint

COUNTRIES_URL = 'iso_3166_2_countries.csv'

def integrate_countries(conn, table):
    fh = urlopen(COUNTRIES_URL)
    uri = lambda r: r['ISO 3166-1 2 Letter Code']
    endpoint = CSVLocalEndpoint(fh, 'Common Name', uri_maker=uri)
    integrate_recon(conn, table, endpoint.reconcile,
                    'country',
                    'country_name', 'country_code',
                    'countries')


def integrate_departments(conn, table):
    def eu_public_body(query):
        return public_body(query, jurisdiction='EU', limit=10)
    integrate_recon(conn, table, eu_public_body,
                    'responsible_department',
                    'department_name', 'department_uri',
                    'eu_bodies')

def integrate_companies(conn, table):
    #def eu_public_body(query):
    #    return public_body(query, jurisdiction='EU', limit=10)
    integrate_recon(conn, table, company,
                    'beneficiary',
                    'beneficiary_name', 'beneficiary_uri',
                    'companies', min_score=60)

def integrate_recon(conn, table, qfunc, src_col, dst_name_col, dst_uri_col,
        memory_name, min_score=None):
    c = conn.cursor()
    memory = SQLiteMemory(conn, memory_name)
    for col in [dst_name_col, dst_uri_col]:
        try:
            c.execute("ALTER TABLE %s ADD COLUMN %s TEXT" % (table, col))
        except: pass
    c.execute("SELECT DISTINCT %s FROM %s" % (src_col, table))
    for row in c:
        res = interactive(qfunc, row[0], memory=memory, min_score=min_score)
        if res is not None:
            print row[0], " -> ", res.name.encode('utf-8'), res.score
            conn.execute('UPDATE %s SET %s = ?, %s = ? WHERE %s = ?' % \
                    (table, dst_name_col, dst_uri_col, src_col),
                    (res.name, res.uri, row[0]))
            conn.commit()

if __name__ == '__main__':
    assert len(sys.argv)==3, "Usage: %s {cc,dg,corp} [sqlite-db]"
    op = sys.argv[1]
    conn = sqlite3.connect(sys.argv[2])
    ops = {
        'dg': integrate_departments,
        'corp': integrate_companies,
        'cc': integrate_countries
        }.get(op)(conn, 'fts'),

