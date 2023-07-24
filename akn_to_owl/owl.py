import json
import random
import rdflib
from rdflib import RDF, RDFS, OWL


class OntologyParser:
    def __init__(self, file_path):
        self.graph = rdflib.Graph()
        self.graph.parse(file_path, format="turtle")
        self.namespaces = dict(self.graph.namespaces())

    def random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def shade_color(self, color, shading_factor):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        r = max(0, min(255, r + shading_factor))
        g = max(0, min(255, g + shading_factor))
        b = max(0, min(255, b + shading_factor))
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def get_prefix(self, uri):
        prefix = None
        prefix_uri = str(uri).split("#")[0]

        for namespace_prefix, namespace_uri in self.namespaces.items():
            if namespace_uri in prefix_uri or prefix_uri in namespace_uri:
                prefix = namespace_prefix

        class_name = str(uri).rsplit("#" if '#' in str(uri) else "/", 1)[1]

        if prefix:
            class_name = prefix + ":" + class_name

        return class_name

    def get_classes(self):
        classes = []

        for subject in self.graph.subjects():
            if isinstance(subject, rdflib.term.URIRef) and (subject, RDF.type, OWL.Class) in self.graph:
                class_name = self.get_prefix(subject)

                if not any(element['text'] == class_name for element in classes):
                    classes.append({
                        "text": class_name,
                        "suffix_key": str(subject),
                        "background_color": self.random_color(),
                        "text_color": "#ffffff",
                        "uri": str(subject)
                    })

        return classes

    def get_properties(self):
        properties = []

        for s, p, o in self.graph.triples((None, rdflib.RDF.type, rdflib.OWL.ObjectProperty)):
            if isinstance(s, rdflib.term.URIRef):
                color = self.shade_color(properties[o]['background_color'], -10) if o in properties else self.random_color()

                property_name = f"{self.get_prefix(s)}"

                # Check if the property name is already in the properties dictionary
                if not any(prop['text'] == property_name for prop in properties):
                    properties.append({
                        "text": property_name,
                        "suffix_key": str(s),
                        "background_color": str(color),
                        "text_color": "#ffffff"
                    })

        return properties

    def ontojson(self):
        return self.get_classes(), self.get_properties()


def owl_to_json(path):
    parser = OntologyParser(path)
    classes, properties = parser.ontojson()

    if classes:
        with open('data/span/classes.json', 'w') as f:
            json.dump(classes, f, indent=4)
    
    if properties:
        with open('data/span/properties.json', 'w') as f:
            json.dump(properties, f, indent=4)
