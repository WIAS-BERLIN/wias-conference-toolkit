#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Creates spreadsheets with an overview on the numbers of submitted talks etc. 
# 
# Reads   the file paper.xml which can be downloaded from Converia
#
# Creates csv files with submission data in the subfolder info-files/
#         info-files/DATE-overview.csv 
#         info-files/DATE-sessions.csv 
#         info-files/DATE-talks.csv 
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

__author__ = "Rafael Arndt, Olivier Huber, Caroline Löbhard, Steven-Marian Stengl"
__copyright__ = "Copyright 2019, WIAS"
__license__ = "GPL"
__maintainer__ = "Caroline Löbhard"
__email__ = "oracline@gmail.com"

from time import gmtime, strftime

datestring = strftime("%Y-%m-%d", gmtime())


import xml.etree.ElementTree as ET
tree = ET.parse('paper.xml')
root = tree.getroot()


###### Create list of clusters ######

cluster_list = []

for topic in root.iter('topic'):
    cluster = topic.find('name').text
    if not cluster in cluster_list: 
        cluster_list.append(cluster)
     
cluster_list.sort()


###### Prepare collection of cluster overview data ######


cluster_nr_sessions = []
cluster_nr_sessiontalks = []
cluster_nr_plaintalks = []
cluster_nr_totaltalks = []


###### Create csv table for sessions ######

session_table_string = r"""ID, eingereicht von, Cluster, Anzahl Talks;
"""

for topic in cluster_list: 
    nr_sessions = 0
    nr_talks_in_sessions = 0
    for session in root:
        if (session.find('paper_type').text=='SESSION' and session.find('topiclist').find('topic') is not None):
            cluster = session.find('topiclist').find('topic').find('name').text
            if cluster==topic:
                nr_sessions +=1
                session_table_string += session.get('id')+", "
                lastname = ' '
                if session.find('person_lastname').text is not None:
                    lastname = session.find('person_lastname').text
                session_table_string += lastname+", "
                session_table_string += cluster+", "
                talks_counter=0
                for paper in root:
                    if paper.find('paper_type').text=='PAPER' and paper.find('paper_paper_id').text==session.get('id'):
                        nr_talks_in_sessions+=1
                        talks_counter+=1
                session_table_string += str(talks_counter)
                session_table_string += r""";
"""
    cluster_nr_sessions.append(nr_sessions)
    cluster_nr_sessiontalks.append(nr_talks_in_sessions)


print(session_table_string)


fileSessions = open("info-files/"+datestring+"-sessions.csv", "w")
fileSessions.write("%s" %session_table_string.encode('utf8'))
fileSessions.close()


###### Create csv table for talks without session ######

talk_table_string = r"""ID, eingereicht von, Cluster;
"""

for topic in cluster_list: 
    nr_talks = 0
    for paper in root:
        if paper.find('paper_type').text=='PAPER' and  paper.find('paper_paper_id').text=='0':
            cluster = paper.find('topiclist').find('topic').find('name').text
            if cluster==topic:
                nr_talks +=1
                talk_table_string += paper.get('id')+", "
                talk_table_string += paper.find('person_lastname').text+", "
                cluster = paper.find('topiclist').find('topic').find('name').text
                talk_table_string += cluster
                talk_table_string += r""";
"""
    cluster_nr_plaintalks.append(nr_talks)

print(talk_table_string)

fileTalks = open("info-files/"+datestring+"-talks.csv", "w")
fileTalks.write("%s" %talk_table_string.encode('utf8'))
fileTalks.close()


###### Create csv table for cluster overview table ######

total_table_string = r"""Cluster; Anzahl Sessions; Anzahl Talks in Sessions; Anzahl Talks ohne Sessions; Gesamtanzahl Talks
"""

index = 0
total_sessions = 0
total_sessiontalks = 0
total_plaintalks = 0
total_talks = 0

for topic in cluster_list: 
    total_table_string += '"'+topic+'"; '
    total_table_string += str(cluster_nr_sessions[index])+"; "
    total_table_string += str(cluster_nr_sessiontalks[index])+"; "
    total_table_string += str(cluster_nr_plaintalks[index])+"; "
    total_table_string += str(cluster_nr_plaintalks[index]+cluster_nr_sessiontalks[index])
    total_table_string += r"""
"""
    total_sessions += cluster_nr_sessions[index]
    total_sessiontalks += cluster_nr_sessiontalks[index]
    total_plaintalks += cluster_nr_plaintalks[index]
    total_talks += cluster_nr_sessiontalks[index] + cluster_nr_plaintalks[index]
    index+=1

total_table_string += "TOTAL;"+str(total_sessions)+"; "+str(total_sessiontalks)+"; "+str(total_plaintalks)+"; "+str(total_talks)

print(total_table_string)

fileOverview = open("info-files/"+datestring+"-overview.csv", "w")
fileOverview.write("%s" %total_table_string.encode('utf8'))
fileOverview.close()
