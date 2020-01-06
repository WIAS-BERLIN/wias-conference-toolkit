#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Builds an xml data base that can be used to for an app. 
# 
# Reads   The database ../xml/db.xml
#
# Creates app-general/schedule.xml
#         This xml file can be uploaded to a web server, and included in a schedule viewer App
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

import datetime
from lxml import objectify
from lxml import etree
import pytz
import uuid
from html import escape  # python 3.x

import syspath
syspath.append_parent_path()
import config


# Adjust dates for your event in ../config/__init__.py


def get_name(p_xml):
    return " ".join((str(p_xml.first_name), str(p_xml.last_name)))

xmlschema_doc = etree.parse("../xml/wias-ct.xsd")
xmlschema = etree.XMLSchema(xmlschema_doc)

parse = objectify.makeparser(schema=xmlschema)

with open("../xml/db.xml", "r") as f:
    xmltree = objectify.parse(f, parse)

db_root = xmltree.getroot()

sched_root = etree.Element('schedule')
sched_xml = etree.ElementTree(sched_root)

etree.SubElement(sched_root, 'version').text = "0.1"

conf_xml = etree.SubElement(sched_root, 'conference')
etree.SubElement(conf_xml, 'title').text = config.conference_name
etree.SubElement(conf_xml, 'acronym').text = config.conference_acronym
etree.SubElement(conf_xml, 'start').text = config.firstday
etree.SubElement(conf_xml, 'end').text = config.lastday
etree.SubElement(conf_xml, 'days').text = str(len(config.day2num))
etree.SubElement(conf_xml, 'timeslot_duration').text = "{:}:00".format(str(config.timeslotduration))
etree.SubElement(conf_xml, 'base_url').text = config.baseurl

rooms = set(db_root.xpath("//room/text()"))

for k, v in config.day2num.items():
    day_xml = etree.SubElement(sched_root, 'day')
    day_xml.attrib["date"] = config.get_xml_date(k)
    day_xml.attrib["start"] = config.get_xml_datetz(k, config.day_start_time)
    day_xml.attrib["end"] = config.get_xml_datetz(k, config.day_end_time)
    day_xml.attrib["index"] = str(v-config.index_offset)

    for room in rooms:
        room_xml = etree.SubElement(day_xml, 'room')
        room_xml.attrib["name"] = str(room)
        for session in db_root.schedule_sessions.xpath("./schedule_session[timeslot/day='{:}'][room='{:}']".format(k, room)):
            start = str(session.timeslot.start)
            ev = etree.SubElement(room_xml, 'event')
            ev.attrib["id"] = str(session.ID)
            ev.attrib["guid"] = str(uuid.uuid4())
            ev.attrib["slot"] = str(session.timeslot.slot)
            etree.SubElement(ev, 'room').text = room
            etree.SubElement(ev, 'title').text = str(session.title)
            etree.SubElement(ev, 'subtitle').text = ''
            etree.SubElement(ev, 'type').text = ''
            etree.SubElement(ev, 'date').text = config.get_xml_datetz(k, start)
            etree.SubElement(ev, 'start').text = start
            etree.SubElement(ev, 'duration').text = config.sessionslotduration
            etree.SubElement(ev, 'abstract').text = "To be decided"
            title_slug = str(session.title).replace(" ", "_").replace("(", "").replace(")", "")
            etree.SubElement(ev, 'slug').text = "{:}-{:}-{:}".format(config.conference_slug,session.ID, title_slug)
            if hasattr(session, "cluster") and session.cluster > 0:
                etree.SubElement(ev, 'track').text = db_root.schedule_sessions.xpath("//cluster[ID='{:}']/title/text()".format(session.cluster))[0]
                ev.attrib["cluster"] = str(session.cluster)
            else:
                etree.SubElement(ev, 'track').text = ""
                ev.attrib["cluster"] = "error"

            presenters = []
            if not hasattr(session, "paper"):
                print("ERROR: session {:} has no paper".format(session.ID))
                continue

            descr = []
            for p in session.paper:
                paper_xml = db_root.xpath("//talk[ID='{:}']".format(p.paperid))[0]
                presenter = db_root.xpath("//person[ID='{:}']".format(paper_xml.presenter))[0]
                presenters.append((get_name(presenter), presenter.ID))
                title_line = "<b> {:} </b> {:}".format(paper_xml.title, get_name(presenter))

                if hasattr(p, "author"):
                    authors = [db_root.xpath("//person[ID='{:}']".format(a)) for a in p.author]
                else:
                    authors = []

                descr.extend((", ".join([title_line]+authors), str(paper_xml.abstract), "<br>"))

            etree.SubElement(ev, 'description').text = "<br>".join(descr)

with open("schedule.xml", "wb") as f:
    f.write(etree.tostring(sched_root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
