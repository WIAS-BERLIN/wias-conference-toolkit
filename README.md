# WIAS Conference Toolkit #

*This is an uncomplete preliminary version. We are just about to include all facilities.*

## Overview ##

This toolkit helps to coordinate a conference and to produce printed conference materials. 


## Facilities ##

The facilities provided in this toolkit include the following: 
* Produce a conference book (verbose variant in DIN A4 with abstracts, or short DIN A5 version)
* Create a web app to display the conference program on smartphones
* Write personalized emails by use of mailing scripts in the directory "mail"
* Produce name badges, letters of participation and conference dinner tickets. 

*With the current version, you can already clean Converia data, and build the data base*


## General work flow ##

1. From your submission and registration system, export the data into an xml data base, such that it fits into the scheme defined in xml/wias-conference-toolkit.xml
2. You can now use all other facilities. 

## Work flow with Converia ##

1. Clean your Converia data set. 
   You can use converia-input/check\_duplicates.py to find (more) possible duplicate accounts. 
   Duplicate talks can be detected with the help of converia-input/talk\_duplicates.py
2. If available, include information on the registration/payment status, and more into the according files. 
   See input files in converia-input/README.md
3. Build the data base with the help of converia-input/build\_xml\_db.py
4. You can now use all other facilities. 
