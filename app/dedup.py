import hashlib
import sqlite3

path_to_scanned = './rbc-statement-parser.db'

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(path_to_scanned)

def upsert_schema():
    con = get_connection()
    cursor = con.cursor()
    cursor.execute('create table if not exists scanned (id integer primary key autoincrement, file nvarchar(256), hash char(20))')

def has_been_parsed(
    path_to_file: str
) -> bool:
    with open(path_to_file, mode='rb') as file:
        contents = file.read()
        sha1_hash = hashlib.sha1(contents).hexdigest()
        con = sqlite3.connect(path_to_scanned)
        res = con.execute('select hash from scanned where file = ?', [path_to_file]).fetchone()
        if res is None:
            return False
        return res[0] == sha1_hash

def mark_as_parsed(
    path_to_file: str
) -> bool:
    with open(path_to_file, mode='rb') as file:
        contents = file.read()
        sha1_hash = hashlib.sha1(contents).hexdigest()
        con = sqlite3.connect(path_to_scanned)
        con.execute('insert into scanned(file, hash) values (?, ?)', (path_to_file, sha1_hash)).fetchone()
        con.commit()
