import sys, csv
from urllib import urlopen
from pprint import pprint

from recon import company, public_body
from recon.interactive import interactive, SQLiteMemory
from recon.local import CSVLocalEndpoint
from sqlaload import connect, get_table, distinct, all, update

COUNTRIES_URL = 'iso_3166_2_countries.csv'

def integrate_countries(engine, table):
    fh = urlopen(COUNTRIES_URL)
    uri = lambda r: r['ISO 3166-1 2 Letter Code']
    endpoint = CSVLocalEndpoint(fh, 'Common Name', uri_maker=uri)
    integrate_recon(engine, table, endpoint.reconcile,
                    'country',
                    'country_name', 'country_code',
                    'countries')


def integrate_departments(engine, table):
    def eu_public_body(query):
        return public_body(query, jurisdiction='EU', limit=10)
    integrate_recon(engine, table, eu_public_body,
                    'responsible_department',
                    'department_name', 'department_uri',
                    'eu_bodies')

def integrate_companies(engine, table):
    #def eu_public_body(query):
    #    return public_body(query, jurisdiction='EU', limit=10)
    integrate_recon(engine, table, company,
                    'beneficiary',
                    'beneficiary_name', 'beneficiary_uri',
                    'companies', min_score=60)

def integrate_recon(engine, table, qfunc, src_col, dst_name_col, dst_uri_col,
        memory_name, min_score=None):
    memory = SQLiteMemory(engine.raw_connection(), memory_name)
    conn = engine.connect()
    for row in list(distinct(engine, table, src_col)):
        res = interactive(qfunc, row[src_col], memory=memory, min_score=min_score)
        if res is not None:
            print row.get(src_col), " -> ", res.name.encode('utf-8'), res.score
            update(conn, table, row, {dst_name_col: res.name, dst_uri_col: res.uri})

from urllib import quote, urlopen
import json
def integrate_geocode(engine, table):
    BASE = 'http://api.geonames.org/postalCodeSearchJSON?formatted=true&country=%s&postalcode=%s&maxRows=1&username=demo&style=full'
    conn = engine.connect()
    for row in list(distinct(engine, table, 'country_code', 'postcode')):
        if not row['country_code'] or not row['postcode']:
            continue
        url = BASE % (quote(row[0].encode('utf-8')), 
                      quote(row[1].encode('utf-8')))
        data = json.load(urlopen(url))
        print url
        print len(data['postalCodes'])
        if len(data['postalCodes']):
            pc = data['postalCodes'][0]
            update(conn, table, row, {
                'admin1_code': pc.get('adminCode1'),
                'admin1_name': pc.get('adminCode1'),
                'admin2_code': pc.get('adminCode2'),
                'admin2_name': pc.get('adminName2'),
                'admin3_code': pc.get('adminCode3'),
                'admin3_name': pc.get('adminName3')
                })

def integrate_nominatim(engine, table):
    BASE = 'http://open.mapquestapi.com/nominatim/v1/search?format=json&q=%s&limit=1&countrycodes=%s'
    CITIES = {}
    def _get(query, country):
        url = BASE % (quote(query.encode('utf-8')),
                      quote(country.encode('utf-8')))
        return json.load(urlopen(url))
    conn = engine.connect()
    for row in list(distinct(engine, table, 'country_code', 'address', 'city',
                             'lng', 'lat')):
        if not row['country_code']: continue
        if row['lng'] and row['lat']: continue
        query = row['address'] + ", " + row['city']
        print query.encode('utf-8')
        data = _get(query, row['country_code'])
        if not len(data):
            city = row['city'].lower().strip()
            if not city in CITIES:
                CITIES[city] = _get(city, row['country_code'])
            data = CITIES[city]
        if len(data):
            loc = data[0]
            criteria = row.copy()
            del criteria['lng']
            del criteria['lat']
            print loc['lon'], loc['lat']
            update(conn, table, criteria, 
                {'lng': loc['lon'], 'lat': loc['lat']})

def integrate_nuts(engine, table):
    from ll2nuts import LonLat2NUTS
    ll = LonLat2NUTS(3)
    conn = engine.connect()
    for row in list(distinct(engine, table, 'country_code', 'lng', 'lat')):
        if not row['country_code'] or not row['lng'] or not row['lat']: 
            continue
        try:
            print row
            nuts = ll.ll2nuts(float(row['lng']), float(row['lat']),
                              iso=row['country_code'])
            if not nuts.startswith(row['country_code']):
                continue
            print nuts
            update(conn, table, row, {'nuts3': nuts})
        except Exception, e:
            print e

def integrate_nutsnames(conn, table):
    fh = open('NUTS_2006.csv', 'rb')
    nuts1, nuts2, nuts3 = {}, {}, {}
    for row in csv.DictReader(fh):
        d = {'1': nuts1, '2': nuts2, '3': nuts3}.get(row['NUTS_LEVEL'], {})
        d[row['CODE']] = dict([(k, v.decode('utf-8')) for k, v in row.items()])
    conn = engine.connect()
    for row in list(distinct(engine, table, 'nuts3')):
        if not row['nuts3']: continue
        nuts1_ = row['nuts3'][:3]
        nuts2_ = row['nuts3'][:4]
        data = {
            'nuts1': nuts1_, 'nuts1_label': nuts1.get(nuts1_, {}).get('LABEL'),
            'nuts2': nuts2_, 'nuts1_label': nuts2.get(nuts2_, {}).get('LABEL'),
            'nuts3_label': nuts3.get(nuts1_, {}).get('LABEL')
                }
        update(conn, table, row, data)

if __name__ == '__main__':
    assert len(sys.argv)==3, "Usage: %s {cc,dg,corp} [sqlite-db]"
    op = sys.argv[1]
    engine = connect('sqlite:///' + sys.argv[2])
    table = get_table(engine, 'fts')
    ops = {
        'dg': integrate_departments,
        'corp': integrate_companies,
        'cc': integrate_countries,
        'geo': integrate_nominatim,
        'nuts': integrate_nuts,
        'nutsnames': integrate_nutsnames
        }.get(op)(engine, table)

