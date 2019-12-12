#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Produces DIN A4 dinner tickets based on the data given in the database ../xml/db.xml
# 
# Reads   ../xml/db.xml
#
# Creates The tex-file dinnerparticipants.tex, which is included in the latex template vouchers-dinner.tex. 
#         The latter can be compiled with Latex to produce a pdf with all dinner tickets. 
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

tex_file = ""


organizing_committee=["Mustermann",
                      "Doe"]
                      
free_ticket_roles = ['Best Paper Finalist', 'Plenary speaker', 'Semiplenary speaker', 'Summer School lecturer', 'Best Paper Committee', 'Program Committee', 'Cluster chair']


number_one_ticket = 0
number_two_tickets = 0
number_waiting_list = 0
number_vip = 0

# DO NOT CHANGE THIS: the ordering here must match the one given to TUBS --xhub
for person in wiasct.sort_persons_tubsorder(db_root.xpath("//person[dinner>=0][not(canceled)]")):
    dinner_ticket=0
    for d in person.iterfind('dinner'):
        if int(d.text) in (0,1,3):
            dinner_ticket += 1
        elif int(d.text) == 2:
            dinner_ticket = 2
    color='gray'
    for role in person.iterfind('role'):
        if role.text in free_ticket_roles or person.findtext('last_name') in organizing_committee:
            color='logoorange'
            number_vip+=1
            break
    if dinner_ticket == 1:
        number_one_ticket +=1
    elif dinner_ticket == 2: 
        number_two_tickets +=1
        
    tex_file += "\\dinnerparticipant{{{dinnerticket}}}{{{lname}}}{{{fname}}}{{{special}}}\n".format(dinnerticket=dinner_ticket, fname=person.findtext('first_name'),lname=person.findtext('last_name'), special=color)

print("\n\nOne ticket: {one}\nTwo tickets: {two}\nTotal number of tickets: {total}\n\nWaiting list: {waiting}\n\nVIP Ticket: {vip}".format(one=number_one_ticket,two=number_two_tickets,total=str(number_one_ticket+2*number_two_tickets),waiting=len(db_root.xpath("//person[dinner<0]")),vip=number_vip))
with open("dinnerparticipants.tex", "w") as f:
    f.write(tex_file)
