#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Email sender function send_email, which is called by email_* functions.
#
# Functionality:
# send_email(msg_subject, msg_template, person_xml_list, msg_bcc, kw_dicts, dry_run=False, password=None)
# see also email_*
#

#
# *********************************************************************************************
# Copyright (c) 2019 Weierstrass Institute for Applied Analysis and Stochastics Berlin (WIAS)
# 
# This file is part of the WIAS Conference Toolkit. 
# 
# The WIAS Conference Toolkit is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# *********************************************************************************************

__author__ = "Rafael Arndt, Olivier Huber, Caroline Löbhard, Steven-Marian Stengl"
__copyright__ = "Copyright 2019, WIAS"
__license__ = "GPL"
__maintainer__ = "Caroline Löbhard"
__email__ = "oracline@gmail.com"


import copy
import datetime
import getpass
import smtplib
import ssl
import sys
import syspath
syspath.append_parent_path()
import wiasct
import config

def send_email(msg_subject, msg_template, person_xml_list, msg_bcc, kw_dicts, dry_run=False, password=None):
    context = ssl.create_default_context()

    print("Dry run mode is {:}. This can be changed in the arguments in the function call of send_email.".format(dry_run))
    if not password:
        password = getpass.getpass('Type the password for {:} and press enter: '.format(config.mail_user))

    with smtplib.SMTP_SSL(config.smtp_server, config.port, context=context) as server:
        server.login(config.mail_user, password)
        time = datetime.datetime.now()
        failure_file = 'doc_mailings/'+time.strftime('%Y-%m-%d-%H-%M')+'-failed_email.csv'
        success_file = 'doc_mailings/'+time.strftime('%Y-%m-%d-%H-%M')+'-successful_email.csv'

        if not isinstance(person_xml_list, list):
            print("ERROR: 3rd argument is not a list!")
            sys.exit(1)

        for p in person_xml_list:
            headers = {
                'Content-Type': 'text/plain; charset=utf-8',
                'Content-Disposition': 'inline',
                'Content-Transfer-Encoding': '8bit',
                'From': config.sender_email,
                'To': p.findtext('email'),
                'Bcc': msg_bcc,
                'Date': time.strftime('%a, %d %b %Y %H:%M:%S %Z'),
                'X-Mailer': 'python',
                'Subject': msg_subject
            }
            msg = ''
            for key, value in headers.items():
                msg += "%s: %s\n" % (key, value)
            lkw = copy.deepcopy(kw_dicts)
            institution = p.xpath('./address/institution/text()')
            if institution and institution[0]:
                lkw['institution'] = institution[0]

            if 'Cc' in kw_dicts:
                headers['Cc'] = kw_dicts['Cc']

            msg += msg_template.format(fname=p.findtext('first_name'), name=p.findtext('last_name'), **lkw)
            rcpt = [headers['To'], headers['Bcc']]
            if 'Cc' in headers:
                rcpt.append(headers['Cc'])
            if not dry_run:
                err = server.sendmail(headers['From'], rcpt, msg.encode('utf-8'))
                print(err)
                if err:
                    with open(failure_file, 'a') as f:
                        for k, v in err.items():
                            f.write('"{:}","{:}","{:}"\n'.format(k, msg_subject, v))
                else: 
                    with open(success_file, 'a') as f:
                        f.write('"{:}","{:}"\n'.format(headers['To'], msg_subject))
            else:
                print("email would be sent to: {:}".format(rcpt))
