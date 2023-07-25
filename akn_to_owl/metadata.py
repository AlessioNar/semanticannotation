import json

def get_metadata(origin, annotated):
    origin_data = []
    annotated_data = []

    # Read origin jsonl file
    with open(origin, 'r') as file:
        for line in file:
            json_obj = json.loads(line)
            origin_data.append(json_obj)
    
    with open(annotated, 'r') as file:
        for line in file:
            json_obj = json.loads(line)
            annotated_data.append(json_obj)
    print(f"Origin data: {len(origin_data)}")    
    print(f"Annotated data: {len(annotated_data)}")

    # Merge the annotated data with the origin data
    for origin_obj in origin_data:
        #print(f"Searching for match: {origin_obj['paragraph_id']} - {origin_obj['text']}")
        for annotated_obj in annotated_data:
            if annotated_obj['text'] == origin_obj['text']:                
                # Add the metadata
                annotated_obj['paragraph_id'] = origin_obj['paragraph_id']
                annotated_obj['article_id'] = origin_obj['article_id']
                annotated_obj['chapter_id'] = origin_obj['chapter_id']
    
    return annotated_data
