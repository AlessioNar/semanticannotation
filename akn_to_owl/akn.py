import xml.etree.ElementTree as ET
import pandas as pd
import json

class AkomaNtosoParser:
    
    def __init__(self, xml_file):        
        
        root = ET.parse(xml_file).getroot()

        self.chapters = self.extract_chapters(root)        
        self.articles = self.extract_articles(root)
        self.paragraphs = self.extract_paragraphs(self.articles)
        self.df = pd.DataFrame(self.paragraphs)   
        self.df = self.create_dataframe(self.df, self.chapters)     
        
        return None
    

    def extract_chapters(self, tree):
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
        chapters_df = pd.DataFrame(article_list)

        return chapters_df

    def extract_articles(self, root):
        articles = []
        for element in root.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}article'):
            articles.append(element)
            
        return articles

    def extract_paragraphs(self, articles):
        paragraph_list = pd.DataFrame(columns=['article_id', 'paragraph_id', 'p_id', 'text', 'insertions', 'references'])
        
        for article in articles:
            article_id = article.attrib['eId']
            
            # Check how many paragraphs are in the article.
            # If there is only one, then the id is para_1
            if len(article.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}paragraph")) == 1:
                # Assign the paragraph_id
                paragraph_id = "para_1"
                # Extract the paragraph
                paragraph = article.find(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}paragraph")
                p_list = self.extract_p(article_id, paragraph_id, paragraph)
                # Convert the list to a dataframe
                p_list = pd.DataFrame(p_list, columns=['article_id', 'paragraph_id', 'p_id', 'text', 'insertions', 'references'])
                # Append the dataframe to the paragraph_list
                paragraph_list = pd.concat([paragraph_list, p_list], ignore_index=True)
                
            else:
                # Loop through all the paragraphs
                paragraph_counter = 0
                for paragraph in article.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}paragraph'):
                    # If the paragraph is empty or has only a double parenthesis, then continue with the next paragraph
                    if self.extract_text(paragraph) == "((" or self.extract_text(paragraph) == "))":
                        continue
                    
                    if paragraph.get('eId') is not None:
                        paragraph_id = paragraph.attrib['eId'].split('__')[1]
                    else:
                        # Increase the counter
                        paragraph_counter += 1
                        # Assign the paragraph_id
                        paragraph_id = "para_" + str(paragraph_counter)
                    
                    p_list = self.extract_p(article_id, paragraph_id, paragraph)
                    # Convert the list to a dataframe
                    p_list = pd.DataFrame(p_list, columns=['article_id', 'paragraph_id', 'p_id', 'text', 'insertions', 'references'])
                    # Append the dataframe to the paragraph_list
                    paragraph_list = pd.concat([paragraph_list, p_list], ignore_index=True)

        return paragraph_list

    def extract_p(self, article_id, paragraph_id, paragraph):
        p_list = []
        elements = paragraph.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p")
        for index, element in enumerate(elements):
            # Assign the p_id
            p_id = "p_" + str(index + 1)
            p_text = self.extract_text(element)
            insertions = self.get_insertions(element)
            references = self.get_references(element)
            p_info = self.build_line(article_id, paragraph_id, p_id, p_text, insertions, references)
            p_list.append(p_info)
        
        return p_list 
    
    def build_line(self, article_id, paragraph_id, p_id, p_text, insertions, references):
        line = {
            'article_id': article_id,
            'paragraph_id': paragraph_id,
            'p_id': p_id,
            'text': p_text,
            'insertions': insertions,
            'references': references,
            # 'list': list
        }
        return line 
    
    def export_jsonl(self, path):
        # Convert each row of the dataframe to a dictionary
        dict = self.df.to_dict('records')    
            
        # For every element in the list, print as a row in the json file
        with open(path, 'w') as outfile:
            for entry in dict:
                json.dump(entry, outfile)
                outfile.write('\n')
    

    # Extract the text from an element, recursively
    def extract_text(self, element):
        if element.text is not None:
            text = element.text.strip()
        else:
            text = ''

        for child in element:
            child_text = self.extract_text(child)
            text += ' ' + child_text.strip()

            if child.tail is not None:
                tail_text = child.tail.strip()
                if tail_text:
                    text += ' ' + tail_text

        
        return text.strip()
    
        
    def get_references(self, paragraph):
        references = []
        for reference in paragraph.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}ref"):        
            reference_id = reference.attrib['eId']
            reference_link = reference.attrib['href']
            reference_text = self.extract_text(reference)

            # Add the reference to the list
            references.append((reference_id, reference_link, reference_text))
        return references

            

    def get_insertions(self, paragraph):
        insertions = []
        for insertion in paragraph.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}ins"):
            insertion_id = insertion.attrib['eId']
            insertion_text = self.extract_text(insertion)
            insertions.append((insertion_id, insertion_text))
        return insertions

    def create_dataframe(self, df, chapters):
        # merge the chapter and df dataframes based on the article_id
        
        df = pd.merge(df, chapters, on='article_id', how='left')
        
        # order the columns
        df = df[['chapter_id', 'chapter_heading', 'article_id', 'paragraph_id', 'p_id', 'text', 'insertions', 'references']]

        df.to_csv('data/csv/copyright_law.csv', index=False)

        return df


def extract_sentences(df):


    # Splitting the text column based on the newline character
    df['sentence'] = df['text'].str.split('\n')

    # For every element in the list, remove the blank spaces at the beginning and at the end
    df['sentence'] = df['sentence'].apply(lambda x: [item.strip() for item in x])

    # For every element in the list, remove the empty elements
    df['sentence'] = df['sentence'].apply(lambda x: [item for item in x if item is not None and item != ''])

    # Create a new column with an index for each element in the list of parts
    df['s_id'] = df['sentence'].apply(lambda x: list(range(1, len(x)+1)))

    # check whether the parts_index column is equal to the length of the parts column and if not, print the article_id, paragraph_id and p_id
    df[df['s_id'].apply(lambda x: len(x)) != df['sentence'].apply(lambda x: len(x))][['article_id', 'paragraph_id', 'p_id']]

    # Nice. There are no differences between the length of the s_id column and the length of the sentence column
    # Delete the s_id column
    df = df.drop(columns=['s_id'])

    # Explode the dataframe based on the sentence column
    df = df.explode('sentence')

    # Group the dataframe by article_id, paragraph_id and p_id and then create a new column with the index of each sentence
    df['s_id'] = df.groupby(['article_id', 'paragraph_id', 'p_id']).cumcount() + 1

    # Make the s_id column a string and add the prefix 's_'
    df['s_id'] = 's_' + df['s_id'].astype(str)

    # Reorder the columns, now the text column is not needed anymore
    df = df[['chapter_id', 'chapter_heading', 'article_id', 'paragraph_id', 'p_id', 's_id', 'sentence', 'insertions', 'references']]

    df.to_csv('data/csv/sentence_level.csv', index=False)

    return df


def save_separate_chapters(df):
    # Loop through the dataframe based on the chapter_id and save each chapter as a separate file
    for chapter_id in df['chapter_id'].unique():
        # Create a dataframe with only the rows for the current chapter_id
        df_chapter = df[df['chapter_id'] == chapter_id]
        
        # Save the dataframe as a csv file
        df_chapter.to_csv('data/csv/chapters/' + chapter_id + '.csv', index=False)
        
        # Save the dataframe as a csv file





