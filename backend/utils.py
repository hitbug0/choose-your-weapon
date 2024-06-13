import functools
import sqlite3

DATABASE = "./database/database.db"
LENGTH_LOG = 50


# ロギング用のデコレータ関数
def logging_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        n = (LENGTH_LOG - len(f" start {func.__name__} ")) // 2
        print("=" * n + f" start {func.__name__} " + "=" * n)
        result = func(*args, **kwargs)
        print("=" * (n + 1) + f" end {func.__name__} " + "=" * (n + 1))
        return result

    return wrapper


# データベース接続
def get_db():
    conn = sqlite3.connect(DATABASE)
    # print("connect to DB")
    return conn


# DB初期化
@logging_decorator
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS table1 (
            uuid TEXT PRIMARY KEY,
            id_by_user TEXT,
            name TEXT NOT NULL,
            type TEXT,
            size_x REAL NOT NULL,
            size_y REAL NOT NULL,
            size_z REAL NOT NULL,
            remarks TEXT,
            first_upload_date TEXT NOT NULL,
            update_date TEXT NOT NULL,
            reference TEXT,
            rate REAL NOT NULL,
            status TEXT NOT NULL
        )"""
    )
    conn.commit()
    conn.close()


def combine_without_duplication(list0, list1):
    return list0 + [item for item in list1 if item not in list0]
