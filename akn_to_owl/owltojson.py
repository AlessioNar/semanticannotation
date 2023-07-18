import rdflib
import random
import json
from rdflib import RDF, RDFS, OWL




def ontojson(filename):
    classes = ttl_to_json(filename, what="classes")
    properties = ttl_to_json(filename, what="properties")
    return classes, properties


def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def shade_color(color, shading_factor):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    r = max(0, min(255, r + shading_factor))
    g = max(0, min(255, g + shading_factor))
    b = max(0, min(255, b + shading_factor))
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def ttl_to_json(file_path, what):
    graph = rdflib.Graph()
    graph.parse(file_path, format="turtle")
    namespaces = dict(graph.namespaces())
    
    if what == "classes":
        classes = get_classes(graph, namespaces)
        return classes
    elif what == "properties":
        properties = get_properties(graph, namespaces)
        return properties
    

def get_classes(graph, namespaces):
    classes = {}
    
    # Iterate over all subjects in the graph
    for subject in graph.subjects():
        if isinstance(subject, rdflib.term.URIRef):
            # Check if the subject is an instance of owl:Class
            if (subject, RDF.type, OWL.Class) in graph:
                class_name = get_class_name(subject, namespaces)
                
                if class_name not in classes:
                    classes[class_name] = {
                        "text": class_name,
                        "suffix_key": chr(97 + len(classes) % 26) * (len(classes) // 26 + 1),
                        "background_color": random_color(),
                        "text_color": "#ffffff",
                        "uri": str(subject)
                    }
    
    return classes


def get_class_name(uri, namespaces):
    prefix = None
    prefix_uri = str(uri).split("#")[0]
    
    for namespace_prefix, namespace_uri in namespaces.items():
        if namespace_uri in prefix_uri:
            prefix = namespace_prefix
        if prefix_uri in namespace_uri:
            prefix = namespace_prefix
    
    if '#' in str(uri):
        class_name = str(uri).rsplit("#", 1)[1]
    else:
        class_name = str(uri).rsplit("/", 1)[1]
    
    if prefix:
        class_name = prefix + ":" + class_name
    
    return class_name


def get_properties(graph, namespaces):
    
    properties = {}
    for s, p, o in graph.triples((None, rdflib.RDF.type, rdflib.OWL.ObjectProperty)):
        if isinstance(s, rdflib.term.URIRef):
            if o in properties:
                color = shade_color(properties[o]['background_color'], -10)
            else:
                color = random_color()

            # Split the URI at the last slash ("/") to get prefix and property_name
            split_uri = str(s).rpartition('/')
            prefix_uri = split_uri[0].rpartition('/')[2]
            property_name = str(s).rsplit("#")[1]

            
            prefix = None
            prefix_uri = str(s).split("#")[0]
            #print(prefix_uri)
            
            for namespace_prefix, namespace_uri in namespaces.items():
                #print(namespace_prefix, namespace_uri)
                # If there is a partial match between the prefix and the namespace_uri
                if namespace_uri in prefix_uri:
                    prefix = namespace_prefix
                    #print(prefix)
                if prefix_uri in namespace_uri:
                    prefix = namespace_prefix
                    #print(prefix)

            # Create prefix:property_name
            full_property_name = f"{prefix}:{property_name}"
            
            # Progressively assign lowercase letters to the properties
            suffix_key = chr(97 + len(properties) % 26) * (len(properties) // 26 + 1)

            properties[s] = {
                "text": str(full_property_name),
                "suffix_key": suffix_key.lower(),
                "background_color": str(color),
                "text_color": "#ffffff"
                #"uri": str(s),
            }

    return properties