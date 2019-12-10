## Description: this folder contains
- _wias-ct.xsd_ the xml schema file for the db
- clusters.xml : definition of the clusters (sometimes also known as streams/topics of the conference)


Do not forget to check the validity of the XML Schema after modification: a possible tool for this is `xmllint`, part of libxml2.
The command for it would be
`xmllint --noout --schema http://www.w3.org/2001/XMLSchema.xsd wias-ct.xsd`
