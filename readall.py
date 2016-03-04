import sqlite3

con = sqlite3.connect('signals.db')
cursor = con.execute('select * from recording')
print(cursor.fetchall())
cursor.close()
con.close()
