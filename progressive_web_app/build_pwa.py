from conference_pwa import Graph
import sys

#configuration
db_format = "schedule.xml" # or "wiasct" which is not ready yet
xml_file = "../app-general/schedule.xml"

#TODO: proper arg parsing
output_format = ""
if len(sys.argv)>1:
    output_format = sys.argv[1]
#fallback to html if input is not understood
if output_format not in ["plain", "html"]:
    print("[WARNING] input parameter not understood. setting output_format to html")
    output_format = "html"

g = Graph(xml_file, db_format=db_format, )
g.add_node("index")
g.render_all_nodes(output_format = output_format, entry_node_id = "index", output_dir = "out")
