# WIAS Conference Toolkit: Vouchers #

The Latex templates in this package are pulished under the Creative Commons Licence CC-BY-SA 4.0. 
Please attribute WIAS Berlin. 

## Dinner tickets ##

The script export\_dinner\_tickets.py produces dinnerparticipants.tex, which is included n the Latex template vouchers-dinner.tex. 
The latter can be compiled with Latex to produce a pdf with all dinner tickets. 

In export\_dinner\_tickets.py, you can edit the variables  
free\_ticket\_roles and organizing\_committee to influence who will have a free ticket, and will be marked as a "special guest"


### Workflow with ../converia-input/build\_xml\_db.py 

To create A4 dinner tickets for dinner participants, you need to 
1. fill the respective columns in ../EVENT_Registrationlist.csv (non-scientific program), see ../converia-input/README.md
4. use 'make vouchers' in wias-conference-toolkit

### Workflow based directly on ../xml/db.xml

To create a special meeting and produce vouchers for its participants, you need to 
1. include your meeting indicator (e.g., BOARD or OTHERBOARD) in ../xml/wiasct.xsd to be allowed as a value in 'meetingtype'
2. include the corresponding element 'meeting' in with th meeting indicator BOARD in ../xml/db.xml
3. use 'make vouchers' in wias-conference-toolkit


## Special meetings ##

If for instance board-meetings take place in the course of your conference, you may want to produce vouchers for the respective participants. 
The vouchers from this template can be printed on Sigel LP798 Business Cards. 

### Workflow with ../converia-input/build\_xml\_db.py 

To create a special meeting and produce vouchers for its participants, you need to 
1. create the respective csv-file in ../converia-input, see ../converia-input/README.md
2. include your meeting indicator (e.g., BOARD or OTHERBOARD) in ../xml/wiasct.xsd to be allowed as a value in 'meetingtype'
3. include your csv-file in the rule for ../xml/db.xml in ../Makefile
4. use 'make vouchers' in wias-conference-toolkit

### Workflow based directly on ../xml/db.xml

To create a special meeting and produce vouchers for its participants, you need to 
1. include your meeting indicator (e.g., BOARD or OTHERBOARD) in ../xml/wiasct.xsd to be allowed as a value in 'meetingtype'
2. include the corresponding element 'meeting' in with th meeting indicator BOARD in ../xml/db.xml
3. use 'make vouchers' in wias-conference-toolkit
