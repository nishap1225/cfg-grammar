# Context Free Grammars + Eval Toy

A project that demonstrates the use of Context Free Grammars with OpenAI GPT-5 for natural language to SQL query generation, featuring a Streamlit UI and Tinybird data backend.

## Architecture

### 1. User Interface
- **Technology**: [Streamlit](https://docs.streamlit.io/)
- **Deployment**: Automatically deploys on merge when `ui.py` is modified

### 2. Data Backend
- **Technology**: [Tinybird](https://www.tinybird.co/docs/forward/get-started/quick-start)
- **Location**: `tinybird/**` directory
- **Deployment**: Manual deployment via CLI
- **Data Management**: Add new data through CLI or API
- **Fixtures**: Complete database available under `fixtures/` directory

## Core Components

### 3. Query Generation (`clients/generate_query.py`)
- Uses OpenAI GPT-5 with [Context Free Grammars](https://cookbook.openai.com/examples/gpt-5/gpt-5_new_params_and_tools#3-contextfree-grammar-cfg) to generate SQL queries
- Grammar optimized for `baby_names` database and ClickHouse SQL syntax
- Most functionality available, with some complex SQL syntax limitations

### 4. Database Querying (`clients/query_db.py`)
- Handles querying the Tinybird database

### 5. Model Evaluation (`clients/evaluation.py`)
- Benchmarks model performance on 5 natural language queries
- Validation includes:
  - Query syntax correctness
  - Minimum required columns
  - Minimum required data 

## Local Model Evaluation

To run model evaluation locally, please follow these steps:

1. **Python Version**  
   - Ensure you are using **Python 3.10 or higher**.

2. **Install Dependencies**  
   - Install all required dependencies by running:
     ```
     pip install -r requirements.txt
     ```

3. **Set Required Environment Variables**  
   You must provide two tokens as environment variables before running the evaluation:

   - **OpenAI API Token**  
     - Set your OpenAI API token as an environment variable named `OPENAI_API_TOKEN`.
     - This token is required for generating SQL queries using GPT-5.

   - **Tinybird JWT Token**  
     - Set your Tinybird JWT token as an environment variable named `TINYBIRD_JWT_TOKEN`.
     - You can generate a JWT by going to the "JWT Generator" tab in the Streamlit UI and clicking the button to generate one.

4. **Run the Evaluation Script**  
   - Once your environment variables are set and dependencies installed, run the local evaluation by executing:
     ```
     python local_evaluation.py
     ```

**Note:**  
Both environment variables (`OPENAI_API_TOKEN` and `TINYBIRD_JWT_TOKEN`) are required for the evaluation to work.  
If you encounter authentication errors, double-check that your environment variables are set correctly, your tokens are valid, and you have installed all required dependencies with the correct Python version.
