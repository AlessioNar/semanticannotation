import argparse
import json
import requests
import pandas as pd
from akn_to_owl import parser, owltojson, jsonltolynx
from akn_to_owl.skos import skos_to_json

    # Step 1: Parse XML data
    #parser.parse_xml('data/akn/19410716_041U0633_VIGENZA_20220922.xml', output_file='data/jsonl/copyright_law.jsonl')
"""	
    df = pd.read_csv('data/resources/ontology/ontologies.csv')

    for index, row in df.iterrows():        
        try:
            save_ontology(prefix = row['prefix'], ontology_uri=row['uri'], format = row['format'])
        except:
            print(row['uri'] + " not found")

    #create_classes_and_properties()
    # Step 4: Upload or send data to a web application through an API
    #functions.send_data(transformed_data, 'http://api.example.com')
    #jsonltolynx.convert_jsonl_to_lynx('data/jsonl/annotated/admin.jsonl', 'data/rdf/lynx.rdf', "http://lynx-project.eu/doc/samples/")

"""

def main():
    parser = argparse.ArgumentParser(description='Converts AKN data to OWL, then to JSON-L and finally to LYNX.')
    parser.add_argument('task', type=str, help='Task to perform, e.g., "skos"')
    args = parser.parse_args()

    if args.task == "skos":

        skos_to_json()

    else:
        print(f"Task {args.task} is not recognized.")
        exit(1)

    # You would need to provide more details about parser, owltojson, and jsonltolynx
    # for me to be able to include them here.


if __name__ == '__main__':
    main()