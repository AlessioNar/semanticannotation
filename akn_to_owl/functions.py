import pandas as pd

import xml.etree.ElementTree as ET


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

def get_parent(element):
    # Iterate over ancestors until finding the parent element
    for ancestor in element.iterancestors():
        if ancestor.tag == "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}article":
            return ancestor
    return None


import pandas as pd

def create_dataframe():
    # Define an empty dataframe with the desired columns
    df = pd.DataFrame(columns=['chapter_id', 'article_id', 'paragraph_id', 'text', 'insertions', 'references', 'ins_id', 'ref_id', 'intro_point', 'intro_point_id', 'intro_point_text'])

    for chapter in data['chapter']:
        chapter_id = chapter['@eId']
        for article in chapter['article']:
            if type(article) == dict:
                article_id = article['@eId']
                for paragraph in article['paragraph']:
                    if type(paragraph) == dict:
                        if '@eId' in paragraph.keys():
                            paragraph_id = paragraph['@eId']
                            if 'content' in paragraph.keys():
                                content = paragraph['content']
                                p = content['p']
                                for element in p:
                                    if type(element) == str:
                                        text = element
                                    else:
                                        if 'ins' in element.keys():
                                            ins = element['ins']
                                            for elem in ins:
                                                # Extract the necessary values and append a new row to the dataframe
                                                ins_id = elem['@eId']
                                                insertions = elem['$']
                                                df = df.append({'chapter_id': chapter_id, 'article_id': article_id, 'paragraph_id': paragraph_id, 'text': text, 'insertions': insertions, 'references': None, 'ins_id': ins_id, 'ref_id': None, 'intro_point': None, 'intro_point_id': None, 'intro_point_text': None}, ignore_index=True)
                                        elif 'ref' in element.keys():
                                            ref = element['ref']
                                            for elem in ref:
                                                # Extract the necessary values and append a new row to the dataframe
                                                ref_id = elem['@eId']
                                                references = elem['$']
                                                intro_point = elem['@href']
                                                intro_point_id = intro_point.split('#')[-1]
                                                intro_point_text = elem['#text']
                                                df = df.append({'chapter_id': chapter_id, 'article_id': article_id, 'paragraph_id': paragraph_id, 'text': text, 'insertions': None, 'references': references, 'ins_id': None, 'ref_id': ref_id, 'intro_point': intro_point, 'intro_point_id': intro_point_id, 'intro_point_text': intro_point_text}, ignore_index=True)
                                        break
                            else:
                                content = paragraph['content']
                                p = content['p']
                                if type(p) == list and len(p) == 1 and (p[0] == '((' or p[0] == '))'):
                                    pass
                                else:
                                    # Extract the necessary values and append a new row to the dataframe
                                    text = p
                                    df = df.append({'chapter_id': chapter_id, 'article_id': article_id, 'paragraph_id': paragraph_id, 'text': text, 'insertions': None, 'references': None, 'ins_id': None, 'ref_id': None, 'intro_point': None, 'intro_point_id': None, 'intro_point_text': None}, ignore_index=True)
    return df