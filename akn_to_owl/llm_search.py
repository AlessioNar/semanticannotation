
def ingest_ontology():

    query = """Load the following ontology. The ontology contains the following classes and properties. The classes are: {classes}. The properties are: {properties}. The instances are: {instances}.
    Do not generate an output."""

    query = query.format(
        classes=", ".join(ontology_information["classes"]),
        properties=", ".join(ontology_information["properties"]),
        instances=", ".join(ontology_information["instances"]),

    )

    # Load into LLM and launch the prompt
    response = promptLLM(query)

    print("Ontology loaded.")

# get user query:
def get_user_query():
    user_query = st.text_input("Enter your query here:", "Can you provide me all the references to work in copyright legislation?")
    
    return user_query

def map_to_ontology(user_query):
    # Map the user query to the ontology
    prompt = ("Map the following user query to the ontology: '{user_query}'\n\n")
    response = promptLLM(prompt)

    print("User query mapped to ontology.")

    return response

