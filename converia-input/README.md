# WIAS Conference Toolkit: Converia

## Input files

A minimal example is provided in this folder. 

### Files exported from Converia

#### paper.xml

Can be downloaded from the Converia data export, and contains most of the data. Nevertheless, some important information is missing. That's why we also use some data exported in extra excel sheets, see below.

#### old_paper.xml

File paper.xml from Converia with the status of submissions from the past, from the submission deadline.
With the help of this file, contributions that were submitted after a deadline can be detected and marked in a special way.
The information is not used to construct the xml data base. It is only used in *export_abstracts.py* to color late contributions in the output pdf-files.

#### EVENT_Personenliste.csv

Can be downloaded as Excel sheet from Converia Management/Person administration/person/Excel export. Save it as csv with utf8 encoding to make it readable for this toolkit.

#### EVENT_Agenda.csv

After creating a Converia schedule, the timetable information can be downloaded as an Excel sheet. Save it as csv with utf8 encoding to make it readable for this toolkit.

### Files that can be added manually

#### EVENT_Registrationlist.csv

A spreadsheet with information of the registration and payment status of the participants.
At ICCOPT 2019, we were deadling with two different companies for abstract submission and conference registration, and it was quite an effort to merge the information from the two sources into one database. The merging is nevertheless helpful, because one can for instance send personalized emails to specific groups of participants, create materials for dinner participants, etc.

#### free_participation.csv

A spreadsheet with a list of people who are eligible for free registration.

Columns are:
Name,Surname,Affiliation,Student,Role,free dinner,notes

*Student* can contain an indication like "Student", "PhD Student", etc.
*Role* can contain the reason for free participation, e.g. "Program Committee", "Grant", etc.
*free dinner* can contain the number of free conference dinner tickets
*notes* can contain a comment, e.g. when the participant has paied a fee and needs to be reimbursed etc.

#### non_participants.csv

people, who are listed in free_participation.csv, but who will not participate in the conference
(e.g., members of a committee who is invited, but told us that they will not make it)

Columns are:
"First Name","Last Name",Email,Affiliation,Role
where *Role* can contain a keyword from the respective column in free_participation.csv

#### BOARD_meeting.csv, OTHERBOARD_meeting.csv

lists of participants of special meetings, e.g. Board meetings.

Columns are:
id, first name, last name (without header line)
*id* is the ID which is used in ../xml/db.xml. We use for instance the Converia ID for participants with Converia account (in EVENT_Personenliste.csv), and otherwise, an ID created in build_xml_db.xml.

#### late_summer_school.csv

In ICCOPT, some students registered for the summer school, but did not indicate this when registering for the conference. That's why the summer school participation was not documented in the spreadsheet we got from the third party service company caring for registrations.
We used this list to include our own participants.

Columns are:
id,"First Name","Last Name",Email (without header line)
*id* is the ID which is used in ../xml/db.xml. We use for instance the Converia ID for participants with Converia account (in EVENT_Personenliste.csv), and otherwise, an ID created in build_xml_db.xml.

#### late_dinner.csv

This list can contain participants of the dinner who did not indicate their participation when registering for the conference.

Columns are:
id,"Last name","First name","Number of tickets" (without header line)
*id* is the ID which is used in ../xml/db.xml. We use for instance the Converia ID for participants with Converia account (in EVENT_Personenliste.csv), and otherwise, an ID created in build_xml_db.xml.

#### summer_school_onsite.csv

Some participant may show up for the summer school at the venue. With the help of this csv file, one can still produce personalized materials, e.g. a letter of participation etc. and also document the participation in the data base.

Columns are:
if,"First name","Last name",Email (without header line)

#### log.csv

Changes in the program can be documented here. When 'canceled' is used in the column 'action', the talk is marked as canceled in the book.

Columns are:
Talk ID, Last name, First name, ID, action, comments
*Talk ID* is the ID which is used in ../xml/db.xml. We use for instance the Converia ID for the talks (in EVENT_Agenda.csv).
*ID* is the ID which is used in ../xml/db.xml. We use for instance the Converia ID for participants with Converia account (in EVENT_Personenliste.csv), and otherwise, an ID created in build_xml_db.xml.

## converia-toolkit: Codes working on the output files of Converia

### build_xml_db

#### Reads

* paper.xml

* EVENT_Agenda.csv

* EVENT_Personenliste.csv

* ../xml/clusters.xml (see ../xml/README.md)

* EVENT_Registrationlist.csv

* free_participation.csv

* non_participants.csv

* late_summer_school.csv

* late_dinner.csv

* summer_school_onsite.csv

* BOARD_meeting.csv, OTHERBOARD_meeting.csv

* log.csv

#### Creates

A database xml/db.xml based on the scheme defined in xml/wias-conference-toolkit.xsd
All information in saved in this file.
See also ../xml/README.md.

### check_duplicates

#### Reads

EVENT_Personenliste.csv

#### Creates

info-files/duplicates-DATE.txt
with similar names in the persons list
This file cay help with deduplication of duplicate accounts in Converia:
First use the built-in functionality in Converia, then export the Excel sheet, save it as csv, and run this code to obtain a list of possible duplicates.
The sensibility can be adjusted in the variable similarity_measure.

### talk_duplicates

#### Reads

paper.xml

#### Creates

text files listing persons who seem to plan two talks in
info-files/duplicate_talks_DATE.txt

### export_overview

Creates spreadsheets with an overview on the numbers of submitted talks etc. 
#### Reads

paper.xml

#### Creates

csv files with an overview on the numer of submitted talks/sessions in clusters etc. in
info-files/DATE-overview.csv
info-files/DATE-sessions.csv
info-files/DATE-talks.csv

### export_abstracts

#### Reads

* paper.xml

* old_paper.xml

#### Creates

* pdf-files with an overview on all talks for each cluster/topic in the subfolder pdf-files/
  contributions in paper.xml, which are not in old_paper.xml (e.g., late submissions) are marked

* the respective tex-files in the subfolder tex-files (to compile by hand, move them to this folder)

* output text with numbers of submitted talks etc.

## Auxiliary files

#### ../wiasct.py

auxiliary functions
right now, it is also copied into other subdirectories of this toolkit.

#### ../correctiontables.py

replacements e.g. for names, institution names, latex syntax.
right now, it is also copied into other subdirectories of this toolkit.

