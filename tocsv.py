'''
Writes a sqlite database
named 'signals.db' to a csv file
'''

import sys
import csv
import sqlite3
def toCSV(filename):
    with open(filename, 'wb') as f:
        conn = sqlite3.connect('signals.db')
        cur = conn.cursor()
        data = cur.execute("SELECT * FROM recording")
        headings = [desc[0] for desc in cur.description]
        writer = csv.writer(f)
        writer.writerow(headings)
        writer.writerows(data)
    print("{} has been created".format(filename))



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ("Please give an output filename")
    else:
        toCSV(sys.argv[1])

