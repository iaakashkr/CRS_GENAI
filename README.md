# CRS_GENAI (Natural Language to SQL Translation Engine)

CRS_GENAI is a modular, metadata-driven Natural Language to SQL (NL-to-SQL) translation engine. It is designed to interpret natural language questions about microfinance, loan, and financial metrics, generate accurate PostgreSQL queries matching the target database schema, execute them against a Supabase database, and return live structured results.

---

## 📂 Project Directory Structure

```text
CRS_GENAI/
├── app_new.py                      # Flask Application entrypoint
├── ask.py                          # CLI Developer Tool for quick querying
├── test_pipeline.py                # End-to-end pipeline test script
├── requirements.txt                # Third-party Python dependencies
├── .env                            # API Keys and database credentials (Git ignored)
├── LICENSE                         # Open-source MIT License
├── crs_tables.csv                  # Reference table metadata descriptions
├── crs_columns.csv                 # Reference column metadata descriptions & instructions
├── crs_joining_instructions.csv    # Pairwise table joining rules matrix
├── fewshot_example.csv             # Example questions and corresponding SQL queries
├── fewshots.yml                    # Secondary few-shot configuration
├── auth/                           # Authentication endpoints
│   └── routes.py                   # /login, /refresh, /logout handlers
├── query/                          # API Query routes
│   └── routes_new.py               # /user/query endpoint
├── pipeline/                       # Core NL-to-SQL Pipeline
│   ├── pipeline.py                 # Main Orchestrator (run_pipeline)
│   ├── modules/                    # Sub-modules for pipeline stages
│   │   ├── rephrase.py             # Entity normalizer & query rephraser
│   │   ├── intent.py               # LLM intent classification (table detection)
│   │   ├── columns.py              # LLM column filtering
│   │   ├── table_utils.py          # Table-level schema cleanup & fuzzy matching
│   │   ├── joining_instructions.py # CSV table join lookup
│   │   ├── fewshot_module.py       # FAISS + BM25 hybrid similarity search
│   │   ├── embedder.py             # Local embedding generation (SentenceTransformer)
│   │   ├── sql_generator.py        # PostgreSQL generation module
│   │   ├── validation.py           # Table/Column validating & quoting helper
│   │   ├── prompt_loader.py        # YAML prompt template loader
│   │   ├── load_references.py      # Reference metadata CSV loader
│   │   ├── token_counter.py        # Token counting helper
│   │   └── token_tracker.py        # Token tracking per transaction step
│   ├── prompts/                    # YAML-based LLM system & user prompts
│   │   ├── intent.yml              # Prompts for table/intent detection
│   │   ├── column.yml              # Prompts for column mapping
│   │   └── sql.yml                 # Prompts for SQL generation rules
│   └── utils/
│       └── cache_manager.py        # Memory cache for FAISS index & models
├── utils/                          # Cross-cutting system utilities
│   ├── audit.py                    # Master-Child CSV logging backend
│   ├── config.py                   # JWT secret and token lifetimes
│   ├── db.py                       # SQL execution test script
│   ├── db_cred.py                  # SQLAlchemy engine & session pool management
│   └── dto.py                      # PipelineDTO schema definition
├── audit_logs/                     # Execution audit files (Git ignored)
│   ├── monitor_master.csv          # High-level pipeline runs log
│   └── monitor_child.csv           # Stepwise timing and token statistics log
└── pickles/                        # Compiled models and cache files (Git ignored)
    └── sysntactic_model_few_shot.pkl # BM25 Syntactic index
```

---

## 🏗️ Architecture & Core Pipeline Flow

The engine uses a linear, DTO-centric design. A single `PipelineDTO` object carries the query state through subsequent modules:

```mermaid
graph TD
    Question[User Question] --> Rephrase[1. Rephrase & Expand]
    Rephrase --> Intent[2. Intent & Table Identification]
    Intent --> Columns[3. Column Identification]
    Columns --> Fuzzy[4. Fuzzy Correction]
    Fuzzy --> Joins[5. Join Instruction Lookup]
    Joins --> FewShot[6. Few-Shot Retrieval]
    FewShot --> SQLGen[7. SQL Generation]
    SQLGen --> SQLExec[8. SQL Execution]
    SQLExec --> Audit[9. Auditing & Logging]
    Audit --> Output[Final Output]
```

### Key Modules:
1. **Rephrase & Expand (`pipeline/modules/rephrase.py`)**: Normalizes month names, values, and normalizes acronyms.
2. **Intent & Table Identification (`pipeline/modules/intent.py`)**: Prompts Gemini with `crs_tables.csv` metadata to detect the relevant tables needed for the question.
3. **Column Identification (`pipeline/modules/columns.py`)**: Identifies column lists using the `crs_columns.csv` rules.
4. **Fuzzy Correction (`pipeline/modules/table_utils.py`)**: Uses `difflib.get_close_matches` to correct hallucinated table and column names back to valid database objects.
5. **Join Lookup (`pipeline/modules/joining_instructions.py`)**: Retrieves strict table join rules from a pre-defined joining matrix to prevent syntax errors during joins.
6. **Few-Shot Retrieval (`pipeline/modules/fewshot_module.py`)**: Computes cosine similarity of queries using HuggingFace `SentenceTransformer` (`all-MiniLM-L6-v2`) in a `FAISS` index, combined with a local `BM25` index for hybrid search.
7. **SQL Generation (`pipeline/modules/sql_generator.py`)**: Prompts Gemini with few-shot context to generate syntactically valid Postgres SQL.
8. **SQL Execution (`utils/db_cred.py`)**: Connects to the database and executes the query securely, parsing records into JSON.
9. **Auditing (`utils/audit.py`)**: Logs token usage, execution timings, generated SQL, and result stats.

---

## 🗄️ Database Schema Details

The database is structured under the `accessdetails` schema containing the following 9 tables:

1. `__genai_arrear_details` - Tracks overdue loan payments, PAR amounts, and days in arrears.
2. `__genai_branch_master` - Hierarchical metadata of branches (states, regions, zones).
3. `__genai_customer_details` - Customer activation, reactivation, and meeting schedules.
4. `__genai_fund` - Metadata of financing institutions (funder IDs and names).
5. `__genai_last_working_days` - Operational schedules and active working days per branch.
6. `__genai_loans_disbursement` - Loan disbursement amounts, interest rates, terms, and values dates.
7. `__genai_portfolio_outstanding` - Active loan portfolios and outstanding principal balances.
8. `__genai_preclosure` - Early preclosed loans, settlement amounts, and closure dates.
9. `__genai_recovery_details` - Principal/interest due vs. collected recovery tracking.

---

## ⚡ Setup & Usage

### 1. Installation & Environment Setup
Activate your Python/Conda environment and install the required dependencies:
```powershell
# Activate your conda environment
conda activate myenv

# Install requirements
pip install -r requirements.txt
```

### 2. Configuration (.env)
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY="your-gemini-api-key"
DATABASE_URL="postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres"
```

### 3. Running the CLI Developer Tool (ask.py)
To query the database directly in natural language from the command line:
```powershell
python ask.py "What is the outstanding portfolio for branch B001?"
```

### 4. Running the Flask API Server
To start the backend web server:
```powershell
python app_new.py
```
By default, the server runs on `http://127.0.0.1:5000/`.

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.
