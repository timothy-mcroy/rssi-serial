import sqlite3

con = sqlite3.connect('signals.db')
con.execute('DELETE FROM recording')
con.commit()
con.close()
