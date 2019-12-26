#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Sample file for mass mailing
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

from send_email import *

import syspath
syspath.append_parent_path()
import wiasct
import config

root = wiasct.parse_iccopt_db('../xml/')

msg_subject = 'Message subject'

msg_bcc = 'BCC Recipient <for@documentation.com>'

msg="""Dear {fname} {name},

sample text

We look forward to welcoming you in Berlin.
"""

msg += config.email_footer

# Testing on test team
#recipients = root.xpath("//person[ID=124599 or ID=154034 or ID=153772]")
#recipients = root.xpath("//person[ID=154034]")

# Manually exclude recipients from mass mailing
exclude_list = ('158029', '135115', '162015', '155023', '164139', '156529')
recipients_raw = wiasct.get_participants(root)

# Another example
# recipients_raw = root.xpath("//person[paiment_status='-1'][contribution_presenter][not(role)]") # (non-registered speakers)

recipients = [p for p in recipients_raw if str(p.ID) not in exclude_list and p.email]

print(len(recipients))
for p in recipients: 
    print(p.findtext('email'))

send_email(msg_subject, msg, recipients, msg_bcc, {}, True)
