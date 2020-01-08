import jinja2
from lxml import etree
from lxml import objectify
from pathlib import Path
import sys, errno

from conference_pwa.conference_tree import *

#auxiliary functions
def get_all_timeslots(db_root):
    db_root.xpath()

class TalkWiasct(Node):
    #html_template = "templates/home_template.html"
    node_type = "talk"

    def set_properties(self):
        id = str(self.xml_element.ID)
        self.properties["node_id"] = id
        self.properties["title"] = str(self.xml_element.find("title"))
        self.properties["abstract"] = str(self.xml_element.find("abstract"))

class SchedulesessionWiasct(Node):
    #html_template = "templates/home_template.html"
    node_type = "schedule_session"

    def set_properties(self):
        self.properties["title"] = str(self.xml_element.find("title"))
        id = str(self.xml_element.ID)
        self.properties["id"] = id
        self.properties["node_id"] = id
        self.properties["room"] = str(self.xml_element.room)
        self.properties["cluster"] = str(self.xml_element.cluster)
        #date, time

    def construct_children(self):
        paperids = self.xml_element.xpath("./paper/paperid")
        for paperid in paperids:
            xml_talk = self.xml_element.xpath(f"//talks/talk[ID={paperid}]")[0]
            self.children.append(TalkWiasct(self.graph, xml_element=xml_talk))

class TimeslotWiasct(Node):
    #html_template = "templates/home_template.html"
    node_type = "timeslot"

    def set_properties(self):
        d = self.properties["day"]
        slot = self.properties["slot"]
        self.properties["title"] = f"{d}_{slot}"
        self.properties["node_id"] = f"{d}_{slot}"

    def construct_children(self):
        d = self.properties["day"]
        slot = self.properties["slot"]
        sessions = self.graph.xmltree.xpath(f"//schedule_session[timeslot/day='{d}' and timeslot/slot='{slot}']")
        for session in sessions:
            self.children.append(SchedulesessionWiasct(self.graph, xml_element=session))

class HomeWiasct(Node):
    #html_template = "templates/home_template.html"
    node_type = "index"

    def set_properties(self):
        self.properties["title"] = "Conference Overview"
        self.properties["conference_title"] = "CONF_TITLE_NOT_AVAILABLE"

    def construct_children(self):
        #TODO: an welcher Stelle sollen Plenaries, Semis, ... anders behandelt werden?
        for id_str in ["Mon_1", "Mon_2", "Mon_P", "Mon_SP"]:
            d, slot = id_str.split("_")
            self.children.append(TimeslotWiasct(self.graph, day=d, slot=slot))

class WiasctGraph(Graph):
    def add_node(self, node_cls, **kwargs):
        if type(node_cls) == str:
            if node_cls == "index":
                node_cls = HomeWiasct
            else:
                print("[ERROR] node type unknown")
        self.root_nodes.append(node_cls(self, **kwargs))
