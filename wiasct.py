#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 
# Module with scripts that help to process converia data
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




from collections import OrderedDict
import csv
import difflib
from lxml import etree, objectify
import re
import subprocess
import sys
from time import gmtime, strftime
import unicodedata

import correctiontables as corr

import config.config as config

start2slot = OrderedDict(
             (("05.08.2019 09:30", 'P'),
              ("05.08.2019 11:00", 1),
              ("05.08.2019 13:45", 2),
              ("05.08.2019 15:30", 'SP'),
              ("05.08.2019 16:20", 'BP'),
              ("06.08.2019 09:00", 'P'),
              ("06.08.2019 10:30", 1),
              ("06.08.2019 13:15", 2),
              ("06.08.2019 14:45", 3),
              ("06.08.2019 16:30", 4),
              ("07.08.2019 09:00", 'P'),
              ("07.08.2019 10:15", 'SP1'),
              ("07.08.2019 11:30", 1),
              ("07.08.2019 14:15", 2),
              ("07.08.2019 16:00", 3),
              ("07.08.2019 17:30", 'SP2'),
              ("08.08.2019 09:00", 1),
              ("08.08.2019 10:45", 2),
              ("08.08.2019 13:30", 3),
              ("08.08.2019 15:15", 'SP'),
              ("08.08.2019 16:15", 'P'),
              ))

day2str = {"05.08.2019": "Mon",
           "06.08.2019": "Tue",
           "07.08.2019": "Wed",
           "08.08.2019": "Thu",
          }


room2size = {"H 0104": "644",
             "H 0105": "1192",
             "H 0106": "99",
             "H 0107": "144",
             "H 0110": "193",
             "H 1012": "254",
             "H 1058": "244",
             "H 1029": "70",
             "H 3013": "40",
             "H 3007": "80",
             "H 3006": "100",
             "H 3012": "40",
             "H 3025": "50",
             "H 3008": "30",
             "H 2038": "50",
             "H 3004": "50",
             "H 3002": "40",
             "H 2032": "235",
             "H 0112": "99",
             "H 2035": "28",
             "H 2037": "28",
             "H 2036": "36",
             "H 3005": "48",
             "H 0111": "99",
             "H 1028": "231",
             "H 2013": "260",
             "H 2053": "243",
             "H 2033": "46",
          }

day2num = {'Mon': 5,
           'Tue': 6,
           'Wed': 7,
           'Thu': 8,
           }

sessionslot2num = {'Mon1': 1,
           'Mon2': 2,
           'Tue1': 3,
           'Tue2': 4,
           'Tue3': 5,
           'Tue4': 6,
           'Wed1': 7,
           'Wed2': 8,
           'Wed3': 9,
           'Thu1': 10,
           'Thu2': 11,
           'Thu3': 12,
           }


flag_not_register = False

def similar(seq1, seq2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.9

def compare_names(name, fname, cmp_name, cmp_fname):
    return similar(name+fname, cmp_name+cmp_fname) or similar(name+fname,cmp_fname+cmp_name)

def sessionincluster(session,topic): 
    return (session.find('paper_type').text=='SESSION' and session.find('topiclist').find('topic') is not None and session.find('topiclist').find('topic').find('name').text==topic)

def insessioniccopt(paper,session,presentationform): 
    return (paper.find('paper_type').text=='PAPER' and paper.find('presentationform').text==presentationform and (paper.find('topiclist').find('topic').find('name').text[1:6]==session.get('id') or paper.find('topiclist').find('topic').find('name').text[0:5]==session.get('id')))

def insession(paper,session,presentationform): 
    return (paper.find('paper_type').text=='PAPER' and paper.find('presentationform').text==presentationform and (paper.find('paper_paper_id').text==session.get('id')))

def incluster(paper,topic,presentationform):
    return (paper.find('paper_type').text=='PAPER' and paper.find('presentationform').text==presentationform and paper.find('topiclist').find('topic').find('name').text==topic and paper.find('paper_paper_id').text==None)



#make the mathematic formulas in the abstracts nice
def replace_all(string, replaces):
    for (k, v) in replaces:
        string = string.replace(k, v)
    return string

replacements = tuple((k, replace_all(v, corr.LaTeXShorts)) for (k, v) in corr.math_replacements)

def quote_replace(string):
    new_string = re.sub(r"''([^']*)''", r"``\1''", string) #''Adam-type'' -> ``Adam-type''
    #if string != new_string:
    #    print("==========")
    #    print("QUOT_REPLACE:")
    #    print("<old>", bytes(string, "UTF8"), "</old>")
    #    print("<new>", bytes(new_string, "UTF8"), "</new>")
    #    print("==========")
    return new_string

def dash_replace(string):
    old_string = string
    string = re.sub(r" - ", r" -- ", string)
    string = re.sub(r" – ", r" -- ", string)
    string = re.sub(r"(?<=[^\s])--(?=[^\sA-Z])", r"-", string)
    string = re.sub(r"(?<=[^\s])–(?=[^\sA-Z])", r"-", string)
    string = re.sub(r"Cahn-Hilliard-Navier-Stokes", r"Cahn--Hilliard--Navier--Stokes", string)
    string = re.sub(r"Cahn-Hilliard", r"Cahn--Hilliard", string)
    string = re.sub(r"Navier-Stokes", r"Navier--Stokes", string)
    #if old_string != string:
    #    print("==========")
    #    print("QUOT_REPLACE:")
    #    print("<old>", bytes(old_string, "UTF8"), "</old>")
    #    print("<new>", bytes(string, "UTF8"), "</new>")
    #    print("==========")
    return string
#which one is it?
#parallel optimization and -- time permitting -- multi objective optimization.
#parallel optimization and --time permitting-- multi objective optimization.
#short-term -- usually profit-seeking -- goals
#short-term --usually profit-seeking-- goals
#    –
#    --

def latexify(string):
    string = replace_all(string, replacements)
    string = quote_replace(string)
    string = dash_replace(string)
    return string
##


def person_registration_color(person):
    if flag_not_register and person.find('paiment_status').text=='-1' and len(person.xpath("./role"))==0:
        namestr = r"""\textcolor{notregistered}{"""+person.find('first_name').text+' '+person.find('last_name').text+'}'
    else:
        namestr = person.find('first_name').text+' '+person.find('last_name').text
    return namestr

def person_registration_color_lastname(person):

    # Disable False to fix the colr
    if flag_not_register and person.find('paiment_status').text=='-1' and len(person.xpath("./role"))==0:
        namestr = r"""\textcolor{notregistered}{"""+person.find('last_name').text+'}'
    else:
        namestr = " ".join((person.findtext('first_name'), person.findtext('last_name')))
    return namestr


def late_submissions(root, old_root): 
    old_list=[]
    
    for talk in old_root:
        old_list.append(talk.get('id'))
        
    # collect all talk IDs from paper.xml, which are not in old_list
    late_list = []
    late_string = 'Submitted after Mar 18:\n\n'
    
    for talk in root:
        if talk.find('paper_type').text=='PAPER' and talk.get('id') not in old_list:
            late_list.append(talk.get('id'))
            late_string+=talk.get('id')+'\n'

    return(late_list, late_string)


###### Create list of clusters ######

def cluster_list(root): 
    cluster_list = []
    for topic in root.iter('topic'):
        if topic.find('name').text[0] not in [" ","2","3"]: 
            cluster = topic.find('name').text
            if not cluster in cluster_list: 
                cluster_list.append(cluster)    
    cluster_list.sort()
    return(cluster_list)

def cluster_colors_latex(root):
    tex_text = '% Define cluster colors\n\n'
    for c in root.find("clusters"):
        tex_text += r"""\definecolor{cluster"""+c.find('ID').text+r"""}{HTML}{"""+c.find('color').text[1:]+"}\n"
    return(tex_text)


def cluster_shortcuts_latex(root):
    tex_text = '% List of cluster shortcuts\n\n'
    tex_text += r"""\begin{description}
"""
    for c in root.find("clusters"):
        tex_text += r"""\item[\textcolor{cluster"""+c.find('ID').text+r"""}{"""+c.find('shortcut').text+r"""}] """+c.find('title').text+"\n"
    tex_text += r"""\end{description}
"""
    return(tex_text)

#### create human-readable session-identification-string ####

##!! there is a similar function further below. This one here might be deprecated
def talk_starttime_string(s_sess_id, db_root, time_offset_talks = 0):
    s_sess = db_root.xpath("//schedule_session[ID='{s_sess_id}']".format(s_sess_id=s_sess_id))[0]
    start_time = s_sess.find('timeslot').find('start').text

    multiplyer = 25
    #memorial session would be different offset
    if s_sess.find("ID").text == "10470": #memorial session
        print("ERROR: you never want offset time for memorial session")
        sys.exit(1)
    elif s_sess.find("ID").text == "10461": #Best Paper Session
        multiplyer = 30
    #also best paper session:

    minute_shift = time_offset_talks*multiplyer
    (h_s, m_s) = start_time.split(':')
    shifted_time_in_minutes = 60*int(h_s) + int(m_s) + minute_shift
    (h_n, m_n) = divmod(shifted_time_in_minutes, 60)
    return "{}:{}".format(h_n, str(m_n).zfill(2)) #the new start time


##### name-corrections ####

def first_or_last_name_correction(name):
    corrected_name = name

    if name in corr.manual_corrections.keys():
        corrected_name = corr.manual_corrections[name]

    if name == name.upper() or name == name.lower():
        corrected_name = name.title()

    return corrected_name

def name_correction(id, first, last, apply_change = False, display = True):
    corrected_first = first_or_last_name_correction(first)
    corrected_last = first_or_last_name_correction(last)
    if display and (corrected_first != first) or (corrected_last != last):
        msg = "applying name correction" if apply_change else "SUGGESTING name correction"
        print("{} #{}: {} -> {}".format(msg, id, first+" "+last, corrected_first+" "+corrected_last))
    if apply_change:
        return (corrected_first, corrected_last)
    else:
        return (first, last)

################################
#Corretion of institution names#
################################
#this affects
#python boa_semi_and_plenaries.py
#python boa_best_paper.py
#python export_poster.py
#python boa_create_register.py
#python export_schedule.py

#maybe define a level of correction
#1: ALL-CAPS,
#   longer than 100 characters
#   Umlaute korrigieren
#2: departments streichen
#   groß-, kleinschreibung, Bindestriche
#3: Wikipedia-Eintrag-Name

verbose = True
correction_level = 2

if correction_level >= 2:
    for dp in corr.delete_parts:
        corr.partial_replacement_dict[dp] = ""

def correct_allcaps(inst, verbose = 1):
    exceptions = ["FICO", "WIAS"]
    if inst.upper() == inst and " " in inst and inst not in exceptions:
        if verbose>2:
            print("<??> ", inst)
            print("====")
        inst = inst.title()
    return inst

def correct_department(inst, verbose = 1):
    if "department" in inst.lower():
        if verbose>2:
            print("<??>", inst)
            print("====")
    return inst

def institute_correction(institute, verbose = 1):
    input_institute = institute
    institute = institute.strip()
    if institute in corr.exceptions:
        return institute
    if institute in corr.full_replacement_dict.keys():
        institute = corr.full_replacement_dict[institute]
        if verbose>0:
            print("[xx] {old}\n[->] {new}".format(old=input_institute, new=institute))
            print("====")
        return institute
    replacements = [(k, corr.partial_replacement_dict[k]) for k in corr.partial_replacement_dict.keys() if k in institute]
    for (k, v) in replacements:
        institute = institute.replace(k, v)
        
    if len(institute)>100:
        if verbose>1: print("<XL>", institute, "\n===")
    institute = correct_allcaps(institute, verbose=verbose)
    institute = correct_department(institute, verbose=verbose)
    if institute != input_institute:
        if verbose>0:
            print("[xx] {old}\n[->] {new}".format(old=input_institute, new=institute))
            print("====")
    return institute


def parse_iccopt_db(path):
    """ parse the ICCOPT xml db using objectify API """
    xmlschema_doc = etree.parse(path+"wias-ct.xsd")
    xmlschema = etree.XMLSchema(xmlschema_doc)

    parse = objectify.makeparser(schema=xmlschema)

    with open(path+"db.xml", "r") as f:
        xmltree = objectify.parse(f, parse)

    return xmltree.getroot()


def display_xml(l):
    for el in l:
        print(etree.tostring(el, pretty_print=True, encoding='utf-8').decode('utf-8'))

def sort_participants_tubsorder(p):
    return unicodedata.normalize('NFKD', str(p.findtext("last_name")).split()[0].lower()).encode("ascii", "ignore")

def sort_participants(p):
    last_name = unicodedata.normalize('NFKD', (' '.join(str(p.findtext("last_name")).split())).lower()).encode("ascii", "ignore").decode("ascii")
    first_name = unicodedata.normalize('NFKD', (' '.join(str(p.findtext("first_name")).split())).lower()).encode("ascii", "ignore").decode("ascii")
    return (last_name, first_name)

def get_participants_tubsorder(db_root):
    """ Get the participants, in the same order as in the data given to TUBS """
    return sorted(db_root.xpath("//person[contribution_presenter or paiment_status!=-1 or role][paiment_status!=-5][not(canceled)]"),
            key=sort_participants_tubsorder)

def get_participants(db_root):
    """ Get the sorted list of participants """
    return sorted(db_root.xpath("//person[contribution_presenter or paiment_status!=-1 or role][paiment_status!=-5][not(canceled)]"),
            key=sort_participants)


def get_canceled(db_root):
    """ Get the late cancellation list """
    return sorted(db_root.xpath("//person[canceled]"), key=sort_participants)

def get_canceled_tubsorder(db_root):
    """ Get the late cancellation list, with the TUBS ordering """
    return sorted(db_root.xpath("//person[canceled]"), key=sort_participants_tubsorder)

def sort_persons_tubsorder(plist):
    """ Sort the list of person, using a special sorting """
    return sorted(plist, key=sort_participants_tubsorder)

def sort_persons(plist):
    """ Sort the list of person """
    return sorted(plist, key=sort_participants)

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(root=None)
def find_person(name, db_root=None):

    if db_root is not None:
        find_person.root = db_root
    elif find_person.root is None:
        print("Please definte the db_root optional argument once!")
        return

    db_root = find_person.root

    exact_last_name = db_root.xpath("//person[last_name='{:}']".format(name))
    if exact_last_name:
        return display_xml(exact_last_name)

    start_with_last_name = db_root.xpath("//person[starts-with(last_name,'{:}')]".format(name))
    if start_with_last_name:
        return display_xml(start_with_last_name)


    contains_last_name = db_root.xpath("//person[contains(last_name,'{:}')]".format(name))
    if contains_last_name:
        return display_xml(contains_last_name)

###############################################################
# translate all the roman numbers to the more advanced system #
# of indian numbering                                         #
###############################################################

roman_to_int = {
        "(Part I)": 1,
        "(Part II)": 2,
        "(Part III)": 3,
        "(Part IV)": 4,
        "(Part V)": 5,
        "(Part VI)": 6,
        "(Part VII)": 7,
        "Contributed Session I": 1,
        "Contributed Session II": 2,
        "Contributed Session III": 3,
}


def generate_number_translator(db_root):
    new_name_lookup = {}
    #buid up name-correction dictionary to change (Part IV) to (4/6)
    parallel_sessions = db_root.xpath("./schedule_sessions/schedule_session[paper]")
    ps_w_part = [{"session": s, "title": str(s.title)} for s in sorted(parallel_sessions, key=lambda s: s.title) if "(Part" in str(s.title) or "Contributed Session" in str(s.title)]
    ps_titles = [s["title"] for s in ps_w_part ]
    for ps in ps_w_part:
        if "Part" in ps["title"]:
            first_part = ps["title"].split(" (")[0]
        else:
            first_part = ps["title"].split("Session")[0]
        ps["totalparts"] = len([t for t in ps_titles if first_part in t])
        ps["number"] = 0
        for (k, v) in roman_to_int.items():
            if k in ps["title"]:
                ps["number"] = max(ps["number"], v)
        if "Part" in ps["title"]:
            ps["new_title"] = first_part+" ("+str(ps["number"])+"/"+str(ps["totalparts"])+")"
        elif ps["totalparts"]==1:
            ps["new_title"] = first_part+"Session"
            ps["new_title"] = ps["new_title"].replace(" - Contributed", " -- Contributed")
        else:
            ps["new_title"] = first_part+"Session "+str(ps["number"])+"/"+str(ps["totalparts"])
            ps["new_title"] = ps["new_title"].replace(" - Contributed", " -- Contributed")
        new_name_lookup[ps["session"].ID] = ps["new_title"]
    def indian_numbered_title(ps):
        if ps.ID in new_name_lookup.keys():
            return new_name_lookup[ps.ID]
        else:
            return str(ps.title)
    return indian_numbered_title

#usage:
#indian_numbered_title = generate_number_translator(db_root)
#session_title_in_indian = indian_numbered_title(ps)


#########################
# db lookup convenience #
#########################

def add_minutes(time_str, minutes=25):
    (h_s, m_s) = time_str.split(':')
    shifted_time_in_minutes = 60*int(h_s) + int(m_s) + minutes
    (h_n, m_n) = divmod(shifted_time_in_minutes, 60)
    return "{}:{}".format(h_n, str(m_n).zfill(2)) #the new start time

def get_timespan(schedule_session):
    return '{:}--{:}'.format(schedule_session.timeslot.start,schedule_session.timeslot.end.text)

def get_starttime(talk_node=None, talk_id=None):
    if talk_id is None:
        if hasattr(talk_node, "ID"):
            talk_id = talk_node.ID
        elif hasattr(talk_node, "paperid"):
            talk_id = talk_node.paperid
        else: #for example in sessions
            talk_id = talk_node.paper
    schedule_session = talk_node.xpath("//schedule_session[paper/paperid={}]".format(talk_id))[0]

    multiplyer = 25
    if schedule_session.find("ID").text == "10470": #memorial session
        #print("WARNING: you never want offset time for memorial session") #this was enoying
        multiplyer = 0
        #print("ERROR: you never want offset time for memorial session")
        #sys.exit(1)
    elif schedule_session.find("ID").text == "10461": #Best Paper Session
        multiplyer = 30

    idx = schedule_session.xpath("./paper[paperid={}]".format(talk_id))[0].idx
    session_start_time = schedule_session.timeslot.start
    return add_minutes(str(session_start_time), (idx-1)*multiplyer)

def get_first_and_last_name(person_node):
    return person_node.first_name+" "+person_node.last_name

path_to_id = {
    "schedule_session": {
        "chair": ("./chair", True, "//person"),
        "sessions": ("./session", False, "//session"), #there might be none
        "cluster": ("./cluster", True, "//clusters/cluster"),
        "talks": ("./paper/paperid", False, "//talks/talk"),
    },
    "session": {
        "organisers": ("./organiser", False, "//person"),
        "cluster": ("./cluster", True, "//clusters/cluster"),
        "talks": ("./paper", False, "//talks/talk"),
    },
    "talk": {
        "presenter": ("./presenter", True, "//person"),
        "authors": ("./author", False, "//person"),
    }
}

functions_for_lookup = {
    "schedule_session": {"timespan": get_timespan},
    "talk": {"starttime": get_starttime},
    "person": {"first_last": get_first_and_last_name},
}

def qget(node, *identifiers):
    if type(node) is list:
        rv = [qget(n, *identifiers) for n in node]
        if type(rv[0]) is list: #flatten
            rv = [a in b for b in rv]
        return rv

    if len(identifiers) > 1:
        return qget(qget(node, identifiers[0]), *identifiers[1:])

    identifier = identifiers[0]

    if node.tag in functions_for_lookup.keys() and identifier in functions_for_lookup[node.tag].keys():
        return functions_for_lookup[node.tag][identifier](node)

    if identifier not in path_to_id[node.tag].keys():
        print("identifier {} not found".format(identifier))
        sys.exit(1)
    (attr, singular, query_prefix) = path_to_id[node.tag][identifier]
    if not attr[0:2]=='./':
        sys.exit(1)
    link_ids = node.xpath(attr)
    #if len(link_ids) == 0:
    #    print("no link_ids for query {} in {}".format(attr, node.__dict__))

    query_ans = [node.xpath(query_prefix+"[ID="+str(link_id)+"]")[0] for link_id in link_ids]
    if singular:
        if len(query_ans) == 0:
            print("no elements for query {} for id {}".format(query_prefix, link_ids))
            return []
        return query_ans[0]
    else:
        return query_ans
#def get_fln(node, identifier):
#    return get_property(node, identifier, "first_last")
