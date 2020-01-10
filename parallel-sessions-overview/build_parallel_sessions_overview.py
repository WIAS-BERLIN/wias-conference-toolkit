#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Creates Parallel_sessions_overview.tex which can be compiled with pdflatex to get a pdf file with an overview on all talks in parallel sessions
#
# Reads   ../xml/db.xml
#         ../config/tex-templates/header_parallel_sessions_overview.tex
#         ../config/__init__.py
#
# Creates Parallel_sessions_overview.tex
#         output overview text
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

import syspath
syspath.append_parent_path()
import wiasct
import config

import subprocess
import csv
import sys
from time import gmtime, strftime
from lxml import etree
from lxml import objectify

import difflib

db_tree = etree.parse('../xml/db.xml')
db_root = db_tree.getroot()

datestring = strftime("%Y-%m-%d", gmtime())
infostring = ''

colors_tex = wiasct.cluster_colors_latex(db_root)

texfile_header = r"""\input{../config/tex-templates/header_parallel_sessions_overview.tex}
"""+colors_tex
texfile_footer = r"""
\end{document}"""

tex_file = texfile_header+r"""\titleheader{Overview on parallel sessions}{"""+datestring+"}\n"

tex_file += r"""\clustershortcuts{"""+wiasct.cluster_shortcuts_latex(db_root)+r"""}"""

for k, v in sorted(config.sessionslot2num.items(), key=lambda item: item[1]):
    print('  '+k)
    ss = db_root.xpath("./schedule_sessions/schedule_session[paper][timeslot/day='{:}'][timeslot/slot='{:}']".format(k[0:3],k[3]))
    if not(ss==[]):
        ss_times = '{:}--{:}'.format(ss[0].find('timeslot').find('start').text,ss[0].find('timeslot').find('end').text)
        tex_file+=r"""\section*{"""+k[0:3]+' '+k[3]+", "+ss_times+"}\n"
    for s_session in sorted(sorted(ss, key=lambda item: item.find("title").text), key=lambda item: int(item.find("cluster").text)):
    #for s_session in sorted(ss, key=lambda item: int(config.room2size[item.find("room").text]), reverse=True):
        tex_file+=r"""\schedulesession{"""+s_session.find('ID').text+r"}{" + s_session.find('title').text+"}"
        chairs = []
        for chairid in s_session.iterfind('chair'):
            chair = db_root.xpath("./participants/person[ID='{:}']".format(chairid.text))[0]
            chairs.append(wiasct.person_registration_color_lastname(chair))
        tex_file+="{"+s_session.findtext('room')+"}"
        print("      "+s_session.find('ID').text+' '+s_session.find('title').text)
        print("            Chair(s): {:}, Room: {:}, Size: {:}".format(", ".join(chairs), s_session.find('room').text, config.room2size[s_session.find('room').text]))
        talk_tex = ''
        for talk in s_session.iterfind('paper'):
            talk_data = db_root.xpath("./talks/talk[ID={:}]".format(talk.find('paperid').text))[0]
            presenter = db_root.xpath("./participants/person[ID='{:}']".format(talk_data.find('presenter').text))[0]
            cancelled = presenter.findtext('canceled')=="True"
            cancelled_strings = (r"\textcolor{gray}{", r"\ [canceled]}") if cancelled else ("","")
            #                talk_tex += r"""\talk{"""+talk.find('paperid').text+"}{"+presenter.find('first_name').text+' '+presenter.find('last_name').text+"}{}{"+wiasct.latexify(talk_data.find('title').text)+"}{"+wiasct.latexify(talk_data.find('abstract').text)+"}\n"
            talk_tex += r"""\talk{"""+talk.find('paperid').text+"}{"+cancelled_strings[0]+wiasct.person_registration_color(presenter)+cancelled_strings[1]+"}{}{"+wiasct.latexify(talk_data.find('title').text)+"}{"+wiasct.latexify(talk_data.find('abstract').text)+"}\n"
            print('            '+talk.find('paperid').text+' '+presenter.find('first_name').text+' '+presenter.find('last_name').text+', '+talk_data.find('title').text)
        tex_file+="{"+talk_tex+"}"
        if len(s_session.xpath('./session'))==0:
            session_type = 'contributed'
            print('            '+session_type)
            tex_file+="{"+session_type+'}'
        else:
            session_type = 'organized'
            session_organizers = []
            session_ids = []
            for sessionid in s_session.iterfind('session'):
                session_ids.append(sessionid.text)
                session_data = db_root.xpath("./sessions/session[ID={:}]".format(sessionid.text))[0]
                for orgaid in session_data.xpath("./organiser"):
                    orga = db_root.xpath("./participants/person[ID='{:}']".format(orgaid.text))[0]
                    session_organizers.append(orga.find('first_name').text+' '+orga.find('last_name').text)
            tex_file+="{organized by: "+", ".join(session_organizers)+"}"
        roomname = s_session.find('room').text
        roomsize = config.room2size[roomname]
        #tex_file+="{"+roomname.replace(' ','~')+r"""\newline"""+roomsize+'}'
        tex_file+="{"+roomname.replace(' ','~')+'}'
        cid = s_session.find('cluster').text
        tex_file+="{cluster"+cid+"}"
        tex_file+="{"+db_root.xpath('./clusters/cluster[ID={:}]'.format(cid))[0].find('shortcut').text+"}\n"
    tex_file+=r"""\newpage
"""

tex_file += texfile_footer

with open('Parallel_sessions_overview.tex', 'w') as f:
    f.write("%s" %tex_file)
