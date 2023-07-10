import pandas as pd

# Extract the text from an element, recursively
def extract_text(element):
    if element.text is not None:
        text = element.text.strip()
    else:
        text = ''

    for child in element:
        child_text = extract_text(child)
        text += ' ' + child_text.strip()

        if child.tail is not None:
            tail_text = child.tail.strip()
            if tail_text:
                text += ' ' + tail_text

    return text.strip()

# find all the articles from  the root of the xml file, going through all the xml file, recursively, with the following tag
# {http://docs.oasis-open.org/legaldocml/ns/akn/3.0}article
# and return a list of all the elements found
def extract_articles(root):
    articles = []
    for element in root.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}article'):
        articles.append(element)
    return articles

# In the xml tree, extract all the elements with the tag {http://docs.oasis-open.org/legaldocml/ns/akn/3.0}chapter, store their eId and heading
# Then navigate the tree to find all the elements with the tag {http://docs.oasis-open.org/legaldocml/ns/akn/3.0}article, and store their eId associated with the chapter eId in a dataframe
# It returns a dataframe with three columns: article_id, chapter_id, chapter_heading
def extract_chapters(tree):
    article_list = []

    # Extract chapters and articles
    chapters = tree.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}chapter")
    for chapter in chapters:
        chapter_eId = chapter.get('eId')
        heading = chapter.findtext(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}heading")
        articles = chapter.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}article")
        for article in articles:
            article_dict = {
                'article_id': article.get('eId'),
                'chapter_id': chapter_eId,
                'chapter_heading': heading
            }
            article_list.append(article_dict)

    # Create DataFrame
    df = pd.DataFrame(article_list)

    return df

# Extracts or assigns a paragraph id that can then be linked
# To the Akoma Ntoso XML file.
# The number of paragraph according to the counter has not legal value, 
# it is just a way to assign a unique id to each paragraph
def get_paragraph_id(paragraph, article_id, counter):
    if 'eId' in paragraph.attrib:
        return paragraph.attrib['eId']
    else:
        return article_id + '__para_' + str(counter)


# Extracts insertions and references from a paragraph
def get_insertions_and_references(p):
    insertions = []
    references = []
    ins_id = []
    ref_id = []

    for ins in p.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}ins'):
        ins_id.append(ins.attrib['eId'])
        text = extract_text(ins)
        insertions.append(text)

    for ref in p.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}ref'):
        ref_id.append(ref.attrib['href'])
        text = extract_text(ref)
        references.append(text)

    return insertions, references, ins_id, ref_id

# Processes the articles got as a consequence of the extract_articles function
# And launches it to the next function, process_paragraph
# It returns a list of paragraphs with an unique id associated to the XML structure
# Of the AKN file
def process_articles(articles):
    paragraph_list = []

    for article in articles:
        article_id = article.attrib['eId']
        counter = 0

        for paragraph in article.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}paragraph'):
            counter += 1
            paragraph_list.extend(process_paragraph(paragraph, article_id, counter))

    return paragraph_list


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
def get_points(paragraph):
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
        
# From the paragraph, the article id and the counter, it processes 
def process_paragraph(paragraph, article_id, counter):
    paragraph_id = get_paragraph_id(paragraph, article_id, counter)
    
    # Get intro and points of the paragraph
    intro_id = get_intro(paragraph)
    points = get_points(paragraph)
    paragraph_list = process_p(paragraph, article_id, paragraph_id, counter, intro_id, points)

    return paragraph_list

def process_p(paragraph, article_id, paragraph_id, counter, intro_id, points):
    # Create list of paragraphs
    p_list = []

    # Set up counters    
    p_counter = 0
    point_counter = 0

    # Iterate over paragraphs
    for p in paragraph.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):
        p_counter += 1
        # Gives the p element a unique id, which is the article id + the paragraph counter + the p counter
        p_id = article_id + "__para_" + str(counter) + '__p_' + str(p_counter)

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
            'text': extract_text(p),
            'insertions': insertions,
            'references': references,
            'ref_id': ref_id,
            'ins_id': ins_id
        }

        p_list.append(p_dict)

    return p_list


def fill_column(df, first_column, second_column, name):
    # Create a copy of the DataFrame to avoid modifying the original
    filled_df = df.copy()

    # Create a new column to store the modified values
    filled_df[name] = ''

    # Iterate over the rows of the DataFrame
    for index, row in filled_df.iterrows():
        first_value = row[first_column]  # Get the value from the first column

        # Split the value by '__' and get a list of parts
        paragraph_parts = first_value.split('__')
        paragraph_number = paragraph_parts[-1]  # Get the paragraph number from the last part

        # Modify the value in the second column based on the paragraph number
        second_value = row[second_column]
        p_parts = second_value.split('__')
        p_number = p_parts[-1]
        
        new_value = p_parts[0] + '__' + paragraph_number + '__' + p_number


        # Update the value in the new column of the current row
        filled_df.at[index, name] = new_value

    return filled_df

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
    df = df[['article_id', 'paragraph_id', 'p_id', "intro", 'intro_id', "point", 'point_id', 'xml_id', 'text', 'insertions', 'references', 'ins_id', 'ref_id']]    
    
    return df