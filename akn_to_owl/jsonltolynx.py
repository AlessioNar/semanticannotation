import json
from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD

# Define the namespaces
LKG = Namespace("http://lkg.lynx-project.eu/def/")
ELI = Namespace("http://data.europa.eu/eli/ontology#")
NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
DCT = Namespace("http://purl.org/dc/terms/")
ITSRDF = Namespace("http://www.w3.org/2005/11/its/rdf#")

import json
from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD

# Define the namespaces
LKG = Namespace("http://lkg.lynx-project.eu/def/")
ELI = Namespace("http://data.europa.eu/eli/ontology#")
DCT = Namespace("http://purl.org/dc/terms/")
NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")

def convert_jsonl_to_lynx(jsonl_file, output_file, base_uri):
    # Create an RDF graph
    g = Graph()
    
    # Bind prefixes
    g.bind("eli", ELI)
    g.bind("dct", DCT)
    g.bind("nif", NIF)
    g.bind("lkg", LKG)
    
    with open(jsonl_file, 'r') as file:
        json_obj = json.load(file)
            
        # Create a LynxDocument URI
        doc_uri = json_obj['id']
        doc_uri = URIRef(base_uri + str(doc_uri).strip())        
        g.add((doc_uri, RDF.type, NIF.Context))
        g.add((doc_uri, RDF.type, LKG.LynxDocument))
        
        # Add the metadata
        metadata_uri = doc_uri + '#metadata'
        g.add((doc_uri, LKG.metadata, metadata_uri))

        # Add the text property
        text = json_obj['text']
        g.add((doc_uri, NIF.isString, Literal(text)))


        print(json_obj.keys())
        index = len(text)
        
        # Add the offset_ini and offset_end properties
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
            g.add((NIF.AnnotationUnit, ITSRDF.taIdentRef, URIRef(label)))

            g.add((entity_uri, LKG.label, Literal(label)))
            value = json_obj['text'][entity['start_offset']:entity['end_offset']]

            g.add((entity_uri, NIF.anchorOf, Literal(value)))
            g.add((entity_uri, NIF.beginIndex, Literal(entity['start_offset'], datatype=XSD.nonNegativeInteger)))
            g.add((entity_uri, NIF.endIndex, Literal(entity['end_offset'], datatype=XSD.nonNegativeInteger)))
            

        
        
    
    # Serialize the graph to Turtle and write to the output file
    g.serialize(destination=output_file, format='turtle')
