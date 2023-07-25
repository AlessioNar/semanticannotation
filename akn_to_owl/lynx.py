import json
from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD, BNode

class LynxDocument:
    # Define the namespaces
    LKG = Namespace("http://lkg.lynx-project.eu/def/")
    ELI = Namespace("http://data.europa.eu/eli/ontology#")
    NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
    DCT = Namespace("http://purl.org/dc/terms/")
    ITSRDF = Namespace("http://www.w3.org/2005/11/its/rdf#")

    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.g = self.initialize_graph()

    def initialize_graph(self):
        # Create an RDF graph
        g = Graph()

        # Bind prefixes
        g.bind("eli", self.ELI)
        g.bind("dct", self.DCT)
        g.bind("nif", self.NIF)
        g.bind("lkg", self.LKG)

        return g
    
    def load_from_jsonl(self, jsonl_file):
        with open(jsonl_file, 'r') as file:
            for line in file:
                json_obj = json.loads(line)
                self.create_document(json_obj)

    def save_to_turtle(self, output_file):
        # Serialize the graph to Turtle and write to the output file
        self.g.serialize(destination=output_file, format='turtle')
    

    def metadata(self, doc_uri, json_obj):
        metadata = BNode()
        self.g.add((doc_uri, self.LKG.metadata, metadata))
        self.g.add((metadata, self.DCT.language, Literal("it")))
        self.g.add((metadata, self.ELI.id_local, Literal("doc_" + str(json_obj['id']))))

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

        # Add entity annotations
        entities = json_obj['entities']
        for entity in entities:
            entity_uri = URIRef(self.base_uri + "3988#offset_{}_{}".format(entity['start_offset'], entity['end_offset']))
            self.g.add((entity_uri, RDF.type, self.LKG.LynxAnnotation))
            self.g.add((entity_uri, RDF.type, self.NIF.OffsetBasedString))
            self.g.add((entity_uri, self.NIF.referenceContext, doc_uri))
            
            label = entity['label']
            # Add the label property as a nif:AnnotationUnit, itsrdf:taIdentRef
            self.g.add((entity_uri, RDF.type, self.NIF.AnnotationUnit))
            self.g.add((entity_uri, self.ITSRDF.taIdentRef, URIRef(label)))  
            self.g.add((entity_uri, self.LKG.label, Literal(label)))
            
            value = json_obj['text'][entity['start_offset']:entity['end_offset']]
            self.g.add((entity_uri, self.NIF.anchorOf, Literal(value)))
            self.g.add((entity_uri, self.NIF.beginIndex, Literal(entity['start_offset'], datatype=XSD.nonNegativeInteger)))
            self.g.add((entity_uri, self.NIF.endIndex, Literal(entity['end_offset'], datatype=XSD.nonNegativeInteger)))
