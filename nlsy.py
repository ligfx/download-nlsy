from multiprocessing import Process, Queue
import requests

def Session():
    r = requests.get("https://www.nlsinfo.org/investigator/pages/search.jsp")
    cookie = r.cookies['JSESSIONID']
    r = requests.get("https://www.nlsinfo.org/investigator/servlet1?set=STUDY&id=1.6", cookies={"JSESSIONID": cookie})
    return cookie

def _get_category(i, o, session, node="0"):
    r = requests.get("https://www.nlsinfo.org/investigator/servlet1?get=TREEVIEW&event=expand&node={0}".format(node), cookies={"JSESSIONID": session})
    try:
        j = r.json()
        for n in j['nodes']:
            n['parent'] = node
            o.put(('print', n))
            if n['hasChildren']:
                o.put(('count', 1))
                i.put(int(n['id']))
    except:
        print r.text
        raise
    o.put(('count', -1))

def _category_runner(i, o, session):
    while True:
       node = i.get()
       if None == node:
           return
       _get_category(i, o, session, node)

def get_categories(j=24):
    session = Session()
    i = Queue()
    o = Queue()
    p = []
    for _ in range(j):
        k = Process(target=_category_runner, args=(i,o, session))
        k.start()
        p.append(k)
    c = 1
    _get_category(i, o, session)
    while c != 0:
        k = o.get()
        if k[0] == 'print':
            yield k[1]
        elif k[0] == 'count':
            c += k[1]
    for _ in p:
        i.put(None)
    for _ in p:
        _.join()
