import xml.etree.ElementTree as ET
from os.path import join, exists
from os import environ, listdir
import json


class XMLFile:
    def __init__(self, path):
        self.path = path
        if not exists(path):
            raise ValueError(f"No file at {path}")
        self.tree = ET.parse(self.path)
        self.root = self.tree.getroot()

    def inject(self, payload, xpath, namespace=None):
        if xpath:
            attachment_point = self.tree.find(xpath, namespace)
        else:
            attachment_point = self.root
        for node in payload.findall('nodes/*'):
            attachment_point.append(node)
        for attribute in payload.findall("attributes/*"):
            attachment_point.attrib[attribute.get("key")] = attribute.get("value")

    def dump(self, in_place=True):
        file_name = self.path if in_place else self.path + ".tst"

        with open(file_name, "w") as out_file:
            self.tree.write(out_file, encoding="unicode")


class Patch(XMLFile):
    def __init__(self, path):
        super().__init__(path)
        self.target_file = self.root.find("target").get("file")
        self.xpath = self.root.find("target").get("xpath", None)
        self.payload = self.root.find("payload")
        self.target_namespace = None
        if self.root.find("target_namespace") and self.root.find("target_namespace").text:
            self.target_namespace = json.loads(self.target_namespace)


if __name__=="__main__":
    configuration_path = environ["CONFIG_PATH"]
    patches_path = environ['PATCHES_PATH']

    for patch_file in listdir(patches_path):
        patch = Patch(join(patches_path, patch_file))
        target = XMLFile(join(configuration_path, patch.target_file))
        target.inject(patch.payload, patch.xpath, patch.target_namespace)
        target.dump()

