#!/usr/bin/env python

from lxml import etree
import requests
import sqlite3
from nlsy import Session

conn = sqlite3.connect('nlsy97.sqlite3')
db = conn.cursor()

db.execute('CREATE TABLE IF NOT EXISTS varnames (rnum text, qname text, category text, title text, year text)')

# Gives you categories without variables yet
db.execute('''
	SELECT categories.id
	FROM categories
	LEFT JOIN (
		SELECT COUNT(*) as count, category
		FROM varnames
		GROUP BY category
	) counts
	ON counts.category == categories.id
	WHERE categories.hasChildren == 0
	AND (
		counts.count == 0
		OR counts.count IS NULL
	)
''')

from multiprocessing import Pool

session = None
def initializer():
	global session
	session = Session()

# Okay if you want more generic multiprocessing things (especially for trees)
# they need to be based on what you're doing. Like, you can have a pool for
# mapping an iterable, and then another pool for traversing a tree.
#
# An iterable is easy: create an input Queue and output Queue. Read from the
# iterable until it's empty, then feed the input Queue `j` messages to stop,
# where `j` is the number of processes. Once all the processes are dead, you're
# done.
#
# A tree needs to keep track of how many things are being processed. You start
# with one seed (root) value, so `c` is 1, where `c` is the number of items
# still being processed. When a worker adds a new task, increment `c`. When a
# worker finishes with a task, decrement `c`. When `c` reaches 0, we know
# nothing is running anymore so we can shut down the workers and finish the
# iterable.
#
# Also, you can still re-use processes, but please do the initializer per
# type of work you're doing. Global variables suck.


def get_rows(k):
	global session
	r = requests.get("https://www.nlsinfo.org/investigator/servlet1?get=Results&criteria=TREENODE%7CEQ%7C{}".format(k), cookies={"JSESSIONID": session, "preferences": "showref=true&showqname=true&showtitle=true&showyear=true"})
	try:
		xml = etree.fromstring(r.content)
		rows = []
		for row in xml.findall(".//ROW"):
			rnum = row.find('RNUM').text
			qname = row.find('QNAME').text
			title = row.find('TITLE').text
			year = row.find('YEAR').text
			rows.append((rnum, qname, k, title, year))
		return rows
	except:
		print k
		print r.text
		raise

if __name__ == '__main__':
	categories = list(c[0] for c in db.fetchall())
	pool = Pool(processes=24, initializer=initializer)
	for rows in pool.imap_unordered(get_rows, categories):
		for row in rows:
			print row
		db.executemany('INSERT INTO varnames VALUES (?, ?, ?, ?, ?)', rows)
		conn.commit()
	pool.close()
	pool.join()