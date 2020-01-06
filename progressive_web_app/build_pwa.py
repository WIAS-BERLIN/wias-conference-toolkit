from conference_pwa import Graph

#configuration
db_format = "schedule.xml" # or "wiasct" which is not ready yet
xml_file = "../app-general/schedule.xml"
#output_format = "plain"
output_format = "html"

g = Graph(xml_file, db_format=db_format, )
g.add_node("index")
g.render_all_nodes(engine = output_format, entry_node_id = "index", output_dir = "out")
