import sqlite3 as sq
# using datatime to get the exact timestamp
import datetime as dt 

from contextlib import contextmanager

# we are using contextmanager from contextlib for creating connection to already
# initiated database
@contextmanager
def cursor():
    try:
        # using connect, sqlite will try to open the file
        conn = sq.connect('GNHTTbot.db')
        # cursor allows you to execute sql code
        cur = conn.cursor()
        yield cur
        # commit saves changes to the database
        conn.commit()
    finally:
        # finally closing connection
        conn.close()

# method for saving data_value
def add_data(user_id, recorded_utc, hr, rmssd):
    with cursor() as cur:
        # executing command INSERT INTO for saving new data
        cur.execute('INSERT INTO data_table values(?, ?, ?, ?)', (user_id, recorded_utc, hr, rmssd))

# gets selected data from table data_table and returns it 
# TODO: expand on this to select data from different tables in the future
def getdatapoint():
    with cursor() as cur:
        cur.execute('SELECT date, data from data_table')
        rows = cur.fetchall()
    return rows