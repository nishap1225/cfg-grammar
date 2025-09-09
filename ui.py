import streamlit as st
from clients import generate_query, query_db, evaluation
import pandas as pd


# Initialize clients only once
@st.cache_resource
def initialize_clients():
    """Initialize clients once and cache them"""
    query_generator = generate_query.QueryGenerator(st.secrets["openai_token"])
    query_db_client = query_db.QueryDB(st.secrets["tinybird_token"])
    evaluator = evaluation.CFGSQLEvaluator(query_generator, query_db_client)
    return query_generator, query_db_client, evaluator


query_generator, query_db_client, evaluator = initialize_clients()

st.title("Context-Free Grammar Playground")
tab1, tab2 = st.tabs(["Query Interface", "Model Evaluation"])

# Tab 1: Original query interface
with tab1:
    st.header("Popular Baby Names")

    # Display sample data
    st.subheader("Sample Data")
    st.write("Here's a preview of the baby names dataset:")

    # Get sample data from the database
    try:
        sample_query = "SELECT * FROM baby_names LIMIT 10 FORMAT CSVWithNames"
        sample_data = query_db_client.query_db(sample_query)
        if sample_data is not None and not sample_data.empty:
            st.dataframe(sample_data, width="content")
        else:
            st.info(
                "No sample data available. Please ensure the database is properly set up."
            )
    except Exception as e:
        st.warning(f"Could not load sample data: {str(e)}")

    # Create a form to handle Enter key press
    with st.form("query_form"):
        question = st.text_input(
            "Ask me about baby names!",
            placeholder="'What are the most popular names for girls in 2020?'",
        )
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
                    st.subheader("Results:")
                    st.dataframe(data=data)

                    # Also show the generated SQL
                    with st.expander("View Generated SQL"):
                        st.code(query, language="sql")
                else:
                    st.warning("No data returned for your query.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    elif submitted and not question.strip():
        st.warning("Please enter a question before submitting.")

# Tab 2: Evaluation section
with tab2:
    st.header("Model Evaluation")

    # Display test cases
    st.subheader("Test Cases")

    # Get test cases
    test_cases = evaluator.test_cases()

    # Display test cases
    test_case_data = []
    for i, case in enumerate(test_cases):
        test_case_data.append(
            {
                "Test #": i + 1,
                "Natural Language Query": case.natural_language,
                "Expected Columns": ", ".join(case.expected_columns),
                "Expected SQL": (
                    case.expected_sql[:100] + "..."
                    if len(case.expected_sql) > 100
                    else case.expected_sql
                ),
            }
        )

    test_cases_df = pd.DataFrame(test_case_data)
    st.dataframe(test_cases_df, width="stretch")

    # Evaluation button and results
    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("Run Evaluation", type="primary"):
            st.session_state.run_evaluation = True

    with col2:
        if st.button("Clear Results"):
            if "evaluation_results" in st.session_state:
                del st.session_state.evaluation_results
            if "run_evaluation" in st.session_state:
                del st.session_state.run_evaluation

    # Run evaluation if button was clicked
    if st.session_state.get("run_evaluation", False):
        with st.spinner("Running evaluation on all test cases..."):
            try:
                results = evaluator.run_evaluation(test_cases)
                st.session_state.evaluation_results = results
                st.session_state.run_evaluation = False
                st.rerun()
            except Exception as e:
                st.exception(e)
                st.error(f"Evaluation failed: {str(e)}")
                st.session_state.run_evaluation = False

    # Display evaluation results if available
    if "evaluation_results" in st.session_state:
        results = st.session_state.evaluation_results

        st.subheader("Evaluation Results")

        # Display metrics
        metrics = results["cfg_metrics"]
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Success Rate", f"{metrics['success_rate']:.1%}")
        with col2:
            st.metric("Schema Compliance", f"{metrics['schema_compliance_rate']:.1%}")
        with col3:
            st.metric("Data Accuracy", f"{metrics['accuracy_rate']:.1%}")

        # Detailed results
        st.subheader("Detailed Results")

        detailed_results = []
        for i, result in enumerate(results["cfg_results"]):
            detailed_results.append(
                {
                    "Test #": i + 1,
                    "Natural Language": result.test_case.natural_language,
                    "Success": "✅" if result.success else "❌",
                    "Schema Match": "✅" if result.schema_matches else "❌",
                    "Data Correct": "✅" if result.data_correct else "❌",
                    "Error": result.error_message if result.error_message else "None",
                }
            )

        detailed_df = pd.DataFrame(detailed_results)
        st.dataframe(detailed_df, width="stretch")

        # Show individual test results with expandable sections
        st.subheader("Individual Test Results")
        for i, result in enumerate(results["cfg_results"]):
            with st.expander(f"Test {i+1}: {result.test_case.natural_language}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Expected SQL:**")
                    st.code(result.test_case.expected_sql, language="sql")

                with col2:
                    st.write("**Generated SQL:**")
                    st.code(result.generated_sql, language="sql")

                if result.error_message:
                    st.error(f"Error: {result.error_message}")

                if (
                    result.actual_results is not None
                    and not result.actual_results.empty
                ):
                    st.write("**Actual Results:**")
                    st.dataframe(result.actual_results)

                if (
                    result.test_case.expected_data is not None
                    and not result.test_case.expected_data.empty
                ):
                    st.write("**Expected Results:**")
                    st.dataframe(result.test_case.expected_data)
