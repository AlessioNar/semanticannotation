# Create an empty list to store article dictionaries
article_list = []

# Call the recursive function for each article
for article in articles:
    article_id = article.attrib['eId']
    article_dict = {'article_id': article_id, 'text': [], 'insertions': [], 'references': [], 'ref_id': [], 'ins_id': []}
    #print(article_id, text)
    for element in article.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):
        text = extract_text(element)
        article_dict['text'].append(text)
    
            
    for element in article.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}ref'):
        ref_id = element.attrib['href']
        text = extract_text(element)
        article_dict['references'].append(text)
        article_dict['ref_id'].append(ref_id)
    article_list.append(article_dict)

# Create a dataframe from the list of dictionaries
df = pd.DataFrame(article_list)
df.head()

        
# Inside the article tag, there can be one or more paragraph tags
# I have some questions:

# Is there only text contained in the articl tag or is it present only inside paragraphs?
# Write a function that checks it using the xml elements stored in the articles list

# Create an empty list to store article dictionaries
article_list = []
paragraph_list = []

for article in articles:
    article_id = article.attrib['eId']    
    counter = 0
    for paragraph in article.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}paragraph'):    
        counter += 1
        # If there is an attribute eId, store it, othewise create it and store it
        if 'eId' in paragraph.attrib:
            paragraph_id = paragraph.attrib['eId']
            p_counter = 0
            for p in paragraph.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):
                p_counter += 1
                p_id = 'p__'+ str(p_counter)
                p_dict = {'p_id': p_id, 'paragraph_id': [], 'text': [], 'insertions': [], 'references': [], 'ref_id': [], 'ins_id': [], 'article_id': []} #, 'chapter_id': chapter_id}
                
                text = extract_text(p)
                p_dict['paragraph_id'].append(paragraph_id)
                p_dict['text'].append(text)

        else:
            paragraph_id = article_id + '__para_' + str(counter)
            for p in paragraph.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):
                p_counter += 1
                p_id = 'p__'+ str(p_counter)
                paragraph_dict = {'p_id': p_id,'paragraph_id': [], 'text': [], 'insertions': [], 'references': [], 'ref_id': [], 'ins_id': [], 'article_id': []} #, 'chapter_id': chapter_id}
                text = extract_text(p)                
                paragraph_dict['paragraph_id'].append(paragraph_id)
                paragraph_dict['text'].append(text)
                #paragraph_list.append(paragraph_dict)
        
        
   
        
                    
        
    print(paragraph_dict)


    article_list = []
paragraph_list = []

for article in articles:
    article_id = article.attrib['eId']
    counter = 0

    for paragraph in article.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}paragraph'):
        counter += 1

        if 'eId' in paragraph.attrib:
            paragraph_id = paragraph.attrib['eId']
        else:
            paragraph_id = article_id + '__para_' + str(counter)
        
        

        p_counter = 0
        for p in paragraph.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):
            p_counter += 1
            p_id = article_id + "__para_" + str(counter) + '__p_' + str(p_counter)
            
            # Insertions
            insertions = []
            ins_id = []
            for ins in p.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}ins'):
                ins_id.append(ins.attrib['eId'])
                text = extract_text(ins)
                insertions.append(text)
            
            # References
            references = []
            ref_id = []
            for ref in p.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}ref'):
                ref_id.append(ref.attrib['href'])
                text = extract_text(ref)
                references.append(text)

        # find all the elements with the tag {http://docs.oasis-open.org/legaldocml/ns/akn/3.0}list, if any 
        #lists = paragraph.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}list")
        #for list in lists:            
            intro = list.find(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}intro")
            ##if get_references(intro) != []:
            #intro_p = intro.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p")
            #for intro_test in intro_p:
            #    print(paragraph_id, intro_test.text)


            
            p_dict = {
                'p_id': p_id,
                'paragraph_id': paragraph_id,
                'text': extract_text(p),
                'insertions': insertions,
                'references': references,
                'ref_id': ref_id,
                'ins_id': ins_id,
                'article_id': article_id,
                "list": list,
                "intro" : True
            }
            paragraph_list.append(p_dict)

print(paragraph_list)

df = pd.DataFrame(paragraph_list)
df.head()


# Processes the articles got as a consequence of the extract_articles function
# And launches it to the next function, process_paragraph
# It returns a list of paragraphs with an unique id associated to the XML structure
# Of the AKN file
def extract_paragraphs(articles):
    paragraph_list = []

    
    for article in articles:
        article_id = article.attrib['eId']
        
        # Check how many paragraphs are in the article. 
        # If there is only one, then the id is para_1
        if len(article.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}paragraph")) == 1:
            
            # Assign the paragraph_id
            paragraph_id = "para_1"
            
            # Extract the paragraph
            paragraph = article.find(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}paragraph")
            
            # Verify whether the paragraph has a list tag inside
            if paragraph.find(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}list") is not None:
                p_counter = 0
                for p in paragraph.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):
                        
                    # Increase the counter
                    p_counter += 1
                    p_id = "p_" + str(p_counter)
                    p_text = extract_text(p)

                    # Add the values to the paragraph_list
                    paragraph_info = build_line(article_id, paragraph_id, p_id, p_text, True)                    
                    paragraph_list.append(paragraph_info)                        

                    continue
            
            # There is no list tag inside the paragraph
            else:

                # Check whether there are multiple p tags inside the paragraph
                if len(paragraph.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p")) == 1:
                    
                    # Assign the p_id
                    p_id = "p_1"
                    
                    # Extract the text
                    p_text = extract_text(paragraph.find(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p"))

                    # Add the values to the paragraph_list
                    paragraph_info = build_line(article_id, paragraph_id, p_id, p_text, False)                    
                    paragraph_list.append(paragraph_info)
                    
                    continue
                else:
                    p_counter = 0
                    for p in paragraph.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):
                        
                        # Increase the counter
                        p_counter += 1
                        p_id = "p_" + str(p_counter)
                        p_text = extract_text(p)

                        # Add the values to the paragraph_list
                        paragraph_info = build_line(article_id, paragraph_id, p_id, p_text, False)                    

                        paragraph_list.append(paragraph_info)
                        continue
                        
        # If there are multiple paragraphs, then loop through them
        else:
            # Loop through all the paragraphs
            # Set up a counter for the paragraphs
            paragraph_counter = 0
            for paragraph in article.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}paragraph'):
                
                # If the paragraph is empty or has only a double parenthesis, then continue with the next paragraph
                if extract_text(paragraph) == "((" or extract_text(paragraph) == "))":
                    # Continue with the next paragraph
                    continue
                
                # Increase the counter
                paragraph_counter += 1
                
                # If the paragraph has an eId, then use it
                if paragraph.get('eId') is not None:
                    
                    paragraph_id = paragraph.attrib['eId'].split('__')[1]
                                  
                
                    # if the paragraph has a list tag inside explore, then for sure there are multiple p tags inside
                    if paragraph.find(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}list") is not None:

                        p_counter = 0

                        for p in paragraph.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):                                
                            # Increase the counter
                            p_counter += 1
                            p_id = "p_" + str(p_counter)
                            p_text = extract_text(p)

                            # Add the values to the paragraph_list
                            paragraph_info = build_line(article_id, paragraph_id, p_id, p_text, True)                    
                            paragraph_list.append(paragraph_info)
                            continue
                    else:
                        # If there are exactly one p tag inside the paragraph, then use it
                        if len(paragraph.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p")) == 1:
                            p_id = "p_1"
                            p_text = extract_text(p)
                            # Add the values to the paragraph_list
                            paragraph_info = build_line(article_id, paragraph_id, p_id, p_text, False)                    
                            paragraph_list.append(paragraph_info)
                            continue
                        else:
                            p_counter = 0
                            for p in paragraph.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):
                                p_counter += 1
                                p_id = "p_" + str(p_counter)
                                p_text = extract_text(p)
                                # Add the values to the paragraph_list
                                paragraph_info = build_line(article_id, paragraph_id, p_id, p_text, False)
                                paragraph_list.append(paragraph_info)
                                continue
                # If the paragraph does not have an eId, then some elements needs to be verified
                else:                    
                    paragraph_counter += 1
                    paragraph_id = "para_" + str(paragraph_counter)

                    # If there are exactly one p tag inside the paragraph, then use it
                    if len(paragraph.findall(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p")) == 1:
                        p_id = "p_1"
                        p_text = extract_text(paragraph.find(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p"))

                        # Add the values to the paragraph_list
                        paragraph_info = build_line(article_id, paragraph_id, p_id, p_text, False)                    
                        paragraph_list.append(paragraph_info)
                        continue
                    else:
                        p_counter = 0
                        for p in paragraph.iter('{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}p'):
                            p_counter += 1
                            p_id = "p_" + str(p_counter)
                            p_text = extract_text(p)
                            
                            # Add the values to the paragraph_list
                            paragraph_info = build_line(article_id, paragraph_id, p_id, p_text, False)                    
                            paragraph_list.append(paragraph_info)
                            continue
            

    return paragraph_list

