import jinja2
from lxml import etree
from lxml import objectify
from pathlib import Path

class Node():
    html_template = "templates/node_template.html"
    node_type = ""

    def __init__(self, graph, xml_element=None, parent=None, children=None, template=None, **kwargs):
        self.xml_element = xml_element
        self.graph = graph

        self.properties = kwargs
        if children==None:
            self.children = []
        else:
            self.children = children
        self.parent = parent
        self.set_properties()
        self.graph.register_node(self)
        self.construct_children()
        if template is not None:
            self.html_template = template

    def set_properties(self):
        pass

    def construct_children(self):
        pass

    def get_filepath(self):
        if "filepath" in self.properties.keys():
            return self.properties["filepath"]
        else:
            filename = self.node_type
            if "node_id" in self.properties.keys():
                filename += "_" + self.properties["node_id"]
            return filename+".html"

    def get_url(self):
        return self.get_filepath()

    def render(self, recursive=True, output_format="html", **kwargs):
        if output_format=="plain":
            self._render_plain(**kwargs)
            if "indent" in kwargs.keys():
                kwargs["indent"] += 2
            else:
                kwargs["indent"] = 2
        else:
            self._render_html(**kwargs)
        if recursive:
            for child in self.children:
                child.render(recursive=True, output_format=output_format, **kwargs)

    #this method could possibly be redefined in every subclass for more specific output
    def _render_plain(self, template=None, outfile=None, recursive=True, indent=0, **kwargs):
        #geht das auch gut mit jinja temlating? waeren wahrscheinlich zu viele files dann
        print(" "*indent, self.node_type.upper())
        for k, v in self.properties.items():
            print(" "*indent, k, ":", v)
        #do some textwrap here

    def _render_html(self, template=None, outfile=None, recursive=True, **kwargs):
        if template is None:
            template = self.html_template
        if outfile is None:
            #TODO: add prefix output folder
            prefix = "."
            if "output_dir" in kwargs.keys():
                prefix = kwargs["output_dir"]
            outfile = prefix+"/"+self.get_filepath()

        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True)
        jinja_template = templateEnv.get_template(template)
        outputText = jinja_template.render({
            "properties": self.properties,
            "children": self.children,
            "parent": self.parent,
            "config": self.graph.config,
        })

        Path(prefix).mkdir(parents=True, exist_ok=True)
        with open(outfile, "w") as fh:
            fh.write(outputText)


class Graph():
    def __init__(self, xml_file, config=None, parent_expression=None, db_format="schedule.xml"):
        self.all_nodes = []
        self.root_nodes = []
        self.id2node = dict()
        self.room2schedulesessions = dict()
        self.cluster2schedulesessions = dict()

        self.xml_file = xml_file
        self.db_format = db_format

        #lxml
        parser = objectify.makeparser()
        with open(self.xml_file, "r") as f:
            self.xmltree = objectify.parse(f, parser)

        if config is not None: #config contains the plotting-settings
            self.config = config
        else:
            self.config = dict()

        if parent_expression is not None:
            self.add_parent_node(self.xmltree.xpath(parent_expression), self, )

    def register_node(self, node):
        self.all_nodes.append(node)

        node_type_id = node.node_type
        #if node_id := node.properties.get("node_id"): #py3.8
        node_id = node.properties.get("node_id")
        if node_id is not None:
            node_type_id += "_" + node_id
            if node_type_id in self.id2node.keys():
                print(f"[WARNING] there seem to be two nodes with same id {node_type_id}")
        #print(f"[registering] {node_type_id}")
        self.id2node[node_type_id] = node

        #if room := node.properties.get("room"): #py3.8
        room = node.properties.get("room")
        if room is not None:
            if room not in self.room2schedulesessions.keys():
                self.room2schedulesessions[room] = set()
            self.room2schedulesessions[room].add(node)

        #if cluster := node.properties.get("cluster"): #py3.8
        cluster = node.properties.get("cluster")
        if cluster is not None:
            if cluster not in self.cluster2schedulesessions.keys():
                self.cluster2schedulesessions[cluster] = set()
            self.cluster2schedulesessions[cluster].add(node)

    def add_node(self, node_cls, **kwargs):
        if type(node_cls) == str:
            if self.db_format == "schedule.xml":
                if node_cls == "index":
                    node_cls = RootSchedule
                elif node_cls == "room_overview":
                    node_cls = MetaRoomsSchedule
                elif node_cls == "clusters_overview":
                    node_cls = MetaClustersSchedule
                else:
                    print("[ERROR] node type unknown")
            elif self.db_format == "wiasct":
                if node_cls == "index":
                    node_cls = HomeWiasct
                else:
                    print("[ERROR] node type unknown")
            else:
                print("[ERROR] db_format unknown")
        self.root_nodes.append(node_cls(self, **kwargs))

    def render_all_nodes(self, recursive=True, entry_node_id=None, **kwargs):
        if recursive:
            #plain-rendering has to be done recursive!
            if entry_node_id == None:
                entry_node = self.root_nodes[0]
            else:
                entry_node = self.id2node[entry_node_id]
            entry_node.render(recursive=True, **kwargs)
        else: #I don't know yet if non-recursive rendering is interessting.
            for node in self.all_nodes:
                node.render(**kwargs)

#BEGIN# schedule.xml structure
class EventSchedule(Node):
    #html_template = "templates/template.html"
    node_type = "event"

    def set_properties(self):
        self.properties["node_id"] = str(self.xml_element.attrib["id"])
        self.properties["title"] = str(self.xml_element.find("title"))
        self.properties["start"] = str(self.xml_element.find("start"))

class RoomSchedule(Node):
    #html_template = "templates/template.html"
    node_type = "room"

    def set_properties(self):
        self.properties["name"] = str(self.xml_element.attrib["name"])
        self.properties["title"] = "Room " + self.properties["name"]
        self.properties["node_id"] = self.parent.properties["node_id"] + "_" + self.properties["name"].replace(" ", "")
    def construct_children(self):
        xml_elements = self.xml_element.findall("event")
        for elt in xml_elements:
            self.children.append(EventSchedule(self.graph, elt, parent=self))


class MetaRoomsSchedule(Node):
    #html_template = "templates/template.html"
    node_type = "rooms_overview"

    def set_properties(self):
        self.properties["title"] = "Rooms Overview"

    def construct_children(self):
        #want to get every room uniquely
        all_rooms = set([str(room_nr) for room_nr in  self.graph.xmltree.xpath("//event/room")])
        for room in sorted(all_rooms):
            room_element = self.graph.xmltree.xpath(f"//room[@name='{room}']")[0]
            #print(room_element.attrib)
            self.children.append(MetaRoomSchedule(self.graph, room_element, parent=self))

class MetaRoomSchedule(Node):
    #for all events in this room
    #html_template = "templates/template.html"
    node_type = "room_overview"

    def set_properties(self):
        self.properties["name"] = str(self.xml_element.attrib["name"])
        self.properties["node_id"] = self.properties["name"].replace(" ", "")

    def construct_children(self):
        xml_elements = self.graph.xmltree.xpath(f"//event[room='{self.properties['name']}']")
        for elt in xml_elements:
            elt_id = "event" + "_" + elt.attrib["id"]
            self.children.append(self.graph.id2node[elt_id])


class MetaClustersSchedule(Node):
    #html_template = "templates/template.html"
    node_type = "clusters_overview"

    def set_properties(self):
        self.properties["title"] = "Clusters Overview"

    def construct_children(self):
        all_clusters = set([str(c) for c in self.graph.xmltree.xpath("//track")])
        for cluster in sorted(all_clusters):
            self.children.append(MetaClusterSchedule(self.graph, name=cluster, parent=self))

class MetaClusterSchedule(Node):
    #html_template = "templates/template.html"
    node_type = "cluster_overview"

    def set_properties(self):
        self.properties["node_id"] = self.properties["name"].replace(" ", "")

    def construct_children(self):
        cluster_name = self.properties["name"]
        events = self.graph.xmltree.xpath(f"//event[track='{cluster_name}']")
        for event in events:
            elt_id = "event" + "_" + event.attrib["id"]
            self.children.append(self.graph.id2node[elt_id])


class DaySchedule(Node):
    #html_template = "templates/template.html"
    node_type = "day"

    def set_properties(self):
        self.properties["date"] = str(self.xml_element.attrib["date"])
        self.properties["title"] = "Day "+self.properties["date"]
        self.properties["node_id"] = self.properties["date"] #TODO: is this appropriate id?

    def construct_children(self):
        xml_elements = self.xml_element.findall("room")
        for elt in xml_elements:
            self.children.append(RoomSchedule(self.graph, elt, parent=self))


class RootSchedule(Node):
    #html_template = "templates/template.html"
    node_type = "index"

    def set_properties(self):
        self.properties["title"] = "Conference Overview"
        self.properties["conference_title"] = str(self.graph.xmltree.xpath("//conference/title")[0])

    def construct_children(self):
        xml_elements = self.graph.xmltree.xpath("//day")
        for elt in xml_elements:
            self.children.append(DaySchedule(self.graph, elt, parent=self))
#END# schedule.xml structure


#BEGIN# wiasct.xsd structure
#this does not function yet
class HomeWiasct(Node): #wiasct-format
    #html_template = "templates/home_template.html"
    node_type = "index"

    def construct_children(self):
        #TODO: an welcher Stelle sollen Plenaries, Semis, ... anders behandelt werden?
        for id_str in ["Mon_1", "Mon_2", "Mon_3"]:
            d, slot = id_str.split("_")
            #self.children.add(TimeSlot(None, self.graph, day=d, slot=slot))
#END# wiasct.xsd structure


#xml_file = "input_data_formats/iccopt_schedule.xml"
#g = Graph(xml_file)
#g.add_node(RootSchedule)
#g.add_node(MetaRoomsSchedule)
#g.add_node(MetaClustersSchedule)
#g.render_all_nodes(output_format = "html", entry_node_id = "index", output_dir = "out")
