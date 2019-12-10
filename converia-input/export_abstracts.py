#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Creates pdf-files with an overview on all talks for each cluster/topic in the subfolder pdf-files/
# 
# Reads   the file paper.xml which can be downloaded from Converia
#         the file old_paper.xml with the status of submission from the past (DATE, e.g. from the submission deadline)
#
# Creates pdf-files with an overview on all talks for each cluster in the subfolder pdf-files/
#         contributions in paper, which are not in old_paper (e.g., late submissions) are marked
#         the respective tex-files in the subfolder tex-files (to compile by hand, move them to this folder)
#         output text with numbers of submitted talks etc.
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
import syspath
syspath.append_parent_path()
import wiasct


datestring = strftime("%Y-%m-%d", gmtime())
infostring = ''

tree = ET.parse('paper.xml')
root = tree.getroot()

old_tree = ET.parse('old_paper.xml')
old_root = old_tree.getroot()

(late_list,late_string) = wiasct.late_submissions(root, old_root)
cluster_list = wiasct.cluster_list(root)

###### Collect information from xml file ######

session_string = ''
talk_counter=0
shortabstract_counter = 0
short_string = 'Short abstracts:'
singletalk_counter=0
poster_counter=0
sessiontalk_counter=0
nocontacts = ''
multiplecontacts = ''
poster_nocontacts = ''
poster_multiplecontacts = ''
sessionposter=''

texfile_header = r"""\documentclass{scrartcl}
\input{tex-files/abstracts_header.tex}
"""
texfile_footer = r"""
\end{document}"""

print(cluster_list)


for topic in cluster_list: 
    cluster_sessiontalk_counter = 0
    cluster_singletalk_counter = 0
    cluster_poster_counter = 0
    cluster_shortabstract_counter = 0
    topicstr = topic.replace(" ","_")
    cluster_sessions_string = ''
    short_string+='\n\n'+topic+'\n\n'
    for session in root:
        if wiasct.sessionincluster(session,topic):
            talk_string = ''
            namesf = ''
            for organizer in session.find('authors'):
                namesf += organizer.find('prename').text+" "+organizer.find('name').text+", "
            names = namesf#.encode('utf8')
            titlef = session.find('paper_title').text#.encode('utf8')
            title = wiasct.latexify(titlef)
            lastname = ''
            if session.find('person_lastname').text is not None:
                lastname=session.find('person_lastname').text
            session_string='\n\n\session{'+session.get('id')+'}{'+lastname+'}{'+names+'}{'+title+'}{'
            for paper in root:
                if wiasct.insession(paper,session,'Poster'): 
                    sessionposter+=paper.get('id')+" ("+topic+")\n"
                elif wiasct.insession(paper,session,'Talk'): 
                    sessiontalk_counter+=1
                    cluster_sessiontalk_counter+=1
                    authors = paper.find('authors')
                    if paper.get('id') in late_list:
                        paper_id = r"""\textcolor{latecolor}{"""+paper.get('id')+r"""}"""
                    else:
                        paper_id = paper.get('id')
                    namesf = ''
                    plainnamesf = ''
                    talk_string='\\talk{'+paper_id+'}'
                    contact_counter=0
                    for author in authors: 
                        if author.find('type').text=='Contact':
                            namesf +=r"""\textcolor{contactcolor}{"""+author.find('prename').text+" "+author.find('name').text+r"""}, """
                            plainnamesf +=author.find('prename').text+" "+author.find('name').text
                            contact_counter+=1
                        elif author.find('type').text=='Presenter':
                            namesf +=r"""\textcolor{presentercolor}{"""+author.find('prename').text+" "+author.find('name').text+r"""}, """
                            plainnamesf +=author.find('prename').text+" "+author.find('name').text
                            contact_counter+=1
                        else:
                            namesf +=r"""\textcolor{coauthorcolor}{"""+author.find('prename').text+" "+author.find('name').text+r"""}, """
                    if contact_counter==0:
                        nocontacts +=paper.get('id')+', '
                    if contact_counter>1:
                        multiplecontacts +=paper.get('id')+', '
                    names = namesf
                    if not paper.find('abstract_content').text:
                        length_abstract=0
                        abstract = ''
                    else:
                        length_abstract = len(paper.find('abstract_content').text)
                        abstract = wiasct.latexify(paper.find('abstract_content').text)
                    if length_abstract<11:
                        cluster_shortabstract_counter+=1
                        short_string+=paper.get('id')+' '+plainnamesf+', '+paper.find('address_email').text+'\n'
                        shortabstract_counter+=1
                        abstract_info = r"""\raisebox{-.25em}{\tikz{\node[fill=shortcolor!20] {"""+str(length_abstract)+r"""}}}"""
                    else:
                        abstract_info = str(length_abstract)
                    titlef = paper.find('paper_title').text
                    title = wiasct.latexify(titlef)
                    talk_string +='{'+names+'}{'+title+'}{'+abstract_info+'}'
                    session_string+='\n'+talk_string
            session_string+='}'
            cluster_sessions_string+=session_string
    cluster_sessions_string+=r"""
\end{description}

\subsection*{Single talks}
"""
    
    singletalksstr = ''
    posterstr = ''
    for paper in root:
        if wiasct.incluster(paper,topic,'Talk'):
            cluster_singletalk_counter+=1
            singletalk_counter+=1
            namesf = ''
            plainnamesf = ''
            if paper.get('id') in late_list:
                paper_id = r"""\textcolor{latecolor}{"""+paper.get('id')+r"""}"""
            else:
                paper_id = paper.get('id')
            talk_string=r"""\singletalk{"""+paper_id+'}'
            contact_counter=0
            for author in paper.find('authors'):
                if author.find('type').text=='Contact':
                    contact_counter+=1
                    namesf +=r"""\textcolor{contactcolor}{"""+author.find('prename').text+" "+author.find('name').text+r"""}, """
                    plainnamesf +=author.find('prename').text+" "+author.find('name').text
                elif author.find('type').text=='Presenter':
                    contact_counter+=1
                    namesf +=r"""\textcolor{presentercolor}{"""+author.find('prename').text+" "+author.find('name').text+r"""}, """
                    plainnamesf +=author.find('prename').text+" "+author.find('name').text
                else:
                    namesf +=r"""\textcolor{coauthorcolor}{"""+author.find('prename').text+" "+author.find('name').text+r"""}, """
            names = namesf
            if contact_counter==0:
                nocontacts +=paper.get('id')+', '
            if contact_counter>1:
                multiplecontacts +=paper.get('id')+', '
            if not paper.find('abstract_content').text:
                length_abstract=0
            else:
                length_abstract = len(paper.find('abstract_content').text)
            if length_abstract<11:
                cluster_shortabstract_counter+=1
                short_string+=paper.get('id')+' '+plainnamesf+', '+paper.find('address_email').text+'\n'
                shortabstract_counter+=1
                abstract_info = r"""\raisebox{-.25em}{\tikz{\node[fill=shortcolor!20] {"""+str(length_abstract)+r"""}}}"""
            else:
                abstract_info = str(length_abstract)
            titlef = paper.find('paper_title').text
            title = wiasct.latexify(titlef)
            talk_string +='{'+names+'}{'+title+'}{'+abstract_info+'}\n\n'
            singletalksstr+=talk_string
        elif wiasct.incluster(paper,topic,'Poster'):
            cluster_poster_counter+=1
            poster_counter+=1
            namesf = ''
            plainnamesf = ''
            if paper.get('id') in late_list:
                paper_id = r"""\textcolor{latecolor}{"""+paper.get('id')+r"""}"""
            else:
                paper_id = paper.get('id')
            poster_string=r"""\poster{"""+paper_id+'}'
            contact_counter=0
            for author in paper.find('authors'): 
                if author.find('type').text=='Contact':
                    contact_counter+=1
                    namesf +=r"""\textcolor{contactcolor}{"""+author.find('prename').text+" "+author.find('name').text+r"""}, """
                    plainnamesf +=author.find('prename').text+" "+author.find('name').text
                elif author.find('type').text=='Presenter':
                    contact_counter+=1
                    namesf +=r"""\textcolor{presentercolor}{"""+author.find('prename').text+" "+author.find('name').text+r"""}, """
                    plainnamesf +=author.find('prename').text+" "+author.find('name').text
                else:
                    namesf +=r"""\textcolor{coauthorcolor}{"""+author.find('prename').text+" "+author.find('name').text+r"""}, """
            names = namesf
            if contact_counter==0:
                poster_nocontacts +=paper.get('id')+', '
            if contact_counter>1:
                poster_multiplecontacts +=paper.get('id')+', '
            if not paper.find('abstract_content').text:
                length_abstract=0
            else:
                length_abstract = len(paper.find('abstract_content').text)
            if length_abstract<11:
                cluster_shortabstract_counter+=1
                shortabstract_counter+=1
                abstract_info = r"""\raisebox{-.25em}{\tikz{\node[fill=shortcolor!20] {"""+str(length_abstract)+r"""}}}"""
            else:
                abstract_info = str(length_abstract)
            titlef = paper.find('paper_title').text
            title = wiasct.latexify(titlef)
            poster_string +='{'+names+'}{'+title+'}{'+abstract_info+'}\n\n'
            posterstr+=poster_string


    overview_string = r"""\subsection*{Overview}
Number of talks in sessions: """+str(cluster_sessiontalk_counter)+r"""\\
Number of single talks: """+str(cluster_singletalk_counter)+r"""\\
Number of posters: """+str(cluster_poster_counter)+r"""\\
Number of short abstracts: """+str(cluster_shortabstract_counter)+r"""\\
"""
    texfilestr = texfile_header+r"""\titleheader{"""+topic+"}{"+datestring+r"""}
"""+overview_string+r"""
\subsection*{Organized Sessions}
\begin{description}
"""+cluster_sessions_string

    if singletalksstr: 
        texfilestr+=r"""\begin{description}
"""+singletalksstr+r"""
\end{description}
"""
    if not posterstr: 
        texfilestr+=texfile_footer
    else: 
        texfilestr+=r"""\subsection*{Posters}
\begin{description}
"""+posterstr+r"""
\end{description}
"""+texfile_footer

    filename = datestring+"_"+topicstr+"_"
    fileSessions = open("tex-files/"+filename+".tex", "w")

    fileSessions.write("%s" %texfilestr)
    fileSessions.close()

    subprocess.check_call(['pdflatex', "tex-files/"+filename+'.tex'])
    subprocess.check_call(['pdflatex', "tex-files/"+filename+'.tex'])
    subprocess.check_call(['mv', filename + '.pdf', 'pdf-files/'])
    subprocess.check_call(['rm', filename + '.aux'])
    subprocess.check_call(['rm', filename + '.log'])
    subprocess.check_call(['rm', filename + '.out'])




outputstring  ='Total number of talks:                      '+str(sessiontalk_counter+singletalk_counter)
outputstring +='\nNumber of posters:                          '+str(poster_counter)
outputstring +='\n\nNumber of talks submitted after DATE:       '+str(len(late_list))
outputstring +='\n\nNumber of talks with short abstracts:       '+str(shortabstract_counter)+' ('+str(100*shortabstract_counter/(sessiontalk_counter+singletalk_counter))+' percent)'
outputstring +='\n\nTalks with more than one presenter/contact author: '+multiplecontacts
outputstring +='\nTalks with less than one presenter/contact author: '+nocontacts

outputstring +='\n\nPosters in sessions:\n'+sessionposter

infofile = open("info-files/submission_overview_"+datestring+".txt", "w")
infofile.write("%s" %outputstring)
infofile.close()

latefile = open("info-files/late_list_"+datestring+".txt", "w")
latefile.write("%s" %late_string)
latefile.close()

shortfile = open("info-files/short_list_"+datestring+".txt", "w")
shortfile.write("%s" %short_string)
shortfile.close()

print('\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%\n{}%%%%%%%%%%%%%%%%%%%%%%%%%%'.format(short_string))

print('\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%\n{}%%%%%%%%%%%%%%%%%%%%%%%%%%'.format(outputstring))
