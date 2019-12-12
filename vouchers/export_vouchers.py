#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Produces vouchers, e.g. for participants of restricted meetings based on the data given in the database ../xml/db.xml
# 
# Reads   ../xml/db.xml
#
# Creates The tex-file vouchers-BOARD.tex, which can be compiled with Latex to produce a pdf with all vouchers.
#         The vouchers from this template can be printed on Sigel LP798 Business Cards. 
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

from lxml import etree
from lxml import objectify

import syspath
syspath.append_parent_path()
import wiasct

db_tree = etree.parse('../xml/db.xml')
db_root = db_tree.getroot()

tex_file_head = r"""
\documentclass[]{scrartcl}

\usepackage{tikz}
\usepackage{geometry}
\usepackage[utf8]{inputenc}
\usepackage{multicol}

\setlength{\columnsep}{10mm}

\geometry{left=15mm,
right=15mm,
top=10mm,
bottom=10mm,
}

\tikzset{
    innerbox/.style={
      line width = 5pt,
      rounded corners,
      text width=72mm,
      minimum height=42mm,
      text centered,
      inner sep=0pt,
      outer sep=0pt,
    },
    outerbox/.style={draw=gray,
      rounded corners,
      inner sep=15pt,
      outer sep=0pt,
    },
}

\definecolor{logogreen}{RGB}{162,173,6}
\definecolor{gruen}{RGB}{142,153,6}
\definecolor{logoorange}{RGB}{222,113,35}

\parindent0pt

\renewcommand{\familydefault}{\sfdefault}
\fboxsep=-\fboxrule

\newcommand{\voucher}[5]{\begin{tikzpicture}
    \clip (-42.5mm,-27.5mm) rectangle (42.5mm,27.5mm);
%    \fill[black!10] (-42.5mm,-27.5mm) rectangle (42.5mm,27.5mm);
%    \clip (0,0) rectangle (85mm,55mm);
    \node[innerbox,draw=#5] at (0,0) {\textbf{\textcolor{#5}{{\Large #1}\\[.5em]#2\\#3\\[1em]{\Large #4}}}};
\end{tikzpicture}
}

\begin{document}

\begin{multicols}{2}
"""

tex_file_foot="""
\end{multicols}
\end{document}"""

tex_file = tex_file_head

for person in wiasct.sort_persons(db_root.xpath("//person[meeting='BOARD']")):
    tex_file += "\\voucher{{BOARD Meeting}}{{Tuesday, August 6, 12:00}}{{H~3005}}{{{name}}}{{gruen}}\n".format(name=" ".join([person.findtext('first_name'),person.findtext('last_name')]))

tex_file += tex_file_foot

with open("vouchers-BOARD.tex", "w") as f:
    f.write(tex_file)

tex_file = tex_file_head

for person in wiasct.sort_persons(db_root.xpath("//person[meeting='OTHERBOARD']")):
    tex_file += "\\voucher{{OTHERBOARD Meeting}}{{Wednesday, August 7, 13:00}}{{H~3005}}{{{name}}}{{logoorange}}\n".format(name=" ".join([person.findtext('first_name'),person.findtext('last_name')]))

tex_file += tex_file_foot

print(tex_file)

with open("vouchers-OTHERBOARD.tex", "w") as f:
    f.write(tex_file)
