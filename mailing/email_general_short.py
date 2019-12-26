#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Sample file for mass mailing to speakers of talks with missing talk data
# 
# Copy this file and fill in details to your specific mailing. 
# Mail server details need to be configured in ../config/__init__.py
#

copyright_string = """
*********************************************************************************************
Copyright (c) 2019 Weierstrass Institute for Applied Analysis and Stochastics Berlin (WIAS)

This file is part of the WIAS Conference Toolkit. 

The WIAS Conference Toolkit is free software: you can redistribute
it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*********************************************************************************************

"""

print(copyright_string)

__author__ = "Rafael Arndt, Olivier Huber, Caroline Löbhard, Steven-Marian Stengl"
__copyright__ = "Copyright 2019, WIAS"
__license__ = "GPL"
__maintainer__ = "Caroline Löbhard"
__email__ = "oracline@gmail.com"

from lxml import etree
import smtplib
import ssl
import getpass
import datetime
from send_email import send_email

tree = etree.parse('../xml/db.xml')
#tree = etree.parse('xml/test-db.xml')
root = tree.getroot()



msg_subject = '. . . URGENT: Finalize your talk data by July 8th'

msg_bcc = 'BCC Recipient <for@documentation.com>'

#recipients = root.xpath("//person[ID=124599]")

# Victims of testing
# 153832 Amal
# 154034 Olivier
# 153772 Rafael
# 124599 Caroline

msg_template = """Dear {fname} {name},

The conference book containing your abstract needs to be sent to the printing company soon.
If you do not reply to this email with an update by Monday, 8th, the following data will be included: 

Title: {title}

Abstract: {abstract}

Session: {session}

We look forward to welcoming you in Berlin!
Best regards,
Local Organizers of the ICCOPT 2019
"""

# talks with short abstracts or short titles, but a special session is included
short_talks = root.xpath("//talk[string-length(abstract) < 20 or string-length(title) < 7][session!='30790']")

# Send only to test team (put IDs of talks of the test team)
# short_talks = root.xpath("//talk[ID=31187 or ID=29564]")

password = getpass.getpass('Type your password and press enter: ')

for talk in short_talks:
    print(talk.findtext('ID'))
    session = root.xpath("//schedule_session[paper/paperid={:}]".format(talk.findtext("ID")))
    p = root.xpath("//person[ID={:}]".format(talk.find('presenter').text))

    organizers = []
    for organizer in session[0].xpath('./organiser'):
        organizers.append(root.xpath("//person[ID={:}]".format(organizer.text))[0].findtext('last_name'))
    session_text = session[0].findtext('title')
    if organizers:
        session_text += " ({:})".format(", ".join(organizers))

    kw = {'title': talk.findtext('title'),
          'abstract': talk.findtext('abstract'),
          'session': session_text
          }
    print(p[0].findtext('email'))
    #print(msg_template.format(fname=p[0].findtext('first_name'), name=p[0].findtext('last_name'), **kw))
    send_email(msg_subject, msg_template, p, msg_bcc, kw, True, password)
