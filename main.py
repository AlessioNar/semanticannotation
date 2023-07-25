import argparse
from akn_to_owl.akn import AkomaNtosoParser
from akn_to_owl.skos import SKOSParser
from akn_to_owl.owl import OntologyParser
from akn_to_owl.lynx import LynxDocument

def main():
    parser = argparse.ArgumentParser(description='Converts AKN data to OWL, then to JSON-L and finally to LYNX.')
    parser.add_argument('task', type=str, help='Task to perform, e.g., "skos"')
    parser.add_argument('file', type=str, nargs='?', help='File to parse, e.g., "data/akn/20230331_23G00044_VIGENZA_20230530.xml"')
    parser.add_argument('output', type=str, nargs='?', help='Output file, e.g., "data/jsonl/origin/copyright.jsonl"')
    args = parser.parse_args()
    
    
    if args.task == "akn":        
        parser = AkomaNtosoParser(args.file)
        parser.export_jsonl(args.output)
        

    elif args.task == "skos":
        # if there is another argument, use it as the file path
        print(f'Parsing skos file: {file_name}')
        file_name = args.file.split('.')[0]
        file_name = file_name.split('/')[-1]
        skos_parser = SKOSParser(args.file)

        # Get the name of the file without the extension
        top_classes = skos_parser.parse_skos()
        print(f'Writing to file: {file_name}')
        if top_classes:
            top_classes = SKOSParser.enrich_json(top_classes)
            SKOSParser.write_to_file(top_classes, 'data/span/'+ file_name +'.json')

    elif args.task == "owl":
        print(f'Parsing owl file: {args.file}')
        parser = OntologyParser(args.file)
        parser = parser.parse_owl()
        file_name = args.file.split('\\')[-1]
        file_name = file_name.split('.')[0]
        print(f'Writing to file: {file_name}')
        parser.write_to_file(file_name)
    
    elif args.task == "jsonl":
        
        print(f'Creating LynxDocument')
        doc = LynxDocument("http://example.com/")
        print(f'Parsing jsonl file: {args.file}')
        doc.load_from_jsonl("data/jsonl/annotated/copyright.jsonl")
        print(f'Writing to file: {args.output}')
        doc.save_to_turtle(args.output)        
        
    else:
        print(f"Task {args.task} is not recognized.")
        exit(1)

if __name__ == '__main__':
    main()