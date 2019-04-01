from autoredis import AutoRedis

DB = {}


def get_db(db):
    try:
        return DB[db]
    except KeyError:
        DB[db] = AutoRedis(('127.0.0.1', 6379),
                           password=None,
                           db=int(db),
                           decode_responses=True)
        return DB[db]
