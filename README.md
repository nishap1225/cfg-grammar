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