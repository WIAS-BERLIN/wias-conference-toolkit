#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Proposes a list of possible duplicate accounts from the speadsheet export file of Converia
# 
# Reads   the file EVENT_Personenliste.csv which can be downloaded 
#         as Excel sheet from Converia Management/Person administration/person/Excel export
# Creates info-files/duplicates-DATE.txt with similar names in the persons list
#         This file might be helpful to help with deduplication: 
#         First use the built-in functionality in Converia
#         then export the excel sheet, save it as csv, 
#         and run this code to obtain a list of possible duplicates 
#         The sensibility can be adjusted in the function similar()

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

from time import gmtime, strftime
import subprocess
import csv
import sys
import difflib

__author__ = "Rafael Arndt, Olivier Huber, Caroline Löbhard, Steven-Marian Stengl"
__copyright__ = "Copyright 2019, WIAS"
__license__ = "GPL"
__maintainer__ = "Caroline Löbhard"
__email__ = "oracline@gmail.com"

similarity_measure = 0.85 # number between 0 (coarse similarity) and 1 (strict similarity)

def similar(seq1, seq2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > similarity_measure

def compare_names(name, fname, cmp_name, cmp_fname):
    return similar(name+fname, cmp_name+cmp_fname) or similar(name+fname,cmp_fname+cmp_name)

datestring = strftime("%Y-%m-%d", gmtime())

address_file = 'EVENT_Personenliste.csv'

with open(address_file, 'r') as f:
  reader = csv.reader(f)
  address_array = list(reader)

duplicates = "Possible duplicates with similarity_measure = {}:\n\n".format(similarity_measure)

for index, row in enumerate(address_array):
  name = row[4]
  fname = row[3]
  for cmp_index, cmp_row in enumerate(address_array): 
    if cmp_index>index: 
      cmp_name = address_array[cmp_index][4]
      cmp_fname = address_array[cmp_index][3]
      if compare_names(name,fname,cmp_name,cmp_fname):
        duplicates+="IDs "+str(row[0])+", "+str(address_array[index+1][0])+": "+name+" "+fname+" / "+cmp_name+" "+cmp_fname+"\n"

print(duplicates)

with open("info-files/duplicates-"+datestring+".txt", "w") as f:
  f.write("%s" %duplicates)
