
# Step 1: Read the skos file serialised in turtle format

# Step 2: Extract the top classes and properties from the skos file

# Step 3: Save the top classes and properties to a file as a list of dictionaries, focusing on the prefLabel in english and the uri

# Step 4: Convert the skos file to a jsonl file with the following format: 
"""
 {
        "text": "Cat",
        "suffix_key": "12",
        "background_color": "#FF0000",
        "text_color": "#ffffff"
    }
""" 

# Where text is the prefLabel in english, suffix_key is a unique id, background_color is a random color and text_color is white


import json
import jsonlines
import random
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import SKOS

# Define namespaces
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

def parse_skos(file_path):
    """ 
    Parses a SKOS file and extracts top classes and properties.
    
    :param file_path: Path to the SKOS file.
    :return: Two lists of dictionaries representing top classes and properties.
    """
    try:
        g = Graph()
        g.parse(file_path, format="xml")
        print(f"Successfully parsed the file: {file_path}")
    except Exception as e:
        print(f"Error parsing the file: {e}")
        return [], []
    
    top_classes = []
    
    # Get the concepts that have at least another concept under them
    qres = g.query(
        """
        SELECT DISTINCT ?s ?label ?p
        WHERE {
            ?s skos:topConceptOf ?o .
            ?s skos:prefLabel ?label .
            FILTER (lang(?label) = 'en')
            ?s ?p ?o .
        }
        """,
        initNs={"skos": SKOS}
    )
    print(f"Found {len(qres)} top concepts")
 
    # This loop will iterate over each row in the results of the SPARQL query (qres)
    for row in qres:

        # Each row consists of three parts: the subject (s), label (prefLabel in English), and the predicate (p)
        s, label, p = row

        # Converting subject URI (an rdflib term) into a Python string for easy handling
        uri = s.toPython()

        # Checking if the predicate (relationship type) of the triple is 'skos:narrower'
        # In SKOS, 'narrower' is used to express a hierarchical or taxonomic relationship between two concepts
        # If the predicate is 'skos:narrower', it means the subject is a broader concept than the object
        if p == SKOS.topConceptOf:

            # If the predicate is 'narrower', then we add this concept to our list of top classes
            # The concept is represented as a dictionary with the preferred English label (prefLabel) and the unique resource identifier (URI)
            top_classes.append({'prefLabel': label, 'uri': uri})

    return top_classes

def write_to_file(data, file_path):
    """ 
    Writes data to a file in JSON format.
    
    :param data: Data to write.
    :param file_path: Path to the output file.
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error writing to file: {e}")


def enrich_json(dictionary):
    """ 
    Main function to enrich the JSONL file with random colors.
    """
    counter = 0
    dictionary = sorted(dictionary, key=lambda k: k['prefLabel'])
    for concept in dictionary:        
        concept['text'] = concept['prefLabel']
        # Remove the prefLabel key
        del concept['prefLabel']
        # Create a unique id for each concept
        concept['suffix_key'] = concept['uri']
        concept['background_color'] = '#{:06x}'.format(random.randint(0, 0xFFFFFF))
        concept['text_color'] = '#ffffff'
        counter += 1
    return dictionary


def skos_to_json():
    """ 
    Main function to parse SKOS file and write the extracted data to files.
    """
    top_classes = parse_skos('data/skos/eurovoc_in_skos_core_concepts.rdf')
    if top_classes:
        top_classes = enrich_json(top_classes)
        write_to_file(top_classes, 'data/span/top_classes.json')



