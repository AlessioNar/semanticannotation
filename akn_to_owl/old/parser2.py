import pandas as pd
from akn_to_owl.functions import extract_text


# Extracts the intro of a list. It returns the id of the intro
def get_intro(paragraph):
    elements = paragraph.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}list")
    if len(elements) > 0:        
        for element in elements:            
            intro = element.find(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}intro")
            if intro is not None:                
                #reference = get_insertions_and_references(intro)
                intro_id = intro.attrib['eId']
                #p_text = intro.find(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p")
                return intro_id
            else:   
                return None
            
    else:
        return None

# Extracts the points of a list. It returns a list of the ids of the points
def get_point(paragraph):
    elements = paragraph.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}list")    
    
    if len(elements) > 0:
        points = paragraph.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}point")
        
        if len(points) > 0:            
            point_ids = []            
            for point in points:
                point_id = point.attrib['eId']
                point_ids.append(point_id)
        
            return point_ids
    return None


def process_p(paragraph, article_id, paragraph_id, intro_id, points):
    # Create list of paragraphs
    p_list = []

    # Set up counters    
    p_counter = 0
    point_counter = 0

    # Iterate over paragraphs
    for p in paragraph.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):
        text = extract_text(p)
        if (text == '((') or (text == '))'):
            continue
        else:
            p_counter += 1
            # Gives the p element a unique id, which is the article id + the paragraph value + the p counter
            p_id = paragraph_id + '__p_' + str(p_counter)

                # Extract insertions and references
            insertions, references, ins_id, ref_id = get_insertions_and_references(p)
                    
            # If there is an intro, it is assigned to the first paragraph
            if points is not None:
                if p_counter != 1:
                    point_id = points[point_counter]
                    point_counter += 1
                else:
                    point_id = None                
            else:
                point_id = None
                    
            p_dict = {
                        'article_id': article_id,
                        'paragraph_id': paragraph_id,
                        'p_id': p_id,
                        "point_id": point_id,
                        "intro_id": intro_id,
                        'text': text,
                        'insertions': insertions,
                        'references': references,
                        'ref_id': ref_id,
                        'ins_id': ins_id
                    }
            p_list.append(p_dict)         
    
    return p_list


def split_art_para_p(df, first_column, second_column, name):
    # Create a copy of the DataFrame to avoid modifying the original
    splitted_df = df.copy()

    # Create a new column to store the modified values
    splitted_df[name] = ''

    # Iterate over the rows of the DataFrame
    for index, row in splitted_df.iterrows():
        paragraph_element = row[first_column]  # Get the value from the first column

        # Split the value by '__' and get a list of parts
        paragraph_parts = paragraph_element.split('__')
        paragraph_number = paragraph_parts[-1]  # Get the paragraph number from the last part

        # Modify the value in the second column based on the paragraph number
        p_element = row[second_column]
        p_parts = p_element.split('__')

        p_number = p_parts[-1]
        updated = p_parts[0] + '__' + paragraph_number + '__' + p_number


        # Update the value in the new column of the current row
        splitted_df.at[index, name] = updated

    return splitted_df

def transform_intro_points(df):
    
    # Update intro where intro is True and point_id is None
    df.loc[(df['intro_id'].notnull()) & (df['point_id'].isnull()), 'intro'] = True

    # Set false when intro is not True
    df.loc[df['intro'] != True, 'intro'] = False
    
    # When intro is False and intro_id is not null, set a new column called points to True
    df.loc[(df['intro'] != True) & (df['intro_id'].notnull()), 'point'] = True

    # Set false when points is not True
    df.loc[df['point'] != True, 'point'] = False
    
    
    # Remove intro_id suffix
    df.loc[df['intro_id'].notnull(), 'intro_id'] = df['intro_id'].str.replace('__intro_1', '')
    
    # Set intro_id to None when intro is True
    df.loc[df['intro'] == True, 'intro_id'] = None
    
    # Update point column
    #df['point'] = df['point_id']
    #df['point'] = df['point'].notnull()
    
    # Select desired columns
    df = df[['article_id', 'paragraph_id', 'p_id', 'original_id', "intro", 'intro_id', "point", 'point_id',  'text', 'insertions', 'references', 'ins_id', 'ref_id']]    
    
    return df