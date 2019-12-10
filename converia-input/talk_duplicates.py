#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Lists persons who seem to plan two talks or other contributions. Some conferences want to avoid this. 
# 
# Reads   the file paper.xml which can be downloaded from Converia
#
# Creates text files listing persons who seem to plan two talks in
#         info-files/duplicate_talks_DATE.txt
#
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




import subprocess
import csv
import sys
from time import gmtime, strftime
import xml.etree.ElementTree as ET
import difflib

def similar(seq1, seq2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.9

def compare_names(name, fname, cmp_name, cmp_fname):
    return similar(name+fname, cmp_name+cmp_fname) or similar(name+fname,cmp_fname+cmp_name)

datestring = strftime("%Y-%m-%d", gmtime())

tree = ET.parse('paper.xml')
root = tree.getroot()


###### Collect presenters from xml file ######

subtalks_presenter = {} 
nocontacts = ''
multiplecontacts = ''

speakerslist = []

for paper in root: 
    if paper.find('paper_type').text=='PAPER':
        authors = paper.find('authors')
        authorcount = 0
        for author in authors: 
            if author.find('type').text=='Contact' or author.find('type').text=='Presenter':
                authorcount+=1
#                nameetc = {'name': author.find('name').text, 'prename': author.find('prename').text, 'talk_id': paper.get('id'), 'session_id': author.find('paper_paper_id').text}
                nameetc = {'name': author.find('name').text, 'prename': author.find('prename').text, 'talk_id': paper.get('id'), 'session_id': paper.find('paper_paper_id').text, 'title': paper.find('paper_title').text}
                speakerslist.append(nameetc)
                if authorcount>1: 
                    multiplecontacts+=str(paper.get('id'))+', '
                if authorcount<1: 
                    nocontacts+=str(paper.get('id'))+', '

duplicate_talks_string = "\n\nTitle ID, (Session) / ID (Session) Name\n"
print(duplicate_talks_string)

for index, speaker in enumerate(speakerslist):
    name = speaker['name']
    fname = speaker['prename']
    for cmp_index, cmp_speaker in enumerate(speakerslist): 
        if cmp_index>index: 
            cmp_name = cmp_speaker['name']
            cmp_fname = cmp_speaker['prename']
            if compare_names(name,fname,cmp_name,cmp_fname):
                if similar(speaker['title'],cmp_speaker['title']): 
                    sametitle = 'SAME '

                else:
                    sametitle = '     '
                if speaker['session_id']=='0':
                    session_id = '    0'
                else:
                    session_id = speaker['session_id']
                if cmp_speaker['session_id']=='0':
                    cmp_session_id = '    0'
                else:
                    cmp_session_id = cmp_speaker['session_id']
                duplicate_talks_string += '\n'+sametitle+speaker['talk_id']+" ("+session_id+") / "+cmp_speaker['talk_id']+" ("+cmp_session_id+") "+name+" "+fname+" / "+cmp_name+" "+cmp_fname
                print(sametitle+speaker['talk_id']+" ("+session_id+") / "+cmp_speaker['talk_id']+" ("+cmp_session_id+") "+name+" "+fname+" / "+cmp_name+" "+cmp_fname)


outputstring ='\n\nTalks with more than one presenter/contact author: '+multiplecontacts
outputstring +='\nTalks with less than one presenter/contact author: '+nocontacts

print(outputstring)

filecontent = outputstring+duplicate_talks_string

filename = "info-files/duplicate_talks_{}.txt".format(datestring)
fileSessions = open(filename, "w")
fileSessions.write("%s" %filecontent)
fileSessions.close()

print('\nA list of duplicate talks was exported to the file {}'.format(filename))
