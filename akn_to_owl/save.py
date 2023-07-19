
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