#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Builds a database ../xml/db.xml based on the scheme defined in ../xml/wias-ct.xsd
# 
# Reads   input files as described in README.md
#
# Creates A database ../xml/db.xml based on the scheme defined in ../xml/wias-ct.xsd
#         All information on conference participants and the schedule is saved in this file. 
#         See also ../xml/README.md. 
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


from collections import namedtuple
import csv
from lxml import etree
import os
import re
import sys
import unicodedata
import syspath
syspath.append_parent_path()

import wiasct
from wiasct import start2slot, day2str, room2size

#print(os.path.dirname(os.path.realpath(__file__)))

try:
    import titlecase
except:
    print("Failed to import titlecase. Did you install it (pip install --user titlecase)?")
    sys.exit(1)

if sys.version_info.major < 3:
    print("This scripts requires Python 3")
    sys.exit(1)

try:
    get_ipython()
    from IPython.core import ultratb
    sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=1)
    in_ipython=True
except:
    in_ipython = False

#Configuration
checksummerschool=0
apply_namecorrections=True

person_items = ("ID", "title", "first_name", "last_name", "email", "address",
                "paiment_status", "dinner", "summer_school",
                "contribution_presenter", "contribution_author", "role",
                "amount_paid", "book_of_abstract", "meeting", "canceled")
Author = namedtuple("Author", person_items)

talk_items = ("ID", "title", "abstract", "author", "presenter", "session",
               "order", "type", "canceled")
Talk = namedtuple('Talk', talk_items)

poster_items = ("ID", "title", "abstract", "author", "presenter", "session", "type", "canceled")
Poster = namedtuple('Poster', poster_items)

session_items = ("ID", "cluster", "title", "abstract", "paper", "organiser")
Session = namedtuple('Session', session_items)

Address = namedtuple("Address", ("institution", "street", "zipcode", "city", "state", "country", "countrycode"))

Cluster = namedtuple("Cluster", ("ID", "title", "abstract", "chairs", "color", "shortcut"))


Timeslot = namedtuple("Timeslot", ("day", "slot", "start", "end"))

PaperOrder = namedtuple("PaperOrder", ("paperid", "idx"))

Schedule_Session = namedtuple("Schedule_Session", ("ID", "title", "paper",
    "chair", "timeslot", "room", "session", "cluster"))
author_rosetta_proposed_file = "xml/rosetta-proposed.csv"

rejection_paper = [30754]
rejected_author = [158829]


authors_dup = {"Erika|Mustermann": (("erika@mustermann.de", 141431),
                             ("erikamustermann@testemaildomain.com", 158323))}

cancel_str = "canceled! "

fatal = False

def my_exit():
    if fatal:
        sys.exit(1)

def err_exit():
    print("ERROR: the script encountered a fatal error")
    if in_ipython:
        kaboom()
    sys.exit(1)

def find_converia_paper_by_id(root, idx):
    return root.findall("paper[paper_type='PAPER'][@id='{:}']".format(idx))

def get_cluster(clusters, name):
    try:
        return clusters.index(name) + 1
    except ValueError:
        print("{:} is not a valid cluster name!".format(name))
        print(clusters)
        return -1

def add_dinner(author, value):
    if not author.dinner:
        author.dinner.append(value)
    elif value in author.dinner:
        print("WARNING: for author \n{:}\nduplicate dinner value {:}".format(author, value))
    else:
        author.dinner.append(value)

def add_summer_school(author, value):
    if not author.summer_school:
        author.summer_school.append(value)
    elif author.summer_school[0] != value:
        print("ERROR: for author \n{:}\nformer summer_school value is {:}, now {:}".format(author, author.summer_school[0], value))
        author.summer_school[0] = value
    else:
        print("WARNING: for author \n{:}\nduplicate summer_school value {:}".format(author, value))

def add_book_of_abstract(author):
    if not author.book_of_abstract:
        author.book_of_abstract.append(1)
    elif author.book_of_abstract[0] != 1:
        print("ERROR: for author \n{:}\nformer book_of_abstract value is {:}, now {:}".format(author, author.book_of_abstract[0], 1))
        author.book_of_abstract[0] = 1
    else:
        print("WARNING: for author \n{:}\nduplicate book_of_abstract value {:}".format(author, 1))


# We don't need that right now
#idx_col_TUBS = ("Firma", "Anrede", "Title", "Vorname", "NachName", "Land", "E-Mail"
#                "MOS student or emeritus members, early bird","MOS student or emeritus members, regular",
#                "MOS members, early bird","MOS members, regular","Non MOS members, early bird",
#                "Non MOS members, regular","Students non MOS members, early bird","Students non MOS members, regular",
#                "non-scientific program", "Free registration", "Participation at the Summer School",
#                "Dinner - Waiting List", "printed book of abstracts", "Zahlstatus", "bezahlt gesamt")

tubs_col_names = {"institution": "Firma",
                  "title": "Titel",
                  "first_name": "Vorname",
                  "last_name": "NachName",
                  "email": "E-Mail",
                  0: "MOS student or emeritus members, early bird",
                  1: "MOS student or emeritus members, regular",
                  2: "MOS members, early bird",
                  3: "MOS members, regular",
                  4: "Non MOS members, early bird",
                  5: "Non MOS members, regular",
                  6: "Students non MOS members, early bird",
                  7: "Students non MOS members, regular",
                  "free_registration": "Free registration",
                  "dinner": "non-scientific program",
                  "free_dinner": "Free dinner",
                  "summer_school": "Participation at the Summer School",
                  "waiting_list_dinner": "Dinner - Waiting List",
                  "book_of_abstract": "printed book of abstracts",
                  "paiement_status": "Zahlstatus",
                  "amount_paid": "Gebühr Total",
                  }

def tubs_find_cols(all_names):
    name_idx_dict = {}

    for k, v in tubs_col_names.items():
        lower_name = v.lower()
        for i, c in enumerate(all_names):
            if c.lower() == lower_name:
                name_idx_dict[k] = i
                break

    return name_idx_dict

# Parse the conference schedule
sched_col_names_csv = ("day",
                       "start",
                       "end",
                       "session_id",
                       "session_title",
                       "session_start",
                       "type_of_event",
                       "paper_id",
                       "session_order_index",
                       "room_name",
                       "topic")

#sched_person_id_fmt = "person{:}_person_id"

sched_col_names_xls = ("day",
                       "start",
                       "end",
                       "session id",
                       "session name",
                       "session start",
                       "event type",
                       "paper id",
                       "session order index?",
                       "room name",
                       "session topic")

#sched_person_id_fmt_xls = "person{:}_person_id"
sched_person_email_fmt_xls = "author {:}: email"

def sched_find_cols(all_names):
    name_idx_dict = {}

    for k, kk in zip(sched_col_names_csv, sched_col_names_xls):
        for i, c in enumerate(all_names):
            if c.lower() == k or c.lower() == kk:
                name_idx_dict[k] = i
                break

    pidx = 1
    while True:
#        c_csv = sched_person_id_fmt.format(pidx)
        c_xls = sched_person_email_fmt_xls.format(pidx)
        for i, c in enumerate(all_names):
            if c.lower() == c_xls:
                name_idx_dict[c_xls] = i
                break

        if c_xls in name_idx_dict:
            pidx += 1
        else:
            break

    return (name_idx_dict, pidx)

def _mv_umlaut(s):
    return s.replace(u'ö', u'oe').replace(u'ä', u'ae').replace(u'ü', 'ue')

def _norm(s):
    return unicodedata.normalize('NFKD', s).encode("ascii", "ignore")

def _mv_umlaut_norm(s):
    return _norm(_mv_umlaut(s))

def _find_similar_author(firstname, name, institution, email, authors_noinst, authors, split=False):

    noop = lambda x: x
    if split:
        op = lambda x: x.split()[0]
        op2 = lambda x: x.split()[1]
        sop2 = lambda x: x.split()[-1]
    else:
        op = noop

    all_authors = [k.split('|') for k in authors_noinst.keys()]

    similar_ids = []
    for fn in (noop, _mv_umlaut, _mv_umlaut_norm, _norm):
        similar_ids = [authors_noinst["{:}|{:}".format(k1, k2)] for k1, k2 in
                        all_authors if k1 and fn(op(firstname)) == fn(op(k1)) and fn(name) == fn(k2)]
        if not similar_ids and split and len(firstname.split()) > 1:
            similar_ids = [authors_noinst["{:}|{:}".format(k1, k2)] for k1, k2 in  all_authors if k1 and fn(op2(firstname)) == fn(op(k1)) and fn(name) == fn(k2)]
        if not similar_ids and split:
            similar_ids = [authors_noinst["{:}|{:}".format(k1, k2)] for k1, k2 in  all_authors if k1 and fn(op(firstname)) == fn(sop2(k1)) and fn(name) == fn(k2)]
        if not similar_ids and split and len(name.split()) > 1:
            similar_ids = [authors_noinst["{:}|{:}".format(k1, k2)] for k1, k2 in  all_authors if k1 and fn(firstname) == fn(k1) and fn(op(name)) == fn(k2)]
        if not similar_ids and split and len(name.split()) > 1:
            similar_ids = [authors_noinst["{:}|{:}".format(k1, k2)] for k1, k2 in  all_authors if k1 and fn(firstname) == fn(k1) and fn(op2(name)) == fn(k2)]
        if not similar_ids and split and len(name.split()) > 1:
            similar_ids = [authors_noinst["{:}|{:}".format(k1, k2)] for k1, k2 in  all_authors if k1 and fn(firstname) == fn(k1) and fn(sop2(name)) == fn(k2)]
        if similar_ids:
            break

    # This condition seemed to be true when we have duplicates in the DB
    if len(similar_ids) == 1 and similar_ids[0] is None:
        if email:
            for k, v in authors.items():
                if v.email == email:
                    similar_ids = [k]
                    break

    if len(similar_ids) == 1 and similar_ids[0] is None:
        print("The person ``{:}'' ``{:}'' {:} at {:}".format(firstname, name, email, institution), end=" ")
        print("is likely a duplicate in the database.")

        if email:
            print("No person with that email was found")
        else:
            print("However, without an email we can't find that person")

        err_exit()

    if similar_ids:
        print("Found those names to be similar to ``{:}'' ``{:}'' {:} at {:}:".format(firstname, name, email, institution))
        for aid in similar_ids:
            print(authors[aid])
        print()
        return similar_ids

    similar_ids = [authors_noinst["{:}|{:}".format(k1, k2)] for k1, k2 in
        all_authors if k1 and k2 and wiasct.compare_names(firstname, name, op(k1), k2)]
    if similar_ids:
        print("Found those names to be similar to ``{:}'' ``{:}'' {:} at {:}:".format(firstname, name, email, institution))
        for aid in similar_ids:
            print(authors[aid])
        print()

    # simple check for same email 
    if email:
        for k, v in authors.items():
            if v.email == email:
                similar_ids = [k]
                break

    if similar_ids:
        print("Found those names to be similar to ``{:}'' ``{:}'' {:} at {:}:".format(firstname, name, email, institution))
        for aid in similar_ids:
            print(authors[aid])
        print()

    return similar_ids

def get_authorid(authors_dbs, firstname, name, institution, authors=None, email=None):
    """ Find the author ID based on firstname, name, and institution """
    authors_inst, authors_noinst, author_rosetta, authors_dup = authors_dbs
    a_id = None
    firstname, name = wiasct.name_correction(a_id, firstname, name, apply_namecorrections, True)

    if institution is not None:
        a_id = authors_inst.get("{:}|{:}|{:}".format(firstname, name, institution))

    a_key = "{:}|{:}".format(firstname, name)
    a_key = author_rosetta.get(a_key, a_key)

    if a_key in authors_dup and email:
        for e, a_id in authors_dup[a_key]:
            if e == email:
                return a_id
        print("FATAL ERROR in looking for author duplicate for {:}".format(a_key))
        err_exit()

    if not a_id:
        a_id = authors_noinst.get(a_key)

    if not a_id and authors:

        similar_ids = _find_similar_author(firstname, name, institution, email, authors_noinst, authors)

        if len(similar_ids) == 0:
            # people may not have registered with their fullname with TUBS
            # For instance all the people with middle name in converia, but not
            # TUBS needs to be checked here
            similar_ids = _find_similar_author(firstname, name, institution, email, authors_noinst, authors, True)

        if len(similar_ids) > 1:
            a_id = None
        elif len(similar_ids) == 1:
            a_id = similar_ids[0]
            a = authors[a_id]
            with open(author_rosetta_proposed_file, "a") as f:
                csvwriter = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                if a.address:
                    a_institution = a.address.institution[0]
                else:
                    a_institution = ""
                csvwriter.writerow([a_key, "|".join((a.first_name, a.last_name)), email, a.email, institution, a_institution])

    if not a_id and not authors:
        print("Could not find the following author in the DB:\n")
        print("First name: {:}\nName: {:}\nInstitution: {:}".format(firstname,
             name, institution))
    if a_id and a_id < 0:
        print("Author named {:} {:} is not unique in the DB!".format(firstname, name))
        my_exit()

    return a_id

contrib_author_exceptions = {
        29022: {'Erika|Mustermann': 158323},
        29023: {'Erika|Mustermann': 158323},

        25901: {'Erika|Mustermann': 141431},
}

def contrib_authors(c, authors_db, authors_db_search, c_title, c_id,
        uniq_presenter=True):
    """ Find the authors and presenter for the contribution """
    real_presenter = None
    c_contact = None
    c_authors = []

    for a in c.find('authors').findall('author'):
        c_authors.append(get_authorid(authors_db_search, a.findtext('prename'),
            a.findtext('name'), a.findtext('institution')))
        a_type = a.findtext('type')
        if not c_authors[-1]:
            if c_id in contrib_author_exceptions:
                ID = contrib_author_exceptions[c_id].get("{:}|{:}".format(a.findtext('prename'),a.findtext('name')))
                if not ID:
                    print("No subsitute ID found for author {:} {:} in paper {:}".format(a.findtext('prename'),a.findtext('name'), c_id))
                    err_exit()
                else:
                    c_authors[-1] = ID
            else:
                print("No subsitute ID found for author {:} {:} in paper {:}".format(a.findtext('prename'),a.findtext('name'), c_id))
                err_exit()

        if a_type == "Presenter":
            real_presenter = c_authors[-1]
            ap = authors_db[real_presenter]
            ap.contribution_presenter.append(c_id)
        elif a_type == "Contact" and not real_presenter:
            # Converia likes to screw up, so as of now, there are paper with both a Contact and a Presenter
            # So the strategy is to keep the Presenter, and not the contact

            c_contact =  c_authors[-1]
#            ap = authors_db[c_presenter]
#            # Complain about multiple presentations by the same author
#            if uniq_presenter and len(ap.contribution_presenter) > 0:
#                ap_cp = ap.contribution_presenter
#                talks = [cp for cp in ap_cp if cp in talks_db and talks_db[cp].session != 1]
#                if talks:
#                    print("ERROR: while processing contribution ``{:}'' (ID {:}): "
#                         "{:} is also a presenter for contribution ID: {:}".format(
#                       c_title, c_id, ap, talks))
#                    ap.contribution_presenter.append(c_id)
#            else:
#               ap.contribution_presenter.append(c_id)
        elif a_type == "Author":
            ap = authors_db[c_authors[-1]]
            ap.contribution_author.append(c_id)
        else:
            print("Wrong author type {:} in contribution {:} (ID {:})".format(a_type,
                c_title, c_id))

    if not real_presenter:
        if c_contact:
            real_presenter = c_contact
            authors_db[real_presenter].contribution_presenter.append(c_id)
        else:
            print("ERROR: could not find a presenter for the contribution {:}".format(c_title))
            err_exit()

    return (c_authors, real_presenter)


def find_sessionid(c, sessions_db, clusters, c_title, c_id):
    """ Find the session ID for the contribution """
    topic = c.xpath('topiclist/topic/name/text()')
    if len(topic) > 1:
        print("Talk {:} (ID: {:}) has more than 1 topic: {:}".format(
            c_title, c_id, topic))

    m = re.match(r" ?([0-9]*):? ", topic[0])

    if m:
        c_session = int(m.group(1))
        s = sessions_db[c_session]
        s.paper.append(c_id)
        c_type = 'invited'
    else:
        # XXX delete
        # For now, not all talks are assigned to session
        c_session = get_cluster(clusters, topic[0])
        c_type = 'contributed'
        if c_session < 0:
            print("Talk {:} (ID: {:}) has an invalid session/cluster: {:}".format(
                    c_title, c_id, topic[0]))

    return c_session, c_type

def add_author(authors_db, authors_db_search, new_id, first_name, last_name, email, title="", institution = None, address = None):

    if (institution is None) == (address is None):
        err_exit()

    (first_name, last_name) = wiasct.name_correction(new_id, first_name, last_name, apply_namecorrections, 23)

    if address is None:
        address = Address(institution=[institution], street="", zipcode="", city="", state="", country="", countrycode="")

    authors_db[new_id] = Author(ID=new_id, title=title, first_name=first_name,
        last_name=last_name, email=email, address=address, paiment_status=[-1],
        dinner=[], summer_school=[], contribution_presenter=[],
        contribution_author=[], role=[], amount_paid=[0],
        book_of_abstract=[], meeting=[], canceled=[])

    authors_db_noinst = authors_db_search[1]
    k = "{:}|{:}".format(first_name, last_name)
    if k in authors_db_noinst:
        authors_db_noinst[k] = None
        print("Author {:} already exists in the DB (ID = {:})".format(
                " ".join(author), authors_db_noinst[k]))
    else:
        authors_db_noinst[k] = new_id


####### Start of the program ######
# Remove all temp files
if os.path.isfile(author_rosetta_proposed_file):
    os.unlink(author_rosetta_proposed_file)


sched_person_file = 'EVENT_Agenda.csv'
if "SCHED_FILE" in os.environ:
    sched_person_file = os.environ["SCHED_FILE"]
    print("WARNING: using {:} as SCHED input file".format(sched_person_file))

if not os.path.isfile(sched_person_file):
    print("No file names {:} found! This is needed for the paiment info".format(sched_person_file))
    err_exit()

import codecs
#with codecs.open(sched_person_file, 'rU', 'cp1252') as f:
with open(sched_person_file, 'r',) as f:
    reader = csv.reader(f)
    sched_person_array = list(reader)

sched_name2idx, max_person = sched_find_cols(sched_person_array[0])
schedule_sessions_db = {}

schedule_sessions = []

for row in sched_person_array[1:]:
    vals = dict(((k, row[v]) for k, v in sched_name2idx.items()))
    if vals["type_of_event"] == "PAPERSESSION":
        schedule_sessions.append(int(vals["paper_id"]))

tree = etree.parse('paper.xml')
root = tree.getroot()

# We do not take into account Andrew R. Conn memorial session. Make sure it
# appears somewhere
#predicate_arc_session = "not(starts-with(topiclist/topic/name, ' 30790'))"
#sessions = [s for s in root.xpath("paper[paper_type='SESSION'][not(@id='30790')]") if not int(s.attrib['id'])  in schedule_sessions]
#talks = root.xpath("paper[paper_type='PAPER'][presentationform='Talk'][{:}]".format(predicate_arc_session))
#posters = root.findall("paper[paper_type='PAPER'][presentationform='Poster']")

# Now including the memorial session
sessions = [s for s in root.xpath("paper[paper_type='SESSION']") if not int(s.attrib['id'])  in schedule_sessions]
talks = root.xpath("paper[paper_type='PAPER'][presentationform='Talk']")
posters = root.findall("paper[paper_type='PAPER'][presentationform='Poster']")
# Find all clusters: the test on the name is to eliminate the memorial session
# about Andy Conn --xhub [01.05.19]
#all_clusters = root.xpath("paper[paper_type='SESSION']/topiclist/topic/name[not(starts-with(., ' 30790'))]/text()")
all_clusters = root.xpath("paper[paper_type='SESSION']/topiclist/topic/name[not(starts-with(., ' '))][not(starts-with(., '2'))][not(starts-with(., '3'))]/text()")
clusters = sorted(set(all_clusters))
#print(clusters)

clusters_tree = etree.parse('../xml/clusters.xml')
clusters_root = clusters_tree.getroot()

clusters = clusters_root.xpath("//cluster/title/text()")
#if not all((c for c in clusters if c.isalpha())):
#    print("Bad ``topic'' in cluster list:")
#    print(cluster)
#    err_exit()

clusters_db = {}
for c in clusters_root.xpath("//cluster"):
    idx = int(c.find("ID").text)
    clusters_db[idx] = Cluster(idx, title=c.find('title').text, abstract=c.find('abstract').text, chairs=[], color=c.find('color').text, shortcut=c.find('shortcut').text)


# Build authors DB
author_file = 'EVENT_Personenliste.csv'
author_rosetta = 'xml/rosetta-author.csv'

authors_rosetta = {}

with open(author_file, 'r') as f:
    reader = csv.reader(f)
    author_array = list(reader)

if os.path.isfile(author_rosetta):
    with open(author_rosetta, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            authors_rosetta[row[0]] = row[1]


authors_db_inst = {}
authors_db_noinst = {}
authors_db_search = (authors_db_inst, authors_db_noinst, authors_rosetta, authors_dup)
authors_db = {}
# authors items are ID, title, first_name, last_name, email, address,
#                paiment_status, contribution_presenter, contribution_author)
for author in author_array[1:]:
    a_id = int(author[0])
    if a_id in rejected_author:
        continue
    title = author[2]
    first_name = author[3]
    last_name = author[4]
    email = author[6]

    institution = author[14]

    address = Address(institution=[institution], street=author[7],
                      zipcode=author[8], city=author[9],
                      state=author[10], country=author[12], countrycode=author[11])

    add_author(authors_db, authors_db_search, a_id, first_name, last_name, email, address = address, title=title)

    #these lines could be moved into add_author
    k_inst = "{:}|{:}|{:}".format(authors_db[a_id].first_name,
                                  authors_db[a_id].last_name,
                                  institution)
    if k_inst in authors_db_inst:
        print("Author {:} already exists in the DB (ID = {:})".format(
                " ".join(author), authors_db_inst[k_inst]))
    authors_db_inst[k_inst] = a_id


# Build authors DB
tubs_person_file = 'EVENT_Registrationlist.csv'
if "TUBS_FILE" in os.environ:
    tubs_person_file = os.environ["TUBS_FILE"]
    print("WARNING: using {:} as TUBS input file".format(tubs_person_file))

if not os.path.isfile(tubs_person_file):
    print("No file names {:} found! This is needed for the paiment info".format(tubs_person_file))
    err_exit()

with open(tubs_person_file, 'r') as f:
    reader = csv.reader(f)
    tubs_person_array = list(reader)

new_id_base = 1000000
new_id = new_id_base
tubs_name2idx = {}


for tubs_person in tubs_person_array:
    # This signals the end of the list
    if tubs_person[0] == 'Ergebnis':
        if not tubs_name2idx:
            print("Malformed TUBS file, could not find starting columns")
            err_exit()

        break

    # Find the index of the columns we are interested in
    if not tubs_name2idx:
        if tubs_person[0] == "Firma":
            tubs_name2idx = tubs_find_cols(tubs_person)
            if not tubs_name2idx:
                print("Malformed TUBS file, could not find extract starting column")
                err_exit()
            continue
        else:
            continue



    first_name = tubs_person[tubs_name2idx["first_name"]].title()
    last_name = tubs_person[tubs_name2idx["last_name"]].title()
    if "email" in tubs_name2idx:
        email = tubs_person[tubs_name2idx["email"]]
    else:
        email = None  # This is consistent with get_authorid

    if email == "tensorial@gmail.com":
        print("SKIPPING TEST PERSON")
        continue

    institution = tubs_person[tubs_name2idx["institution"]]
    amount_paid = float(tubs_person[tubs_name2idx["amount_paid"]].split()[0].replace(',',''))

    # Exclude sponsors
    if not last_name:
        continue

    a_id = get_authorid(authors_db_search, first_name, last_name,
                        institution, authors_db, email)

    if not a_id:
        print("\nNo author id found for {:} {:} at {:}: create new author with id {:}\n".format(
            first_name, last_name, institution, new_id))
        title =  tubs_person[tubs_name2idx["title"]]
        add_author(authors_db, authors_db_search, new_id, first_name, last_name, email, institution=institution, title=title)
        a_id = new_id
        new_id += 1
    else: # Maybe there is no institution in converia, but in TUBS, so copy that info
        if not authors_db[a_id].address.institution[0] and institution:
            authors_db[a_id].address.institution[0] = institution

    authors_db[a_id].amount_paid[0] += amount_paid

    tubs_paiement_status = tubs_person[tubs_name2idx["paiement_status"]]
    if tubs_paiement_status == "bezahlt":
        if tubs_person[tubs_name2idx["dinner"]] == "1":
            # That is a good citizen
            if amount_paid in (515.0, 430.0):
                add_dinner(authors_db[a_id], 2)
            else:
                add_dinner(authors_db[a_id], 1)

        elif tubs_person[tubs_name2idx["dinner"]] == "2":
            # Also a good citizen
            add_dinner(authors_db[a_id], 2)
        elif tubs_person[tubs_name2idx["waiting_list_dinner"]] == "1":
            # Paid and is on the waiting list
            add_dinner(authors_db[a_id], -1)

        if tubs_person[tubs_name2idx["summer_school"]] == "1":
            add_summer_school(authors_db[a_id], 1)

        paiment_status = -1
        for i in range(0, 8):
            v = tubs_person[tubs_name2idx[i]]
            if v == '1':
                if paiment_status == -1:
                    paiment_status = i
                else:
                    print("Buggy paiment for author ID {:} {:} {:} at {:}".format(a_id, 
                        first_name, last_name, institution))
                    print("Want to insert {:}, but we already have {:}".format(v, 
                                paiment_status))

        if paiment_status == -1 and tubs_person[tubs_name2idx["free_registration"]] == "1":
            paiment_status = 8

        authors_db[a_id].paiment_status[0] = paiment_status

    elif tubs_paiement_status == "kostenfrei":
        authors_db[a_id].paiment_status[0] = 8
        if tubs_person[tubs_name2idx["summer_school"]] == "1":
            add_summer_school(authors_db[a_id], 1)
        if tubs_person[tubs_name2idx["dinner"]] == "1":
            add_dinner(authors_db[a_id], 1)
    else: #tubs_paiement_status == "offen"
        if tubs_person[tubs_name2idx["dinner"]] == "1":
            add_dinner(authors_db[a_id], 0)
        elif tubs_person[tubs_name2idx["waiting_list_dinner"]] == "1":
            add_dinner(authors_db[a_id], -2)


        if tubs_person[tubs_name2idx["free_registration"]] == "1":
            if float(tubs_person[tubs_name2idx["amount_paid"]].split()[0].replace(',','')) == 0:
                # People with a free registration, didn't order anything else, but not validated by TUBS
                authors_db[a_id].paiment_status[0] = -3
            else:
                # People with a free registration, but didn't pay everything (like dinner?)
                authors_db[a_id].paiment_status[0] = -4
            # summer school participant, didn't pay
            if tubs_person[tubs_name2idx["summer_school"]] == "1":
                add_summer_school(authors_db[a_id], -1)
        else:
            # Registered, but didn't pay (everything?)
            authors_db[a_id].paiment_status[0] = -2
            # summer school participant, didn't pay
            if tubs_person[tubs_name2idx["summer_school"]] == "1":
                add_summer_school(authors_db[a_id], 0)

    if "book_of_abstract" in tubs_name2idx:
        boa = tubs_person[tubs_name2idx["book_of_abstract"]]
        if boa in ("I would like to have a printed book.", "yes"):
            add_book_of_abstract(authors_db[a_id])
        elif boa in ("I would NOT like to have a printed book.", ""):
            pass
            # This is just a quality check
        else:
            print("ERROR: unknown value in book of abstract column {:}:".format(tubs_name2idx["book_of_abstract"]))
            print("``{:}''".format(boa))


    if tubs_person[tubs_name2idx["free_dinner"]] == "1":
        add_dinner(authors_db[a_id], 3)

free_person_file = 'free_participation.csv'
if not os.path.isfile(free_person_file):
    print("No file names {:} found! This is needed for the paiment info".format(free_person_file))
    err_exit()

with open(free_person_file, 'r') as f:
    reader = csv.reader(f)
    free_person_array = list(reader)


new_id = 2 * new_id_base
for free_person in free_person_array[4:]:
    # This signals the end of the list
    if free_person == 'Ergebnis':
        break

    first_name = free_person[0]
    last_name = free_person[1]
    institution = free_person[2]
    role = free_person[4].split('/')
    free_dinner = free_person[5]

    a_id = get_authorid(authors_db_search, first_name, last_name, institution, authors_db)

    if not a_id:
        print("\nNo author id found for {:} {:} at {:}: create new author with id {:}\n".format(
            first_name, last_name, institution, new_id))
        add_author(authors_db, authors_db_search, new_id, first_name, last_name, "", institution=institution)
        a_id = new_id
        new_id += 1

    for r in role:
        authors_db[a_id].role.append(r)

    if free_dinner == "1":
        if not authors_db[a_id].dinner:
            print("FREE DINNER DEBUG: {:} has no free dinner in TUBS".format(last_name))
            add_dinner(authors_db[a_id], 3)
    elif authors_db[a_id].dinner and authors_db[a_id].dinner[0] == 3 and (not free_dinner or free_dinner == "0"):
        print("FREE DINNER DEBUG: {:} has no free dinner in free_participation.csv, but has one in TUBS".format(last_name))

non_participants_file = 'non_participants.csv'
if not os.path.isfile(non_participants_file):
    print("No file names {:} found!".format(non_participants_file))
    err_exit()

with open(non_participants_file, 'r') as f:
    reader = csv.reader(f)
    non_participants_array = list(reader)


for non_participants in non_participants_array[1:]:
    # First Name,Last Name,Email,Affiliation,Role
    first_name = non_participants[0]
    last_name = non_participants[1]
    email = non_participants[2]
    institution = non_participants[3]
    role = non_participants[4].split('/')

    a_id = get_authorid(authors_db_search, first_name, last_name, institution, authors_db)

    if not a_id:
        print("\nNo author id found for {:} {:} at {:}: create new author with id {:}\n".format(
            first_name, last_name, institution, new_id))
        add_author(authors_db, authors_db_search, new_id, first_name, last_name, email, institution=institution)
        a_id = new_id
        new_id += 1

    for r in role:
        authors_db[a_id].role.append(r)

    authors_db[a_id].paiment_status[0] = -5


new_id = 3 * new_id_base
late_summer_school_reg = 'late_summer_school.csv'
if not os.path.isfile(late_summer_school_reg):
    print("No file names {:} found!".format(late_summer_school_reg))
    err_exit()

with open(late_summer_school_reg, 'r') as f:
    reader = csv.reader(f)
    late_summer_school_array = list(reader)

for late_summer_school_p in late_summer_school_array:
    id_, fname, name, email = late_summer_school_p

    if not id_:
        id_ = get_authorid(authors_db_search, fname, name, "", authors_db, email = email)
    if not id_:
         print("\nNo author id found for {:} {:} at {:}: create new author with id {:}\n".format(fname, name, email, new_id))
         add_author(authors_db, authors_db_search, new_id, fname, name, email, institution="")
         id_ = new_id
         new_id += 1
         authors_db[id_].paiment_status[0] = 8

    add_summer_school(authors_db[int(id_)], 1)

late_dinner_reg = 'late_dinner.csv'
if not os.path.isfile(late_dinner_reg):
    print("No file names {:} found!".format(late_dinner_reg))
    err_exit()

with open(late_dinner_reg, 'r') as f:
    reader = csv.reader(f)
    late_dinner_array = list(reader)

for late_dinner_p in late_dinner_array:
    id_, fname, name, nb = late_dinner_p

    if not id_:
        id_ = get_authorid(authors_db_search, fname, name, "", authors_db)
    if not id_:
         print("\nNo author id found for {:} {:} at {:}: create new author with id {:}\n".format(fname, name, "", new_id))
         add_author(authors_db, authors_db_search, new_id, fname, name, "", institution="")
         id_ = new_id
         new_id += 1
         authors_db[int(id_)].paiment_status[0] = 8

    a_id = int(id_)
    add_dinner(authors_db[a_id], nb)

new_id = 4 * new_id_base
summer_school_onsite = 'summer_school_onsite.csv'
if not os.path.isfile(summer_school_onsite):
    print("No file names {:} found!".format(summer_school_onsite))
    err_exit()

with open(summer_school_onsite, 'r') as f:
    reader = csv.reader(f)
    late_summer_school_array = list(reader)

for late_summer_school_p in late_summer_school_array:
    id_, fname, name, email = late_summer_school_p

    if not id_:
        id_ = get_authorid(authors_db_search, fname, name, "", authors_db)
    if not id_:
         print("\nNo author id found for {:} {:} at {:}: create new author with id {:}\n".format(fname, name, email, new_id))
         add_author(authors_db, authors_db_search, new_id, fname, name, email, institution="")
         id_ = new_id
         new_id += 1
         authors_db[id_].paiment_status[0] = -1

    add_summer_school(authors_db[int(id_)], 2)

sessions_db = {}
# session_items are: ID, cluster, title, abstract, paper, chair,
#                     organiser, timeslot

for s in sessions:
    s_id = int(s.get('id'))
    s_title = s.findtext('paper_title')
    s_abstract = s.findtext('abstract_content')

    topic = s.xpath('topiclist/topic/name/text()')
    if len(topic) > 1:
        print("Session {:} (ID: {:}) has more than 1 topic: {:}".format(
            s_title, s_id, topic))
    # If no topic, may be a schedule thing
    elif not topic:
        print("Session {:} (ID: {:}) has no topic".format(s_title, s_id))
        continue

    s_cluster = get_cluster(clusters, topic[0])
    if s_cluster < 0:
        print("Session {:} (ID: {:}) has an invalid cluster: {:}".format(
                s_title, s_id, topic[0]))


    s_organizer = []
    for org in s.find('authors').findall('author'):
        s_organizer.append(get_authorid(authors_db_search, org.findtext('prename'),
            org.findtext('name'), org.findtext('institution')))

    session_data = (s_id, s_cluster, s_title, s_abstract, [], s_organizer)
    sessions_db[s_id] = Session(*session_data)

talks_db = {}
# paper items are: ID, title, abstract, author, presenter, session,
#               order, type)

for t in talks:
    t_id = int(t.get('id'))
    if t_id in rejection_paper:
        continue
    t_title = t.findtext('paper_title')
    t_abstract = t.findtext('abstract_content')
    order = t.findtext('paper_order_index')
    t_order = None
    if order:
        t_order = int(order[0])

    topic = t.xpath('topiclist/topic/name/text()')
    if len(topic) > 1:
        print("Talk {:} (ID: {:}) has more than 1 topic: {:}".format(
            t_title, t_id, topic))

    t_session, t_type = find_sessionid(t, sessions_db, clusters, t_title, t_id)
    t_authors, t_presenter = contrib_authors(t, authors_db, authors_db_search, t_title, t_id, t_session != 30790)

    if t_presenter < 0:
        print("No presenter for talk ``{:}'' (ID {:}) in session ``{:}''".format(
                t_title, t_id, t_session))

    is_canceled = None
    if t_title.startswith(cancel_str):
        is_canceled = True
        t_title = t_title.replace(cancel_str, "")

    talk_data = (t_id, t_title, t_abstract, t_authors, t_presenter, t_session,
            t_order, "{:}_talk".format(t_type), is_canceled)
    talks_db[t_id] = Talk(*talk_data)

posters_db = {}
for p in posters:
    p_id = int(p.get('id'))
    if p_id in rejection_paper:
        continue
    p_title = p.findtext('paper_title')
    p_abstract = p.findtext('abstract_content')

    p_session, _ = find_sessionid(p, sessions_db, clusters, p_title, p_id)
    p_authors, p_presenter = contrib_authors(p, authors_db, authors_db_search,
            p_title, p_id, False)

    if p_presenter < 0:
        print("No presenter for poster ``{:}'' (ID {:}) in session ``{:}''".format(
                p_title, p_id, p_session))

    is_canceled = None
    if p_title.startswith(cancel_str):
        is_canceled = True
        p_title = p_title.replace(cancel_str, "")

    poster_data = (p_id, p_title, p_abstract, p_authors, p_presenter,
            p_session, "poster", is_canceled)
    posters_db[p_id] = Poster(*poster_data)


if checksummerschool:
    additional_summer_school_registration = 'summer_school_registrations_manual.csv'
    
    with open(additional_summer_school_registration, 'r') as f:
        reader = csv.reader(f)
        author_array = list(reader)
        assert(author_array[0] == ['ID','registered','first_name','last_name'])
        for sschoolreg in author_array[1:]:
            a_id = int(sschoolreg[0])
            a = authors_db[a_id]
            assert(a.first_name == sschoolreg[2])
            assert(a.last_name == sschoolreg[3])
            if a.summer_school != []:
                print("WARNING: SUMMER_SCHOOL: already entry for {:} {:}".format(a.first_name, a.last_name))
                if sschoolreg[1] == '1':
                    add_summer_school(authors_db[a_id], 2)


# add meeting informations
meeting_files = ("BOARD_meeting.csv", "OTHERBOARD_meeting.csv")
for m in meeting_files:
    with open(m, "r") as f:
        reader = csv.reader(f)
        part_array = list(reader)
        for row in part_array:
            author = authors_db[int(row[0])]
            author.meeting.append(m.split('_')[0])

# Late changes
with open('log.csv', 'r') as f:
    reader = csv.reader(f, skipinitialspace=True)
    late_changes_array = list(reader)


for change in late_changes_array[1:]:
    c_id, name, fname, p_id, action = change[:5]

    if action != "canceled":
        print("INFO: action ``{:}'' is not supported yet".format(action))
        continue
    if not name:
        print("INFO: no action for row {:}".format(change))
        continue

    p_id = int(p_id)
    if c_id:
        c_id = int(c_id)
    else:
        c_id = -1

    key = "{:}|{:}".format(fname, name)
    if p_id < new_id_base:
        authors_db[p_id].canceled.append(True)
    elif key in authors_db_noinst:  # Detects people with no converia account, who just registered with TUBS --xhub
        valid_id = authors_db_noinst[key]
        authors_db[valid_id].canceled.append(True)
    else:
        print("ERROR: Could not find {fname} {name} in the TUBS list".format(fname=fname, name=name))


    if (c_id in talks_db and not talks_db[c_id].canceled) or (c_id in posters_db and not posters_db[c_id].canceled):
        print("Contribution {:} is not marked as canceled".format(c_id))

# Serialize
xmlschema_doc = etree.parse("../xml/wias-ct.xsd")
xmlschema = etree.XMLSchema(xmlschema_doc)

def serialize_simple(p_xml, name, obj):
    if not obj:
        return
    child_xml = etree.SubElement(p_xml, name)

    for k, v in obj._asdict().items():
        if k in xml_methods:
            xml_methods[k](child_xml, k, v)
        else:
            # This is the detection of namedtuple
            if issubclass(type(v), tuple):
                serialize_simple(child_xml, k, v)
            elif isinstance(v, list):
                for e in v:
                    if issubclass(type(e), tuple):
                        serialize_simple(child_xml, k, e)
                    else:
                        k_xml = etree.SubElement(child_xml, k)
                        k_xml.text = str(e)
            elif isinstance(v, str) or v:
                k_xml = etree.SubElement(child_xml, k)
                k_xml.text = str(v)

xml_methods = {'address': serialize_simple}

db_root = etree.Element('wiasct_conference')
db_xml = etree.ElementTree(db_root)

participants_xml = etree.SubElement(db_root, "participants")
for a in authors_db.values():
    serialize_simple(participants_xml, "person", a)

talks_xml = etree.SubElement(db_root, "talks")
for t in talks_db.values():
    serialize_simple(talks_xml, "talk", t)

posters_xml = etree.SubElement(db_root, "posters")
for p in posters_db.values():
    serialize_simple(posters_xml, "poster", p)

sessions_xml = etree.SubElement(db_root, "sessions")
for s in sessions_db.values():
    serialize_simple(sessions_xml, "session", s)
s
clusters_xml = etree.SubElement(db_root, "clusters")
for c in clusters_db.values():
    serialize_simple(clusters_xml, "cluster", c)

s_session_title_regexp = re.compile(r"(.*)(\(Part .*\))")
s_session_part_regexp = re.compile(r".*Part ([^)]*).*")

s_session_in_parts = {}
s_session_no_part = {}
roman2arab = {'I':    1,
              'II':   2,
              'III':  3,
              'IV':   4,
              'V':    5,
             }

fix_H_1058 = {"H 1058 ": "H 1058"}

ignore_sched_session = (11099,)

for row in sched_person_array[1:]:
    vals = dict(((k, row[v]) for k, v in sched_name2idx.items()))
    sid = int(vals["session_id"])
    if sid in ignore_sched_session:
        continue
    if vals["type_of_event"] == "PAPERSESSION":
        s_start = vals["session_start"]
        if s_start not in start2slot:
            print("\nERROR: for session {:}, unknown starting time {:}\n".format(sid, s_start))
            continue
        timeslot = Timeslot(start=vals["start"], end=vals["end"],
                   day=day2str[vals["day"]], slot=start2slot[s_start])
        room = vals["room_name"]
        room = fix_H_1058.get(room, room)
        if not room:
            print("ERROR: session {:} has no room".format(sid))
            room = None
        chairs = []
        for i in range(max_person):
            email = vals.get(sched_person_email_fmt_xls.format(i+1), None)
            if email:
                res = participants_xml.xpath("./person[email='{:}']/ID/text()".format(email))
                if not res:
                    print("ERROR in parsing the schedule: chair with email {:} for sessions {:} is not in the author db".format(email, sid))

                elif len(res) > 1:
                    print("ERROR in parsing the schedule: chair with email {:} has multiple entries: ".format(email))
                    for r in res:
                        print("\t{:}".format(r))

                else:
                    chairs.append(res[0])
            else:
                break

        s_title = titlecase.titlecase(vals["session_title"])

        s_cluster = get_cluster(clusters, vals["topic"])
        if s_cluster < 0:
            print("Session {:} (ID: {:}) has an invalid cluster: {:}".format(s_title, sid, vals["topic"]))


        m = s_session_title_regexp.match(s_title)
        if m:
            title = m.group(1)
            part = m.group(2)
            if title[-1] != ' ':
                print("ERROR: schedule session {:} with name ``{:}''".format(sid, s_title), end =' ')
                print("There is no space between the title and the Part information")

            mm = s_session_part_regexp.match(part)
            if not mm:
                print("ERROR: schedule session ``{:}'' with name {:}".format(sid, s_title), end =' ')
                print("Could not parse the part information ``{:}''".format(part))

            else:
                sched_session_order = roman2arab.get(mm.group(1), None)

                if sched_session_order:
                    if title not in s_session_in_parts:
                        s_session_in_parts[title] = []

                    s_session_in_parts[title].append(((sched_session_order,
                                                       sid), (timeslot.day, timeslot.slot, room)))

        else:
            st_id = s_session_no_part.get(s_title, None)
            if st_id:
                s_session_no_part[s_title].append(sid)
            else:
                s_session_no_part[s_title] = [sid]


        schedule_sessions_db[sid] = Schedule_Session(ID=sid,
            title=s_title, paper=[], chair=chairs,
            timeslot=timeslot, room=room,
            cluster=[s_cluster], session=[])

    elif vals["type_of_event"] == "PAPEREVENT":
        order = int(vals["session_order_index"])
        sid = int(vals["session_id"])
        pid = vals["paper_id"]
        if sid not in schedule_sessions_db:
            print("ERROR: schedule session {:} does not exists for paper {:}".format(sid, pid))
            continue

        if order < 1:
            print("ERROR: paper order is {:}".format(order))

        po = PaperOrder(paperid=pid, idx=order)
        schedule_sessions_db[sid].paper.append(po)

for v in schedule_sessions_db.values():
    sess = []
    clusters = {}
    for p in v.paper:
        p_id = int(p.paperid)
        s = talks_db[p_id].session
        if s > 100:
            sess.append(s)
            c = sessions_db[s].cluster
        else:
            c = s

        if c not in clusters:
            clusters[c] = [p_id]
        else:
            clusters[c].append(p_id)

    # Assign the cluster
    if not clusters:
         print("\nERROR: Could not assign cluster for session {:} named ``{:}''".format(v.ID, v.title))
    elif len(clusters) == 1:
        k = list(clusters.keys())[0]
        if k != v.cluster[0]:
            print("\nERROR: different cluster for session {:} named ``{:}''".format( v.ID, v.title))
            print("Agenda has {:}, papers have {:}".format(v.cluster[0], k))
    else:
        print("\nERROR: different cluster (named for session {:} named ``{:}''".format( v.ID, v.title))
        print("Agenda has {:}".format(v.cluster[0]))
        nb_paper = 0
        for c, p in clusters.items():
            print("Cluster {:} for papers {:}".format(c, p))

    v.session.extend(set(sess))

schedule_sessions_xml = etree.SubElement(db_root, "schedule_sessions")
for s in schedule_sessions_db.values():
    serialize_simple(schedule_sessions_xml, "schedule_session", s)

# Reduce verbosity
#print("Schedule sessions with similar names")
#for k, v in s_session_no_part.items():
#    if len(v) > 1:
#        print("{:}: ID = {:}".format(k, v))
#
#print("Schedule sessions with parts")
#for k, v in s_session_in_parts.items():
#    print("Main title: {:}".format(k))
#    for e in v:
#        print("\t\tPart {:}, ID {:}: \t{:} @ slot {:} in room {:}".format(e[0][0], e[0][1], e[1][0], e[1][1], e[1][2]))
#    print()

xmlschema.assertValid(db_root)

with open("../xml/db.xml", "wb") as f:
    f.write(etree.tostring(db_root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
