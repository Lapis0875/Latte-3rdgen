import sqlite3

test_db = sqlite3.connect(database="test.db")
conn = test_db.cursor()
conn.execute(sql="CREATE TABLE")