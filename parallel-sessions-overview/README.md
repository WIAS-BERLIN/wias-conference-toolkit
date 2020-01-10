# WIAS Conference Toolkit: Overview of parallel sessions in a nive pdf file

## Overview

'build\_parallel\_sessions\_overview.py' creates a tex file that can be compiled with pdflatex to
obtain a pdf file with an overview on parallel sessions. 

## Usage

1. Adjust ../config/tex-templates/header\_parallel\_sessions\_overview.tex
2. Adjust conference data in ../config/\_\_init\_\_.py
3. Go to the parent directory and use <pre>make parallel-sessions-overview/Parallel_sessions_overview.pdf</pre>
Or run build\_parallel\_sessions\_overview.py

#### Reads

* The database ../xml/db.xml
* ../config/tex-templates/header\_parallel\_sessions\_overview.tex
* ../config/\_\_init\_\_.py

#### Creates 

<pre>parallel-sessions-overview/Parallel\_sessions\_\overview.tex</pre>

After compilation with Latex: 
<pre>parallel-sessions-overview/Parallel\_sessions\_\overview.pdf</pre>
