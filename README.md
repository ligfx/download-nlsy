Analyzed the network requests and saw that most calls are to `servlet1` with some GET parameters. The request with parameter `get=TREEVIEW` returned a JSON file of the toplevel categories. Clicking on a category resulted in another request of type `get=TREEVIEW` with subcategories.

```
curl "https://www.nlsinfo.org/investigator/servlet1?get=TREEVIEW&event=expand&node=0" -b "JSESSIONID=84d9dfa68f5af4ccb01839822126.nlsws00"

{"id":68551.0,"desc":"1.6","count":0,"nodes":[
  {"label":"Education, Training & Achievement Scores","id":68552.0,"count":17778,"hasChildren":true},
  {"label":"Employment","id":68783.0,"count":22551,"hasChildren":true},
  ...
]

GET /investigator/servlet1?get=TREEVIEW&event=expand&node=68552 HTTP/1.1
Host: www.nlsinfo.org
Referer: https://www.nlsinfo.org/investigator/pages/search.jsp
Cookie: preferences=showref=true&showqname=false&showtitle=false&showyear=false&showdata=false&shownav=false&showaint=false&showallaint=false&showsec=false&showpref=false&pref=PRIMARY&usecaseid=false&collection=true&sas=false&spss=false&stata=false&codebook=true&csv=true&xml=false&csvuseqname=false&xmluseqname=false&collectiontype=RNUM_LIST&cdbkstyle=NONE&sdf=true&showvalidn=false&showvtype=false&enablerollup=false; JSESSIONID=84d9dfa68f5af4ccb01839822126.nlsws00; has_js=1; __utma=80463176.1737560674.1389136161.1389136161.1389829532.2; __utmb=80463176.1.10.1389829532; __utmc=80463176; __utmz=80463176.1389136161.1.1.utmcsr=bls.gov|utmccn=(referral)|utmcmd=referral|utmcct=/bls/exit_BLS.htm

{"id":68552.0,"desc":"Education, Training & Achievement Scores","count":17778,"nodes":[
  {"label":"Education","id":68553.0,"count":15310,"hasChildren":true},
  ...
]
```

After that, it looks like individual question data shows up in calls like `servlet1?get=Results&criteria=TREENODE|EQ|68723`.

Once you have a parent node, it looks like `curl "https://www.nlsinfo.org/investigator/servlet1?get=Results&criteria=TREENODE%7CEQ%7C68723" -b "preferences=showref=true&showqname=true&showtitle=true&showyear=false&showdata=false&shownav=false&showaint=false&showallaint=false&showsec=false&showpref=false&usecaseid=false; JSESSIONID=84d9dfa68f5af4ccb01839822126.nlsws00;"`, with an appropriate session ID, will get you the questions.

```
<?xml version="1.0" encoding="UTF-8"?>
<DATA>
  <TABLEOPTIONS>
    <MODE>ID</MODE>
    <CURRENT_ID />
    <SHOWNAV>true</SHOWNAV>
    <FIRST_ID>1</FIRST_ID>
    <PREVIOUS_ID />
    <NEXT_ID />
    <LAST_ID>9022</LAST_ID>
    <QYEAR_COLUMN_NAME>YEAR</QYEAR_COLUMN_NAME>
  </TABLEOPTIONS>
  <ROW value="Z90341.00">
    <RNUM>Z90341.00</RNUM>
    <QNAME>CVC_ACT_SCORE_2007</QNAME>
    <TITLE><![CDATA[HIGHEST ACT SCORE 2007]]></TITLE>
    <VARTYPE><![CDATA[CREATED VARIABLES]]></VARTYPE>
    <YEAR>XRND</YEAR>
    <VALIDN>2425</VALIDN>
    <PREF>PRIMARY</PREF>
    <DATA />
  </ROW>
  <ROW value="Z90342.00">
    <RNUM>Z90342.00</RNUM>
    <QNAME>CVC_ACT_RND_2007</QNAME>
    <TITLE><![CDATA[ROUND REPORTED HIGHEST ACT SCORE 2007]]></TITLE>
    <VARTYPE><![CDATA[CREATED VARIABLES]]></VARTYPE>
    <YEAR>XRND</YEAR>
    <VALIDN>2425</VALIDN>
    <PREF>PRIMARY</PREF>
    <DATA />
  </ROW>
</DATA>
```

If the category has more than 5000 variables, you receive an XML file with toplevel node `<ERROR>`, and HTTP 200 OK.

# Tagsets

A tagset file is an "\r\n"-separated list of RNUMs, where the period in the RNUM in the server response disappears.

```
$ curl "https://www.nlsinfo.org/investigator/servlet1?get=tagsetcount" -b "JSESSIONID=ca456bfdda9530e47b735a9c9431.nlsws00"
7
$ curl -F upfile=@default.NLSY97 "https://www.nlsinfo.org/investigator/servlet1?cmd=uploadtagset" -b "JSESSIONID=ca456bfdda9530e47b735a9c9431.nlsws0"
$ curl "https://www.nlsinfo.org/investigator/servlet1?get=tagsetcount" -b "JSESSIONID=ca456bfdda9530e47b735a9c9431.nlsws00"
6902
```

# Codebook

Pretty easy. `https://www.nlsinfo.org/investigator/servlet1?get=codebook&rnum=R7297600`, probably with a valid JSESSIONID.

# Downloads

```
https://www.nlsinfo.org/investigator/servlet1?set=preference&csv=true
https://www.nlsinfo.org/investigator/servlet1?collection=on&csv=on&csvuseqname=false&event=start&cmd=extract&desc=default
-> job:y3LIGRiNb09WBK
https://www.nlsinfo.org/investigator/servlet1?job=y3LIGRiNb09WBK&event=progress&cmd=extract&_=1389902657180
-> where _ is unix time
-> {"status_response":{"message":"Starting Extract","name":"default","state":"A","job":"y3LIGRiNb09WBK"}}
-> checking every second or so
-> when state == "S", it's done? or message == ""?
https://www.nlsinfo.org/investigator/servlet1?get=downloads&study=current
<DATA>
 <ROW>
  <DATE>2014-01-16 15:06:29</DATE>
  <STUDY>NLSY97</STUDY>
  <NAME>default</NAME>
  <LINK><![CDATA[./../downloads/y3LIGRiNb09WBK/default.zip]]></LINK>
  <SIZE>6.6M</SIZE>
 </ROW>
</DATA>
```

