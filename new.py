def worker(ctx):
	while True:
		k = ctx.next_task()
		if None == k:
			return
		k[0](ctx, *k[1])
		ctx.finish_task()

class Tasks(object):
	def __init__(self, j):
		self.i = Queue()
		self.o = Queue()
		self.c = Queue()
		self.j = j
		self.processes = []
		for _ in range(j):
			k = Process(target=worker, args=(self,))
			k.start()
			self.processes.append(k)
		self.c = 1
	def next_task(self):
		return self.i.get()
	def finish_task(self):
		self.c.put(-1)
	def next(self):
		return o.get()
	def submit(self, func, args):
		self.c.put(1)
		self.i.put((func, args))
	def ret(self, obj):
		self.o.put(obj)

#!/usr/bin/env python

from multiprocessing import Process, Queue
import requests

def Session():
    r = requests.get("https://www.nlsinfo.org/investigator/pages/search.jsp")
    cookie = r.cookies['JSESSIONID']
    r = requests.get("https://www.nlsinfo.org/investigator/servlet1?set=STUDY&id=1.6", cookies={"JSESSIONID": cookie})
    return cookie

session = Session()

def nlsy(ctx, node="0"):
    try:
        r = requests.get("https://www.nlsinfo.org/investigator/servlet1?get=TREEVIEW&event=expand&node={0}".format(node), cookies={"JSESSIONID": session})
        j = r.json()
        for n in j['nodes']:
            n['parent'] = node
            #o.put(('print', n))
            print n
            if n['hasChildren']:
                o.put(('count', 1))
                i.put(int(n['id']))
    except:
        print r.text
        raise
    o.put(('count', -1))

def runner(i, o):
    while True:
       node = i.get()
       if None == node:
           return
       nlsy(i, o, node)

j = 24

if __name__ == '__main__':
    i = Queue()
    o = Queue()
    p = []
    for _ in range(j):
        k = Process(target=runner, args=(i,o))
        k.start()
        p.append(k)
    c = 1
    nlsy(i, o)
    while c != 0:
        k = o.get()
        if k[0] == 'print':
            print k[1]
        elif k[0] == 'count':
            c += k[1]
    for _ in p:
        i.put(None)
    for _ in p:
        _.join()
