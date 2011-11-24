#coding: utf-8
# this script CONVERTS fts xml FILES INTO A csv FORMAT APPROPRIATE FOR 
# LOADING INTO oPENsPENDING. wHILE THE ec DOES OFFER A csv FILE FOR DOWNLOAD
# THE GENERATED FORMAT OF THIS IS CLEANER AND MORE DETAILED.

import sys
from lxml import etree

import sqlite3

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

def convert_file(filename, filedb):
    doc = etree.parse(filename)
    conn = sqlite3.connect(filedb)
    headers = []
    rows = []
    id = [0]
    for i, commitment in enumerate(doc.findall('//commitment')):
        source = {'source_file': filename, 'source_line': commitment.sourceline,
                  'source_contract_id': i}
        def write(data):
            row = source.copy()
            row.update(data)
            row['source_id'] = id[0]
            id[0] += 1
            if not len(headers):
                headers.extend(row.keys())
                q = ', '.join(["%s TEXT" % h for h in headers])
                conn.execute("CREATE TABLE IF NOT EXISTS fts (%s);" % q)
            q = ', '.join(['?']*len(headers))
            #print headers
            conn.execute("INSERT INTO fts VALUES (%s);" % q, [row.get(h) for h in \
                headers])

        convert_commitment(commitment, write)
    #table.writerows(rows)
    #out_file.close()
    conn.commit()

if __name__ == '__main__':
    assert len(sys.argv)==3, "Usage: %s [source-file] [sqlite-db]"
    convert_file(sys.argv[1], sys.argv[2])

