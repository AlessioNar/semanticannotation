import argparse
from akn_to_owl.parser import AkomaNtosoParser
from akn_to_owl.skos import SKOSParser
from akn_to_owl.owl import OntologyParser
from akn_to_owl.lynx import LynxDocument

def main():
    parser = argparse.ArgumentParser(description='Converts AKN data to OWL, then to JSON-L and finally to LYNX.')
    parser.add_argument('task', type=str, help='Task to perform, e.g., "skos"')
    parser.add_argument('file', type=str, nargs='?', help='File to parse, e.g., "data/akn/20230331_23G00044_VIGENZA_20230530.xml"')
    args = parser.parse_args()
    
    
    if args.task == "akn":
        xml_file = 'data/akn/20230331_23G00044_VIGENZA_20230530.xml'
        parser = AkomaNtosoParser(xml_file)
        parser.export_jsonl('data/jsonl/origin/new.jsonl')
        

    elif args.task == "skos":
        # if there is another argument, use it as the file path
        file_name = args.file.split('.')[0]
        file_name = file_name.split('/')[-1]
        skos_parser = SKOSParser(args.file)
        # Get the name of the file without the extension
        top_classes = skos_parser.parse_skos()
        if top_classes:
            top_classes = SKOSParser.enrich_json(top_classes)
            SKOSParser.write_to_file(top_classes, 'data/span/'+ file_name +'.json')

    elif args.task == "owl":
        parser = OntologyParser(args.file)
        parser = parser.parse_owl()
        file_name = args.file.split('\\')[-1]
        file_name = file_name.split('.')[0]
        print(f'Writing to file: {file_name}')
        parser.write_to_file(file_name)
    
    elif args.task == "jsonl":
        # Then you can use the class like this:
        doc = LynxDocument("http://example.com/")
        doc.load_from_jsonl("data/jsonl/annotated/copyright.jsonl")
        doc.save_to_turtle("data/lynx/copyright.ttl")        
        
    else:
        print(f"Task {args.task} is not recognized.")
        exit(1)

if __name__ == '__main__':
    main()