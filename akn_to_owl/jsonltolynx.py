import json
from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD, BNode

# Define the namespaces
LKG = Namespace("http://lkg.lynx-project.eu/def/")
ELI = Namespace("http://data.europa.eu/eli/ontology#")
NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
DCT = Namespace("http://purl.org/dc/terms/")
ITSRDF = Namespace("http://www.w3.org/2005/11/its/rdf#")

def convert_jsonl_to_lynx(jsonl_file, output_file, base_uri):
    
    g = initialize_graph()
    with open(jsonl_file, 'r') as file:
        for line in file:
            json_obj = json.loads(line)
            g = create_document(json_obj, base_uri, g)
    
    # Serialize the graph to Turtle and write to the output file
    g.serialize(destination=output_file, format='turtle')

def initialize_graph():
    # Create an RDF graph
    g = Graph()
    
    # Bind prefixes
    g.bind("eli", ELI)
    g.bind("dct", DCT)
    g.bind("nif", NIF)
    g.bind("lkg", LKG)

    return g

def create_document(json_obj, base_uri, g):
    # Create a LynxDocument URI
    doc_uri = json_obj['id']
    doc_uri = URIRef(base_uri + "doc_" + str(doc_uri).strip())        
    g.add((doc_uri, RDF.type, NIF.Context))
    g.add((doc_uri, RDF.type, LKG.LynxDocument))

    # Add the type property
    g.add((doc_uri, RDF.type, LKG.Legislation))
    
    # Add the metadata    
    metadata = BNode()
    g.add((doc_uri, LKG.metadata, metadata))
    g.add((metadata, DCT.language, Literal("it")))  # Add dct:language "it"
    g.add((metadata, ELI.id_local, Literal("doc_" + str(json_obj['id']))))  # Add eli:id_local "id"
    g.add((metadata, ELI.jurisdictions, Literal("IT")))  # Add eli:jurisdictions "IT"
    g.add((metadata, ELI.first_date_entry_in_force, Literal("2001-01-01")))  # Add eli:first_date_entry_in_force "date" @todo
    
    # Add the text property
    text = json_obj['text']
    g.add((doc_uri, NIF.isString, Literal(text)))
    
    # Add the offset_ini and offset_end properties
    index = len(text)
    offset_ini = 0
    offset_end = index - 1
    g.add((doc_uri, NIF.beginIndex, Literal(offset_ini, datatype=XSD.nonNegativeInteger)))
    g.add((doc_uri, NIF.endIndex, Literal(offset_end, datatype=XSD.nonNegativeInteger)))

    # Add entity annotations
    entities = json_obj['entities']
    for entity in entities:
        entity_uri = URIRef(base_uri + "3988#offset_{}_{}".format(entity['start_offset'], entity['end_offset']))
        g.add((entity_uri, RDF.type, LKG.LynxAnnotation))
        g.add((entity_uri, RDF.type, NIF.OffsetBasedString))
        g.add((entity_uri, NIF.referenceContext, doc_uri))
        
        label = entity['label']
        # Add the label property as a nif:AnnotationUnit, itsrdf:taIdentRef
        g.add((entity_uri, RDF.type, NIF.AnnotationUnit))
        g.add((entity_uri, ITSRDF.taIdentRef, URIRef(label)))  # Corrected line
        g.add((entity_uri, LKG.label, Literal(label)))
        
        value = json_obj['text'][entity['start_offset']:entity['end_offset']]
        g.add((entity_uri, NIF.anchorOf, Literal(value)))
        g.add((entity_uri, NIF.beginIndex, Literal(entity['start_offset'], datatype=XSD.nonNegativeInteger)))
        g.add((entity_uri, NIF.endIndex, Literal(entity['end_offset'], datatype=XSD.nonNegativeInteger)))
        
    return g
