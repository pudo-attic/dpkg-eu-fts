#coding: utf-8

import sys
from lxml import etree

import util
import sqlaload as sl

NUMCHAR = "0123456789-."

def to_float(num):
    try:
        num = num.replace('.', '').replace(',', '.')
        return float(''.join([n for n in num if n in NUMCHAR]))
    except:
        "NaN"

def convert_commitment(commitment, write):
    common = {}
    common['date'] = commitment.findtext('year')
    common['total'] = to_float(commitment.findtext('amount'))
    common['cofinancing_rate'] = commitment.findtext('cofinancing_rate')
    common['cofinancing_rate_pct'] = to_float(common['cofinancing_rate'])
    common['position_key'] = commitment.findtext('position_key')
    common['grant_subject'] = commitment.findtext('grant_subject')
    common['responsible_department'] = commitment.findtext('responsible_department')
    common['action_type'] = commitment.findtext('actiontype')
    budget_line = commitment.findtext('budget_line')

    name, code = budget_line.rsplit('(', 1)
    code = code.replace(')', '').replace('"', '').strip()
    common['budget_item'] = name.strip()
    common['budget_code'] = code

    parts = code.split(".")
    common['title'] = parts[0]
    common['chapter'] = '.'.join(parts[:2])
    common['article'] = '.'.join(parts[:3])
    if len(parts) == 4:
        common['item'] = '.'.join(parts[:4])

    for beneficiary in commitment.findall('.//beneficiary'):
        row = common.copy()
        row['beneficiary'] = beneficiary.findtext('name')
        if '*' in row['beneficiary']:
            row['beneficiary'], row['alias'] = row['beneficiary'].split('*', 1)
        else:
            row['alias'] = row['beneficiary']
        row['address'] = beneficiary.findtext('address')
        row['city'] = beneficiary.findtext('city')
        row['postcode'] = beneficiary.findtext('post_code')
        row['country'] = beneficiary.findtext('country')
        row['geozone'] = beneficiary.findtext('geozone')
        row['coordinator'] = beneficiary.findtext('coordinator')
        detail_amount = beneficiary.findtext('detail_amount')
        if detail_amount is not None and len(detail_amount):
            row['amount'] = to_float(detail_amount)
        else: 
            row['amount'] = row['total']
        if row['amount'] is "NaN":
            row['amount'] = row['total']
        write(row)

def write_row(engine, base, row):
    base['source_id'] += 1
    data = base.copy()
    data.update(row)
    table = sl.get_table(engine, 'fts')
    sl.upsert(engine, table, data, ['source_file', 'source_id'])


def convert_file(filename):
    doc = etree.parse(filename)
    engine = util.make_engine()
    base = {'source_file': filename, 'source_id': 0}
    for i, commitment in enumerate(doc.findall('//commitment')):
        base.update({'source_line': commitment.sourceline,
                     'source_contract_id': i})
        write = lambda r: write_row(engine, base, r)
        convert_commitment(commitment, write)

if __name__ == '__main__':
    assert len(sys.argv)==2, "Usage: %s [source-file]"
    convert_file(sys.argv[1])

