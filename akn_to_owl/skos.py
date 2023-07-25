import json
import random
from rdflib import Graph, Namespace
from rdflib.namespace import SKOS

class SKOSParser:
    # Define namespaces
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

    def __init__(self, file_path):
        self.file_path = file_path
        self.graph = Graph()
    
    def parse_skos(self):
        """ 
        Parses a SKOS file and extracts top classes and properties.
        """
        try:
            self.graph.parse(self.file_path, format="xml")
            print(f"Successfully parsed the file: {self.file_path}")
        except Exception as e:
            print(f"Error parsing the file: {e}")
            return [], []

        top_classes = self._get_top_classes()
        return top_classes

    def _get_top_classes(self):
        """
        Get the top classes from the parsed graph.
        """
        top_classes = []
        qres = self.graph.query(
            """
           SELECT DISTINCT ?s ?label ?p ?o      
             WHERE {
                ?s a skos:Concept .
                ?s skos:prefLabel ?label .
                FILTER NOT EXISTS { ?x skos:topConceptOf ?s . }
                FILTER (lang(?label) = 'en')
                ?s ?p ?o .
                
            }
            """,
            initNs={"skos": SKOSParser.SKOS}
        )
        print(f"Found {len(qres)} top concepts")

        for row in qres:
            #print(row)
            s, label, p, o = row
            uri = s.toPython()
            prefLabel = label.toPython()
            # get the second to last element of the uri and save it as prefix
            prefix = uri.split('/')[-2]            
            # Check if the concept is already in the top_classes list
            if not any(element['uri'] == uri for element in top_classes):
                top_classes.append({
                    "uri": uri,
                    "prefLabel": prefLabel,
                    "prefix": prefix

                })
        print(top_classes)
        

        
        return top_classes

    @staticmethod
    def write_to_file(data, file_path):
        """ 
        Writes data to a file in JSON format.
        """
        try:
            # Create a new file, and if it already exists, overwrite it
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Successfully wrote to the file: {file_path}")
        except Exception as e:
            print(f"Error writing to the file: {e}")





    @staticmethod
    def enrich_json(dictionary):
        """ 
        Main function to enrich the JSON file with random colors.
        """
        counter = 0
        dictionary = sorted(dictionary, key=lambda k: k['prefLabel'])
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        

        for concept in dictionary:        
            concept['text'] = concept['prefix'] + ':' + concept['prefLabel']
            del concept['prefLabel']
            concept['suffix_key'] = concept['uri']
        
            concept['background_color'] = color
            concept['text_color'] = '#ffffff'
            counter += 1
        return dictionary




