from akn_to_owl import parser, owltojson
import json 

def main():
    # Step 1: Parse XML data
    #parser.parse_xml('data/akn/19410716_041U0633_VIGENZA_20220922.xml', output_file='data/jsonl/copyright_law.jsonl')

    # Step 2: Prepare ontologies for loading in doccano
    creation_classes, creation_properties = owltojson.ontojson('data/ttl/copyrightonto-creationmodel.ttl')
    action_classes, action_properties = owltojson.ontojson('data/ttl/copyrightonto-actionsmodel.ttl')
    right_classes, right_properties = owltojson.ontojson('data/ttl/copyrightonto-rightsmodel.ttl')

    
    classes = {**creation_classes, **action_classes, **right_classes}
    properties = {**creation_properties, **action_properties, **right_properties}

    # Reset the suffix keys and reassign them a letter from a to z
    for i, class_name in enumerate(classes):
        classes[class_name]["suffix_key"] = chr(97 + i % 26) * (i // 26 + 1)
    

    # Save the classes to a file as a list of dictionaries
    with open("data/json/classes.json", "w") as f:
        json.dump(list(classes.values()), f)

    with open("data/json/properties.json", "w") as f:
        json.dump(list(properties.values()), f)


    #owltojson.ontojson('data/ttl/cdm.ttl')


    # Step 4: Upload or send data to a web application through an API
    #functions.send_data(transformed_data, 'http://api.example.com')

if __name__ == '__main__':
    main()
