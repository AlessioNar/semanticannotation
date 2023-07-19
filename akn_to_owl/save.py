
def create_classes_and_properties():

    # Step 2: Prepare ontologies for loading in doccano
    #creation_classes, creation_properties = owltojson.ontojson('data/ttl/copyrightonto-creationmodel.ttl')
    #action_classes, action_properties = owltojson.ontojson('data/ttl/copyrightonto-actionsmodel.ttl')
    #right_classes, right_properties = owltojson.ontojson('data/ttl/copyrightonto-rightsmodel.ttl')
    #mediavaluechain_classes, mediavaluechain_properties = owltojson.ontojson('data/ttl/mediavaluechain.ttl')
    
    classes = {**creation_classes, **action_classes, **right_classes, **mediavaluechain_classes}
    properties = {**creation_properties, **action_properties, **right_properties, **mediavaluechain_properties}

    # Reset the ids
    for i, c in enumerate(classes.values()):
        c['suffix_key'] = str(i + 1)

    # Reset the ids
    for i, p in enumerate(properties.values()):
        p['suffix_key'] = str(i + 1)

    # Save the classes to a file as a list of dictionaries
    with open("data/json/classes.json", "w") as f:
        json.dump(list(classes.values()), f)

    with open("data/json/properties.json", "w") as f:
        json.dump(list(properties.values()), f)



import rdflib
from rdflib.util import guess_format
    
def save_ontology(prefix, ontology_uri, format = None):
    # Download the ontology
    try:
        r = requests.get(ontology_uri)
        print(f"Downloaded ontology from {ontology_uri}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the ontology: {e}")
        return
    
    # Guess the format if it is not provided
    if format == None:
        format = guess_format(r.content)

    print(f"Format: {format}")


    graph = rdflib.Graph()

    # Load the content into the graph
    try:
        graph.parse(data=r.content, format=format)
        print("Ontology parsed successfully.")
    except rdflib.parser.ParserError as e:
        print(f"Failed to parse the ontology: {e}")
        return
    
    # Get the prefix of the ontology
    try:
        prefix = graph.namespace_manager.compute_qname(ontology_uri)[0]
        print(f"Prefix: {prefix}")
    except Exception as e:
        print(f"Failed to get the prefix: {e}")
        return

    # Save the graph to a file
    try:
        destination = f"data/ttl/{prefix}.ttl"
        graph.serialize(destination=destination, format="turtle")
        print(f"Ontology saved as {destination}")
    except Exception as e:
        print(f"Failed to save the ontology: {e}")

    return
