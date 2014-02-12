#!/usr/bin/env python

import sqlite3

conn = sqlite3.connect('nlsy97.sqlite3')
db = conn.cursor()

def chunk(seq, size):
	collect = []
	for k in seq:
		collect.append(k)
		if len(collect) == size:
			yield collect
			collect = []
	if len(collect) > 0:
		yield collect


db.execute('''SELECT rnum FROM varnames ORDER BY rnum''')
rnums = []
i = 1

for i, rnums in enumerate(chunk((_[0].replace('.', '') for _ in db.fetchall()), 5000)):
	with open('tagset-{}.NLSY97'.format(i), 'w') as f:
		f.write('\n'.join(rnums))