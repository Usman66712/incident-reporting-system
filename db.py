import pymysql
from pymysql.cursors import DictCursor
from config import DB_CONFIG

def get_connection(use_database: bool = True):
    cfg = dict(DB_CONFIG)
    if not use_database:
        cfg.pop("database", None)
    cfg["cursorclass"] = DictCursor
    cfg["autocommit"] = False
    return pymysql.connect(**cfg)
