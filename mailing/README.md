# WIAS Conference Toolkit: Mailing facilities

## Overview

Mass mailings can be sent with the function send\_email in send\_email.py. 
Two sample files for mailings are in 
* email\_general.py (simple mailing to all participants of the conference)
* email\_general_short (mailing to speakers of talks where data like title or abstract are still missing)

## How to 

1. Configure your email server in ../config/\_\_init\_\_.py
2. Copy one of the sample files and adjust your mailing, you can use dry run mode to see at first a list of all recipients
3. After proper testing of the recipients list and content, send your email by running your copy of the sample file

## Documentation of the mailing

Files with the mailing documentation are saved in the folder doc\_mailings. 
You should remove those belonging to your testing and only keep those for the final mailings. 

Additionally, you may want to send every message in BCC to a documentation recipient email address. 
This is configured in the mailing script (i.e., your copied sample file). 
