# WIAS Conference Toolkit: Data base for a generic schedule viewer app

## Overview

'build_schedule.py' builds an xml data base that complies with the scheme defined in 'schedule.xml.xsd'. 
In this way, some generic conference viewer apps can be used. 
Examples are Giggity, Congress (iOS). 

A minimalistic workflow with Giggity is for instance: 
1. Build schedule.xml
2. Upload schedule.xml to URL
3. Ask conference participants to install Giggity
4. Publish the URL, such that participants can configure their app installation. 

## Usage

The date, event name, time slot length etc. need to be adjusted manually in ../config/\_\_init\_\_.py

#### Reads

The database ../xml/db.xml

#### Creates 

app-general/schedule.xml
