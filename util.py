import os
import sqlaload as sl

def make_engine():
    db_url = os.environ.get('FTS_URL')
    assert db_url is not None, \
        "Set FTS_URL in the environment!"
    return sl.connect(db_url)


def process_rows(handlefunc, engine=None):
    if engine is None:
        engine = make_engine()
    table = sl.get_table(engine, 'fts')
    for row in sl.all(engine, table):
        out = handlefunc(row)
        sl.upsert(engine, table, out, ['id'])
    return table

