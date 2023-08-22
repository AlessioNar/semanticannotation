import argparse
from akn_to_owl.akn import AkomaNtosoParser
from akn_to_owl.skos import SKOSParser
from akn_to_owl.owl import OntologyParser
from akn_to_owl.lynx import LynxDocument
from akn_to_owl.metadata import get_metadata

def parse_akn(args):
    print(f'Instantiating AkomaNtosoParser for file: {args.file}')        
    parser = AkomaNtosoParser(args.file)
    print(f'Parsing {args.file} to JSONL in {args.output}')
    parser.export_jsonl(args.output)

def parse_skos(args):
    file_name = args.file.split('.')[0].split('/')[-1]
    print(f'Parsing skos file: {file_name}')
    skos_parser = SKOSParser(args.file)
    top_classes = skos_parser.parse_skos()
    print(f'Writing to file: {file_name}')
    if top_classes:
        top_classes = SKOSParser.enrich_json(top_classes)
        SKOSParser.write_to_file(top_classes, 'data/span/'+ file_name +'.json')

def parse_owl(args):
    print(f'Parsing owl file: {args.file}')
    parser = OntologyParser(args.file)
    parser = parser.parse_owl()
    file_name = args.file.split('\\')[-1].split('.')[0]
    print(f'Writing to file: {file_name}')
    parser.write_to_file(file_name)

def transform_to_lynx(args):
    metadata = get_metadata('data/jsonl/origin/paragraph.jsonl', args.file)
    print(f'Creating LynxDocument')
    doc = LynxDocument("http://italian-copyright.it/")
    print(f'Parsing jsonl file: {args.file}')
    doc.load_from_jsonl(metadata)
    print(f'Writing to file: {args.output}')
    doc.save_to_turtle(args.output)

def main():
    parser = argparse.ArgumentParser(description='Converts AKN data to OWL, then to JSON-L and finally to LYNX.')
    parser.add_argument('task', type=str, help='Task to perform, e.g., "skos"')
    parser.add_argument('file', type=str, nargs='?', help='File to parse, e.g., "data/akn/20230331_23G00044_VIGENZA_20230530.xml"')
    parser.add_argument('output', type=str, nargs='?', help='Output file, e.g., "data/jsonl/origin/copyright.jsonl"')
    args = parser.parse_args()
    
    task_map = {
        "akn": parse_akn,
        "skos": parse_skos,
        "owl": parse_owl,
        "lynx": transform_to_lynx
    }
    
    task_function = task_map.get(args.task)
    
    if task_function:
        task_function(args)
    else:
        print(f"Task {args.task} is not recognized.")
        exit(1)

if __name__ == '__main__':
    main()
