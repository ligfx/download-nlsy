#!/usr/bin/env python

import nlsy
import sys

print '''CREATE TABLE categories (count integer, id text, parent text, hasChildren integer, label text);'''

for c in nlsy.get_categories():
    sys.stderr.write(repr(c) + "\n")
    print 'INSERT INTO categories VALUES ({}, {}, {}, {}, "{}");'.format(c['count'], str(int(c['id'])), str(c['parent']), int(c['hasChildren']), c['label'])