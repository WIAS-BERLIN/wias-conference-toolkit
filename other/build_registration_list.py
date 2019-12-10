#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Rebuilds the list EVENT_Registrationlist.csv from the data base ../xml/db.xml. This can help if late changes/cancelations are tracked in this data management system, but the conference admoinistration nevertheless needs the data in the original list format. 
# 
# Reads   The database ../xml/db.xml
#
# Creates EVENT_Registrationlist_wiasct.csv
#         EVENT_Registrationlist_wiasct_CANCELLED.csv
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

__author__ = "Rafael Arndt, Olivier Huber, Caroline Löbhard, Steven Marian Stengl"
__copyright__ = "Copyright 2019, WIAS"
__license__ = "GPL"
__maintainer__ = "Caroline Löbhard"
__email__ = "oracline@gmail.com"

from collections import OrderedDict
import csv
from lxml import etree, objectify

import syspath
syspath.append_parent_path()

import wiasct

db_root = wiasct.parse_iccopt_db('../xml/')

columns = ("First Name",
           "Name",
           "Institution",
           "PhD",
           "dinner ticket",
           "dinner waiting list",
           "Conference book",
           "VIP T-shirt",
           "Reimbursement",
           "COAP meeting",
           "SIOPT meeting",
           "Colored badge",
#           "OMS meeting",
#           "JNSA meeting",
          )


def add_participant(tubs_list, pd):
    new_row = ['']*len(columns)

    for k, v in pd.items():
        if k not in columns:
            print("ERROR: key {:} is not an allowed column value".format(k))
            sys.exit(1)

        new_row[columns.index(k)] = v

    tubs_list.append(new_row)
    return

def fill_list(persons_list):
    p_list = [columns, ['']*len(columns)]
    for p in persons_list:
        # This is Tensorial Tensorial
        if p.ID == '130762':
            continue
        pd = OrderedDict(zip(columns, ['']*len(columns)))
        pd["First Name"] = p.first_name
        pd["Name"] = p.last_name
        if hasattr(p, "address"):
            pd["Institution"] = p.address.institution

        if "Dr" in p.title or "prof" in str(p.title).lower():
            pd["PhD"] = 1

        if hasattr(p, "dinner"):
            for d in p.dinner:
                if d in (1, 2 ,3):
                    if not pd["dinner ticket"]:
                        pd["dinner ticket"] = 1 if d in (1, 3) else 2
                    else:
                        pd["dinner ticket"] += 1
                elif d == -1:
                    pd["dinner waiting list"] = 1

            # This is a hack to detect 2 tickets
            if p.amount_paid in (515.0, 430.0) and pd["dinner ticket"] != 2:
                print("ERROR participant {:} {:} paid for 2 tickets but has {:}".format(p.first_name,p.last_name, pd["dinner ticket"]),
                        etree.tostring(p, pretty_print=True, encoding='utf-8').decode('utf-8'), pd["dinner ticket"])
                pd["dinner ticket"] = 2

        if hasattr(p, "book_of_abstract"):
            pd["Conference book"] = 1

        if hasattr(p, "meeting"):
            for m in p.meeting:
                pd[" ".join((str(m), "meeting"))] = 1

        if hasattr(p, "role"):
            for r in p.role:
                if r in ("Local Organizer", "Program Committee", "Cluster chair"):
                    pd["VIP T-shirt"] = 1

                if r in ("Grant", "Summer School lecturer", "Plenary speaker"):
                    pd["Reimbursement"] = 1

                if r in ("Local Organizer", "Local Helper", "Student Helper"):
                    pd["Colored badge"] = 1

        add_participant(p_list, pd)

    return p_list

# We iterate over the people who are participants (or likely to be)
# DO NOT CHANGE THE ORDERING METHOD HERE! --xhub
tubs_list = fill_list(wiasct.get_participants_tubsorder(db_root))

# This is all the late cancelation
cancelled_list = fill_list(wiasct.get_canceled_tubsorder(db_root))


with open("EVENT_Registrationlist_wiasct.csv", "w") as f:
    csv_writer = csv.writer(f)
    csv_writer.writerows(tubs_list)

with open("EVENT_Registrationlist_wiasct_CANCELLED.csv", "w") as f:
    csv_writer = csv.writer(f)
    csv_writer.writerows(cancelled_list)
