import argparse
from akn_to_owl.parser import AkomaNtosoParser
from akn_to_owl.skos import skos_to_json
from akn_to_owl.owl import owl_to_json

def main():
    parser = argparse.ArgumentParser(description='Converts AKN data to OWL, then to JSON-L and finally to LYNX.')
    parser.add_argument('task', type=str, help='Task to perform, e.g., "skos"')
    args = parser.parse_args()
    
    if args.task == "akn":
        xml_file = 'data/akn/20230331_23G00044_VIGENZA_20230530.xml'
        parser = AkomaNtosoParser(xml_file)
        parser.export_jsonl('data/jsonl/origin/new.jsonl')
        

    elif args.task == "skos":
        skos_to_json()

    elif args.task == "owl":
        owl_to_json('data/ttl/copyrightonto-actionsmodel.ttl')

    else:
        print(f"Task {args.task} is not recognized.")
        exit(1)

if __name__ == '__main__':
    main()