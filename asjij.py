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
	);
''')

from multiprocessing import Process, Queue

def runner(i, o):
	session = Session()
	while True:
		k = i.get(False)
		r = requests.get("https://www.nlsinfo.org/investigator/servlet1?get=Results&criteria=TREENODE%7CEQ%7C{}".format(k), cookies={"JSESSIONID": session, "preferences": "showref=true&showqname=true&showtitle=true&showyear=true"})
		try:
			rows = []
			for row in etree.fromstring(r.content).findall(".//ROW"):
				rnum = row.find('RNUM').text
				qname = row.find('QNAME').text
				title = row.find('TITLE').text
				year = row.find('YEAR').text
				rows.append((rnum, qname, c[0], title, year))
			o.put(rows)
		except:
			print k
			print r.text
			raise

i = Queue()
o = Queue()

for c in db.fetchall():
	i.put(c[0])

j = 24
p = []
for _ in range(j):
    k = Process(target=runner, args=(i,o))
    k.start()
    p.append(k)
while True:
	if i.empty():
		break
	rows = o.get()
	for row in rows:
		print row
	db.executemany('INSERT INTO varnames VALUES (?, ?, ?, ?, ?)', rows)
	conn.commit()

for _ in p:
	_.join()