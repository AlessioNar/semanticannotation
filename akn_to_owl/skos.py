import json
import random
from rdflib import Graph, Namespace
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
       SELECT DISTINCT ?topConcept ?label ?p
        WHERE {
            ?s skos:hasTopConcept ?topConcept .
            ?topConcept skos:prefLabel ?label .
            FILTER (lang(?label) = 'en')
            ?s ?p ?o .
        }
        """,
        initNs={"skos": SKOS}
    )
    print(f"Found {len(qres)} top concepts")
    
    # This loop will iterate over each row in the results of the SPARQL query (qres)
    for row in qres:
        print(row)

        # Each row consists of three parts: the subject (s), label (prefLabel in English), and the predicate (p)
        s, label, p = row

        # Converting subject URI (an rdflib term) into a Python string for easy handling
        uri = s.toPython()

        # Checking if the predicate (relationship type) of the triple is 'skos:narrower'
        # In SKOS, 'narrower' is used to express a hierarchical or taxonomic relationship between two concepts
        # If the predicate is 'skos:narrower', it means the subject is a broader concept than the object
        if p == SKOS.hasTopConcept:

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
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error writing to file: {e}")


def enrich_json(dictionary):
    """ 
    Main function to enrich the JSON file with random colors.
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
        write_to_file(top_classes, 'data/span/skos.json')



