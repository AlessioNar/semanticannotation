
# Check that for every combination of article_id, paragraph_id and p_id there is only one text
df.groupby(['article_id', 'paragraph_id', 'p_id']).count().sort_values(by='text', ascending=False).head(50)

# Print the text of all the lines with duplicates for article_id, paragraph_id and p_id
df[df.duplicated(subset=['article_id', 'paragraph_id', 'p_id'], keep=False)].sort_values(by=['article_id', 'paragraph_id', 'p_id'])

# @TODO: Duplicate lines are due to the fact that there are bis, ter, quater, etc. notations in the paragraph_id and this is not taken into account in the code above
# @TODO: As there are only 4 cases, a quick fix is to manually change the paragraph_id for them, but a better solution would be to take this into account in the code above


import os

def list_folder_content(path):
    for root, dirs, files in os.walk(path):
        for directory in dirs:
            print("Directory:", os.path.join(root, directory))
        for file in files:
            print("File:", os.path.join(root, file))
