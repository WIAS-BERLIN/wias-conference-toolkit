from conference_pwa import SchedulexmlGraph, WiasctGraph
import sys


#TODO: proper arg parsing
output_format = ""
if len(sys.argv)>1:
    output_format = sys.argv[1]
#fallback to html if input is not understood
if output_format not in ["plain", "html"]:
    print("[WARNING] input parameter not understood. setting output_format to html")
    output_format = "html"

#db_format = "schedule.xml"
db_format = "wiasct"

if db_format == "schedule.xml":
    #xml_file = "../../pwa_archive/input_data_formats/iccopt_schedule.xml"
    xml_file = "../app-general/schedule.xml"
    g = SchedulexmlGraph(xml_file)
    g.add_node("index")
    g.add_node("rooms_overview")
    g.add_node("clusters_overview")
    print(" ##############")
    print(" # Event Tree #")
    print(" ##############\n")
    g.render_all_nodes(output_format = output_format, entry_node_id = "index", output_dir = "out")
    print("\n ##################")
    print(" # Rooms Overview #")
    print(" ##################\n")
    g.render_all_nodes(output_format = output_format, entry_node_id = "rooms_overview", output_dir = "out")
    print("\n #####################")
    print(" # Clusters Overview #")
    print(" #####################\n")
    g.render_all_nodes(output_format = output_format, entry_node_id = "clusters_overview", output_dir = "out")
else:
    #xml_file = "../../pwa_archive/input_data_formats/iccopt_db.xml"
    xml_file = "../xml/db.xml"
    g = WiasctGraph(xml_file)
    g.add_node("index")
    print(" ##############")
    print(" # Event Tree #")
    print(" ##############\n")
    g.render_all_nodes(output_format = output_format, entry_node_id = "index", output_dir = "out")
