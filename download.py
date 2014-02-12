#!/usr/bin/env python

from lxml import etree
import os
import os.path
import requests
import sys
import time

f = sys.argv[1]

from nlsy import Session

session = Session()
print session

url = "https://www.nlsinfo.org/investigator/servlet1?cmd=LOADPREDEFINEDTAGSET&id=133&value=false"
requests.get(url, cookies={'JSESSIONID': session})
url = "https://www.nlsinfo.org/investigator/servlet1?cmd=uploadtagset"
requests.post(url, files={'upfile': open(f, 'rb')}, cookies={'JSESSIONID': session})
url = "https://www.nlsinfo.org/investigator/servlet1?get=tagsetcount"
r = requests.get(url, cookies={'JSESSIONID': session})
print "{} variables being downloaded".format(r.text)

url = "https://www.nlsinfo.org/investigator/servlet1?set=preference&csv=true"
requests.get(url, cookies={'JSESSIONID': session})
url = "https://www.nlsinfo.org/investigator/servlet1?set=preference&codebook=true"
requests.get(url, cookies={'JSESSIONID': session})
name = f.rsplit(".", 1)[0]
print name
url = "https://www.nlsinfo.org/investigator/servlet1?collection=on&csv=on&csvuseqname=false&codebook=on&event=start&cmd=extract&desc={}".format(name)
r = requests.get(url, cookies={'JSESSIONID': session})
job = r.text
print job
assert job.startswith('job:')
job = job.split('job:', 1)[1]

while True:
	url = "https://www.nlsinfo.org/investigator/servlet1?job={}&event=progress&cmd=extract&_={}".format(job, int(time.time() * 1000))
	r = requests.get(url, cookies={'JSESSIONID': session})
	j = r.json()
	print j['status_response']['message']
	if j['status_response']['state'] == 'S':
		url = "https://www.nlsinfo.org/investigator/servlet1?get=downloads&study=current"
		r = requests.get(url, cookies={'JSESSIONID': session})
                print r.text
		x = etree.fromstring(r.text)
                link = x.xpath(".//NAME[text()='{}']/../LINK/text()".format(name))[0]
		link = "https://" + os.path.normpath(os.path.join("www.nlsinfo.org/investigator/servlet1", link))
                print "curl -O {} -b JSESSIONID={}".format(link, session)
		os.execvp("curl", ("curl", "-O", link, "-b", "JSESSIONID={}".format(session)))
	time.sleep(1)

