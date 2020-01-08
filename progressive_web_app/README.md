# Progressive Web App for WIAS Conference Toolkit #

This tool generates a human-readable overview over the events in the conference.
In this current early stage, the html output is not as useful as the name "progressive web app" suggests.

## Options

Currently the output-formats "plain" and "html" can be chosen, by providing the respective string as command line parameter.
"html" creates the html-files in the subdirectory "out/" and "plain" prints to stdout.

## Example

to get a nice overview of the events in the terminal, a command like this could be handy:

python build_pwa.py plain | pr -tw100 -4 -s"|" | less
(pr formats the output in columns and truncates content that does not fit in. the -tw100 option has to be adjusted to terminal size)
