import logging
import requests
import csv

import util
import sqlaload as sl
import shapegeocode

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('beneficiary')
session = requests.session()

SERVICE = 'http://open.mapquestapi.com/nominatim/v1/search'
KEYS = ['country_code', 'address', 'city', 'postcode']


def geocode(row):
    if not row.get('country_code'):
        return
    res = session.get(SERVICE, params={
        'format': 'json',
        'limit': 1,
        'countrycodes': row.get('country_code'),
        'postalcode': row.get('postcode'),
        'city': row.get('city'),
        'street': row.get('address')
        })
    if res.ok and len(res.json()):
        loc = res.json()[0]
        return {'lat': loc['lat'],
                'lon': loc['lon']}


def load_region_hierarchy():
    fh = open('NUTS_2006.csv', 'rb')
    data = {}
    for row in csv.DictReader(fh):
        data[row['CODE']] = dict([(k, v.decode('utf-8')) \
            for k, v in row.items()])
    return data


def find_region(geocoder, regions, row):
    data = geocoder.geocode(float(row['lat']), float(row['lon']),
        filter=lambda r: r['NUTS_ID'][:2] == row['country_code'])
    if data is None:
        return {}
    nuts3_code = data.get('NUTS_ID')
    nuts3 = regions.get(nuts3_code, {})
    nuts2 = regions.get(nuts3_code[:4], {})
    nuts1 = regions.get(nuts3_code[:3], {})
    return {
        'nuts3': nuts3_code,
        'nuts3_label': nuts3.get('LABEL'),
        'nuts2': nuts3_code[:4],
        'nuts2_label': nuts2.get('LABEL'),
        'nuts1': nuts3_code[:3],
        'nuts1_label': nuts1.get('LABEL'),
        }


def merge():
    geocoder = shapegeocode.geocoder(
        'nuts2-shapefile/data/NUTS_RG_10M_2006.shp',
        filter=lambda r: r['STAT_LEVL_'] == 3)
    regions = load_region_hierarchy()
    engine = util.make_engine()
    table = sl.get_table(engine, 'fts')
    for row in sl.distinct(engine, table, *KEYS):
        loc = geocode(row)
        if loc is None:
            continue
        row.update(loc)
        reg = find_region(geocoder, regions, row)
        row.update(reg)
        log.info("Geocoded: %s/%s - %s",
            row['lat'], row['lon'], row.get('nuts3_label'))
        sl.upsert(engine, table, row, KEYS)


if __name__ == '__main__':
    merge()
