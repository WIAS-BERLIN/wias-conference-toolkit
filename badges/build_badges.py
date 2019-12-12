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

from lxml import etree
from lxml import objectify

import syspath
syspath.append_parent_path()
import wiasct


db_tree = etree.parse('../xml/db.xml')
db_root = db_tree.getroot()

tex_file = []

long_names = ("Long-Name-to-scale",)

for person in wiasct.sort_persons(db_root.xpath("//person[summer_school][not(canceled)]")):
    name = person.findtext('last_name')
    fsize = r"\huge"
    if name in long_names:
        fsize = r"\LARGE"
    tex_file.append("\\nametag{{{fname}}}{{{lname}}}{{{fsize}}}%".format(fname=person.findtext('first_name'),lname=name,fsize=fsize))

with open("summer-school-participants.tex", "w") as f:
    f.write('\n'.join(tex_file))

for person in wiasct.sort_persons(db_root.xpath("//person")):
    name = person.findtext('last_name')
    fsize = r"\huge"
    if name in long_names:
        fsize = r"\LARGE"
    tex_file.append("\\nametag{{{fname}}}{{{lname}}}{{{fsize}}}%".format(fname=person.findtext('first_name'),lname=name,fsize=fsize))

with open("all-participants.tex", "w") as f:
    f.write('\n'.join(tex_file))
