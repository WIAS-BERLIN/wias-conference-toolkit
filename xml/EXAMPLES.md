# Examples for the use of the xml data base #


select persons going to to summer school (irrespective of value)
```python
db_root.xpath("//person[summer_school]")
```

select prolific authors
```
db_root.xpath("//person[count(contribution_author)+count(contribution_presenter)>2]")
```

look for short abstract
```
db_root.xpath("//talk[string-length(abstract) < 50]/ID/text()")
db_root.xpath("//talk[string-length(title) < 7]/title/text()")
```

Look for presenters with short abstracts (probably "t.b.a.")
```
[db_root.xpath("//person[contribution_presenter=$talkid]/*[name()='first_name' or name()='last_name' or name()='email']/text()", talkid=tid) for tid in db_root.xpath("//talk[ string-length(abstract) < 50 ]/ID/text()")]
```

Duplicate emails
```
xpatheval = etree.XPathEvaluator(db_root)
cmp_email = etree.XPath("count(participants/person[email = $email])")
[e for e in xpatheval("//email/text()") if cmp_email(db_root, email=e) > 1]
```

People who have a free registration, but already paid
```
[(e.findtext('first_name'), e.findtext('last_name'), e.findtext('email')) for e in db_root.xpath("//person[role and amount_paid>150]")]
```
[(e.findtext('first_name'), e.findtext('last_name'), e.findtext('email')) for e in db_root.xpath("//person[(role or contains(email,'wias-berlin.de') or contains(email,'u-berlin.de') or contains(email,'zib.de')) and amount_paid>0]")]



Count number of nodes:
```
db_root.xpath("//talk[count(author) > 7]")
```

More complex example: iterate over some schedule sessions, find the associated paper and then get the session/cluster from them
```
for s in db_root.xpath("//schedule_session[timeslot/day='Mon'][timeslot/slot='1']"):
    for p_id in s.xpath("./paper/paperid/text()"):
        print("paper id {:}".format(p_id))
        s_id = db_root.xpath("//talk[ID='{:}']/session/text()".format(p_id))
        if s_id:
            sid = s_id[0]
        else:                                                                                                         
            sid = "unkown"

        if sid != "unkown" and int(sid) > 100:
            cluster_id = db_root.xpath("//session[ID='{:}']/cluster/text()".format(sid))[0]
        else:
            cluster_id = sid
            sid = "no session"
        print("session ID: {:} Cluster ID: {:}".format(sid, cluster_id))
```

Show parallel sessions with 2 talks
```
sorted([(db_root.xpath('//cluster[ID={:}]'.format(ss.findtext('cluster')))[0].findtext('shortcut'), ss.find('timeslot').findtext('day'),ss.find('timeslot').findtext('slot'),ss.findtext('room'),ss.findtext('title') ) for ss in db_root.xpath('//schedule_session[count(paper)=2][cluster!=1]')])
```
