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

from urllib import quote, urlopen
import json
def integrate_geocode(conn, table):
    BASE = 'http://api.geonames.org/postalCodeSearchJSON?formatted=true&country=%s&postalcode=%s&maxRows=1&username=demo&style=full'
    c = conn.cursor()
    for col in ["admin1_code", "admin1_name", "admin2_code", "admin2_name",
                "admin3_code", "admin3_name"]:
        try:
            c.execute("ALTER TABLE %s ADD COLUMN %s TEXT" % (table, col))
        except: pass
    c.execute("SELECT DISTINCT country_code, postcode FROM %s" % table)
    for row in c:
        if row is None:
            break
        #import ipdb; ipdb.set_trace()
        if not row[0] or not row[1]:
            continue
        url = BASE % (quote(row[0].encode('utf-8')), 
                      quote(row[1].encode('utf-8')))
        data = json.load(urlopen(url))
        print url
        print len(data['postalCodes'])
        if len(data['postalCodes']):
            pc = data['postalCodes'][0]
            conn.execute('UPDATE %s SET admin1_code = ?, admin1_name = ?, '
                'admin2_code = ?, admin2_name = ?, admin3_code = ?, '
                'admin3_name = ? WHERE country_code = ? AND postcode = ?' %
                table, (pc.get('adminCode1'), pc.get('adminName1'), 
                    pc.get('adminCode2'), pc.get('adminName2'),
                    pc.get('adminCode3'), pc.get('adminName3'),
                    row[0], row[1]))
            conn.commit()

def integrate_nominatim(conn, table):
    BASE = 'http://open.mapquestapi.com/nominatim/v1/search?format=json&q=%s&limit=1&countrycodes=%s'
    CITIES = {}
    c = conn.cursor()
    for col in ["lng", "lat"]:
        try:
            c.execute("ALTER TABLE %s ADD COLUMN %s TEXT" % (table, col))
        except: pass
    c.execute("SELECT DISTINCT country_code, address, city, lng, lat FROM %s" % table)
    def _get(query, country):
        url = BASE % (quote(query.encode('utf-8')),
                      quote(country.encode('utf-8')))
        return json.load(urlopen(url))
    for row in c:
        if row is None:
            break
        if not row[0]: continue
        if row[3] and row[4]: continue
        query = row[1] + ", " + row[2]
        print query.encode('utf-8')
        data = _get(query, row[0])
        if not len(data):
            city = row[2].lower().strip()
            if not city in CITIES:
                CITIES[city] = _get(city, row[0])
            data = CITIES[city]
        if len(data):
            loc = data[0]
            print loc['lon'], loc['lat']
            conn.execute('UPDATE %s SET lng = ?, lat = ? '
                'WHERE country_code = ? AND address = ? AND city = ?' %
                table, (loc['lon'], loc['lat'],
                    row[0], row[1], row[2]))
            conn.commit()

from ll2nuts import LonLat2NUTS
def integrate_nuts(conn, table):
    c = conn.cursor()
    ll = LonLat2NUTS(3)
    for col in ["nuts2"]:
        try:
            c.execute("ALTER TABLE %s ADD COLUMN %s TEXT" % (table, col))
        except: pass
    c.execute("SELECT DISTINCT country_code, lng, lat FROM %s" % table)
    for row in c:
        if row is None:
            break
        if not row[0]: continue
        if not row[1] or not row[2]: continue
        try:
            print row
            nuts = ll.ll2nuts(float(row[1]), float(row[2]), iso=row[0])
            if not nuts.startswith(row[0]):
                continue
            print nuts
            conn.execute('UPDATE %s SET nuts2 = ? WHERE lat = ? AND  '
                'lng = ? AND country_code = ?' % table, 
                (nuts, row[2], row[1], row[0]))
            conn.commit()
        except Exception, e:
            print e

if __name__ == '__main__':
    assert len(sys.argv)==3, "Usage: %s {cc,dg,corp} [sqlite-db]"
    op = sys.argv[1]
    conn = sqlite3.connect(sys.argv[2])
    ops = {
        'dg': integrate_departments,
        'corp': integrate_companies,
        'cc': integrate_countries,
        'geo': integrate_nominatim,
        'nuts': integrate_nuts
        }.get(op)(conn, 'fts'),

