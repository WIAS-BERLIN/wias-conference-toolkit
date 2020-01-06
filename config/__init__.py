import os
import pytz
import datetime
from collections import OrderedDict

# Conference title and acronyms

conference_name = "EVENT FULL NAME"
conference_acronym = "EVENT ACRONYM"
conference_slug = "iccopt2019"
baseurl = "https://wias-berlin.de"
timeslotduration = 25

# used in app_general/build_schedule.py
sessionslotduration = "1:15" 

# Conference dates

start2slot = OrderedDict(
             (("05.08.2019 09:30", 'P'),
              ("05.08.2019 11:00", 1),
              ("05.08.2019 13:45", 2),
              ("05.08.2019 15:30", 'SP'),
              ("05.08.2019 16:20", 'BP'),
              ("06.08.2019 09:00", 'P'),
              ("06.08.2019 10:30", 1),
              ("06.08.2019 13:15", 2),
              ("06.08.2019 14:45", 3),
              ("06.08.2019 16:30", 4),
              ("07.08.2019 09:00", 'P'),
              ("07.08.2019 10:15", 'SP1'),
              ("07.08.2019 11:30", 1),
              ("07.08.2019 14:15", 2),
              ("07.08.2019 16:00", 3),
              ("07.08.2019 17:30", 'SP2'),
              ("08.08.2019 09:00", 1),
              ("08.08.2019 10:45", 2),
              ("08.08.2019 13:30", 3),
              ("08.08.2019 15:15", 'SP'),
              ("08.08.2019 16:15", 'P'),
              ))

day2str = {"05.08.2019": "Mon",
           "06.08.2019": "Tue",
           "07.08.2019": "Wed",
           "08.08.2019": "Thu",
          }

day2num = {'Mon': 5,
           'Tue': 6,
           'Wed': 7,
           'Thu': 8,
           }
room2size = {"H 0104": "644",
             "H 0105": "1192",
             "H 0106": "99",
             "H 0107": "144",
             "H 0110": "193",
             "H 1012": "254",
             "H 1058": "244",
             "H 1029": "70",
             "H 3013": "40",
             "H 3007": "80",
             "H 3006": "100",
             "H 3012": "40",
             "H 3025": "50",
             "H 3008": "30",
             "H 2038": "50",
             "H 3004": "50",
             "H 3002": "40",
             "H 2032": "235",
             "H 0112": "99",
             "H 2035": "28",
             "H 2037": "28",
             "H 2036": "36",
             "H 3005": "48",
             "H 0111": "99",
             "H 1028": "231",
             "H 2013": "260",
             "H 2053": "243",
             "H 2033": "46",
          }

sessionslot2num = {'Mon1': 1,
           'Mon2': 2,
           'Tue1': 3,
           'Tue2': 4,
           'Tue3': 5,
           'Tue4': 6,
           'Wed1': 7,
           'Wed2': 8,
           'Wed3': 9,
           'Thu1': 10,
           'Thu2': 11,
           'Thu3': 12,
           }


def get_xml_date(day):
    return "2019-08-0{:}".format(day2num[day])

def get_xml_datetz(day, time):
    h, m = time.split(':')
    datetimeobject = datetime.datetime(2019, 8, day2num[day], int(h), int(m))
    localtime = pytz.timezone('Europe/Berlin').localize(datetimeobject)
    return localtime.isoformat()
    #return datetime.datetime(2019, 8, config.day2num[day], int(h), int(m)).astimezone(pytz.timezone('Europe/Berlin')).isoformat()

# used in app_general/build_schedule.py
firstday = get_xml_date('Mon')
lastday = get_xml_date('Thu')
day_start_time = "09:00"
day_end_time = "18:00"
index_offset = 4

# Late submissions

old_paper_date = 'Mar 18'



# Mailing

#mail_user = os.environ['USER']
mail_user = 'loebhard'
sender_email = "ICCOPT 2019 <info@iccopt2019.berlin>"
smtp_server = "smtp.wias-berlin.de"
port = 465

email_footer = """
Best regards,
Local Organizers of the ICCOPT 2019

------------------------------------
Weierstrass Institute for Applied Analysis and Stochastics (WIAS)
Leibniz Institute in Forschungsverbund Berlin e.V.
(member of Leibniz Association)
------------------------------------
Mohrenstr. 39
10117 Berlin
Germany
------------------------------------
e-mail: info@iccopt2019.berlin
phone:  +49 30 20372-583 (Cecilia Bonetti)
fax:    +49 30 20372-300
web:    https://iccopt2019.berlin
------------------------------------
"""
