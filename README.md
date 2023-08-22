# A semantic annotation pipeline for legislative documents

This repository contains code to convert Akoma Ntoso (AKN) documents into Web Ontology Language (OWL) format.

## Structure

- `main.py`: The main script that orchestrates the conversion process.
- `akn_to_owl/`: A folder containing the following modules:
  - `akn.py`: Handles the processing of AKN documents.
  - `lynx.py`: Contains functions related to the Lynx data format.
  - `metadata.py`: Manages metadata extraction and processing.
  - `owl.py`: Deals with OWL-related functionality.
  - `skos.py`: Provides functions for working with SKOS (Simple Knowledge Organization System) concepts.

## Dependencies

List any dependencies or prerequisites needed to run the code here.


## Usage

The script provides a command-line interface to convert AKN data to OWL, then to JSON-L, and finally to LYNX. The usage is as follows:

### Command-line Arguments

- `task`: The task to perform, e.g., "skos", "akn", "owl", "lynx".
- `file`: The file to parse (optional).
- `output`: The output file (optional).

### Example

To instantiate the Akoma Ntoso Parser for a specific file and output the result to a given location, you can use:

```bash

python main.py akn data/akn/20230331_23G00044_VIGENZA_20230530.xml data/jsonl/origin/copyright.jsonl

```

## License

This project is licensed under the MIT License, the same as Doccano. You can find the full text of the license in the [Doccano repository](https://github.com/doccano/doccano/blob/master/LICENSE) or in the LICENSE file.

## Contact

For any questions, concerns, or support related to this code, please visit [alessionardin.eu](https://www.alessionardin.eu) or use the contact information provided on the website.
