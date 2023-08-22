import json
from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD, BNode
import os

class LynxDocument:
    # Define the namespaces
    LKG = Namespace("http://lkg.lynx-project.eu/def/")
    ELI = Namespace("http://data.europa.eu/eli/ontology#")
    NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
    DCT = Namespace("http://purl.org/dc/terms/")
    ITSRDF = Namespace("http://www.w3.org/2005/11/its/rdf#")
    AKN = Namespace("http://docs.oasis-open.org/legaldocml/ns/akn/3.0/CSD13")

    def __init__(self, base_uri):
        
        self.base_uri = base_uri
        self.g = self.initialize_graph()

    def convert_akn_elements(self):

        # Read the json file akn_elements.json as a tuple of (text, uri)
        with open('data/json/akn_elements.json', 'r') as file:
            # Read the json file akn_elements.json as a tuple of (text, uri)
            self.akn_elements = json.load(file)

        vocabulary = self.akn_elements.keys()
        uris = self.akn_elements.values()
        self.akn_elements = list(zip(vocabulary, uris))
        # Save them as akomantoso.jsonl in the data directory
        json_list = []
        for element in self.akn_elements:
           # Create json object
            json_obj = {
                'text': element[0],
                'suffix_key': element[1],
                'background_color': '#FF0000',
                'font_color': '#FFFFFF'
          }
        
            json_list.append(json_obj)
        
        with open('data/span/akomantoso.json', 'w') as outfile:
            json.dump(json_list, outfile)           
        
        return self.akn_elements

    def initialize_graph(self):
        # Create an RDF graph
        g = Graph()

        akomantoso = self.convert_akn_elements()
        # Load akomantoso into the graph
            
        # Load akn_elements into the graph
        #for element in self.akn_elements:
        #    g.add((URIRef(element['uri']), RDF.type, URIRef(element['type'])))
        #    g.add((URIRef(element['uri']), RDFS.label, Literal(element['label'])))

        # Bind prefixes
        g.bind("akn", self.AKN)
        g.bind("eli", self.ELI)
        g.bind("dct", self.DCT)
        g.bind("nif", self.NIF)
        g.bind("lkg", self.LKG)

        return g
    
    def load_from_jsonl(self, annotated):
        for element in annotated:
            self.create_document(element)

    def save_to_turtle(self, output_file):
        # Serialize the graph to Turtle and write to the output file
        self.g.serialize(destination=output_file, format='turtle')
    

    def metadata(self, doc_uri, json_obj):
        metadata = BNode()
        self.g.add((doc_uri, self.LKG.metadata, metadata))
        self.g.add((metadata, self.DCT.language, Literal("it")))
        self.g.add((metadata, self.ELI.id_local, Literal("doc_" + str(json_obj['id']))))
        
        # I do not know whether ELI actually supports identifiers at the paragraph level or whether it is Akoma Ntoso that does
        self.g.add((metadata, self.ELI.has_part, Literal(json_obj['article_id'])))
        self.g.add((metadata, self.ELI.chapter, Literal(json_obj['chapter_id'])))
        self.g.add((metadata, self.ELI.paragraph, Literal(json_obj['paragraph_id'])))

    def doc_uri(self, json_obj):
        return URIRef(self.base_uri + "doc_" + str(json_obj['id']).strip())
    
    def create_document(self, json_obj):
        
        # Create the document URI
        doc_uri = self.doc_uri(json_obj)
        

        # Add the document URI to the graph
        self.g.add((doc_uri, RDF.type, self.NIF.Context))
        self.g.add((doc_uri, RDF.type, self.LKG.LynxDocument))

        # Add the metadata
        self.metadata(doc_uri, json_obj)

        # Add the text
        self.text(doc_uri, json_obj)
        self.annotations(doc_uri, json_obj)



    def text(self, doc_uri, json_obj):
        # Add the text property
        text = json_obj['text']
        self.g.add((doc_uri, self.NIF.isString, Literal(text)))
        
        # Add the offset_ini and offset_end properties
        index = len(text)
        offset_ini = 0
        offset_end = index - 1
        self.g.add((doc_uri, self.NIF.beginIndex, Literal(offset_ini, datatype=XSD.nonNegativeInteger)))
        self.g.add((doc_uri, self.NIF.endIndex, Literal(offset_end, datatype=XSD.nonNegativeInteger)))
    
    def annotations(self, doc_uri, json_obj):
        
        classes = self.get_entities_uri()

        # Add entity annotations
        entities = json_obj['entities']
        for entity in entities:
            # Create the annotation 
            entity_uri = URIRef(doc_uri + "#offset_{}_{}".format(entity['start_offset'], entity['end_offset']))
            self.g.add((entity_uri, RDF.type, self.LKG.LynxAnnotation))
            self.g.add((entity_uri, RDF.type, self.NIF.OffsetBasedString))
            self.g.add((entity_uri, self.NIF.referenceContext, doc_uri))

            # Add the anchorOf, beginIndex and endIndex properties for the value
            value = json_obj['text'][entity['start_offset']:entity['end_offset']]
            self.g.add((entity_uri, self.NIF.anchorOf, Literal(value)))
            self.g.add((entity_uri, self.NIF.beginIndex, Literal(entity['start_offset'], datatype=XSD.nonNegativeInteger)))
            self.g.add((entity_uri, self.NIF.endIndex, Literal(entity['end_offset'], datatype=XSD.nonNegativeInteger)))
            
            label = entity['label']
            
            # Create a blank node for the annotation unit
            annotation_unit = BNode()
            self.g.add((entity_uri, self.NIF.annotationUnit, annotation_unit))
            self.g.add((annotation_unit, RDF.type, self.NIF.AnnotationUnit))
            self.g.add((annotation_unit, self.ITSRDF.taAnnotatorsRef, URIRef("https://alessionardin.eu")))
            self.g.add((annotation_unit, self.ITSRDF.taClassRef, URIRef(label)))
            self.g.add((annotation_unit, self.ITSRDF.taConfidence, Literal(1)))

            # check if the label is in the classes tuple at the first position
            for label, uri in classes:
                if label == entity['label']:
                    self.g.add((annotation_unit, self.ITSRDF.taIdentRef, URIRef(uri)))
                    break
            
    
            self.g.add((annotation_unit, RDF.value, Literal(value)))
    
    def get_entities_uri(self):
        # List to store the tuples of (text, uri)
        entities_list = []
        data_dir = 'data/span'

        # Iterate over all files in the data directory
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                with open(os.path.join(data_dir, filename), 'r') as file:
                    data = json.load(file)

                    # Extract the text and URI of the entities and add them to the list
                    for entity in data:
                        entities_list.append((entity.get('text', ''), entity.get('uri', '')))

        # Remove duplicates by converting the list to a set and back to a list
        entities_list = list(set(entities_list))

        return entities_list



