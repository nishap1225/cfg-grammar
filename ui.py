import streamlit as st
from clients import generate_query, query_db

# Initialize clients only once using session state
@st.cache_resource
def initialize_clients():
    """Initialize clients once and cache them"""
    query_generator = generate_query.QueryGenerator(st.secrets["openai_token"])
    query_db_client = query_db.QueryDB(st.secrets["tinybird_token"])
    return query_generator, query_db_client

query_generator, query_db_client = initialize_clients()
print("HERE")
# Create a form to handle Enter key press
with st.form("query_form"):
    question = st.text_input("Ask about baby names in New York City")
    submitted = st.form_submit_button("Submit")

# Only process when form is submitted with input
if submitted and question and question.strip():
    with st.spinner("Processing your query..."):
        try:
            supporting_prompt = f"Generate a query for the Tinybird baby_names dataset for the following request: {question}. Do not impose any constraints beyond what is described in the request."
            query = query_generator.generate_query(supporting_prompt)
            data = query_db_client.query_db(query)
            
            # Display the results
            if data is not None and not data.empty:
                st.dataframe(data=data)
            else:
                st.warning("No data returned for your query.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

elif submitted and not question.strip():
    st.warning("Please enter a question before submitting.")