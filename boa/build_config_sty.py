#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Builds the sty file which provides definitions in tex that were configured in ../config
# 
# Reads   ../wiasct.py and thereby ../config/__init__.py
#
# Creates boa/generated-configs.sty
#         This file will be included in the book of abstract tex file
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

import syspath
syspath.append_parent_path()
import wiasct

config_sty_content = []
for name, color_object in wiasct.color_dict.items():
    config_sty_content.append(color_object.tex_definition())

with open('generated-config.sty', 'w') as f:
    f.write("\n".join(config_sty_content))
