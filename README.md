# CRS_GENAI

CRS_GENAI is a lightweight, modular data query pipeline that converts user questions into SQL queries, executes them on a database, and returns the results. It is designed for quick metric extraction with few-shot LLM assistance, without dynamic segments or insights.

---

## 🚀 How It Works_

The pipeline is linear, simple, and easy to follow. Here’s the step-by-step workflow:

1. **User Input**
   - The user types a question, e.g.,  
     `"Portfolio outstanding for branch IN0010097?"`

2. **Clean and Understand the Question**
   - **Rephrase**: Normalizes the question using `rephrase_question`.
   - **Add Keywords**: Ensures important terms are included.
   - Keywords are deduplicated for clarity.

3. **Pick What Data You Need**
   - **Identify Tables**: Uses `identify_intent` to select relevant tables.
   - **Identify Columns**: Uses `identify_columns` to find required columns.
   - Columns and keywords are added to the pipeline DTO.

4. **Fix Table Names**
   - **Correct Typos**: Uses `correct_tables` to fix any table name errors.
   - Only tables that exist in the reference metadata are kept.

5. **Validate Tables and Columns**
   - Ensures that all selected tables and columns are valid and consistent with the database reference.

6. **Build SQL**
   - **Join Instructions**: Determines how tables should be joined using `get_joining_instructions`.
   - **SQL Generation**: Uses `generate_sql_from_dto` with LLM + few-shot resources (FAISS, BM25, embeddings) to create the SQL query.

7. **Run SQL**
   - Executes the generated SQL using `execute_sql`.
   - Stores the response in the DTO.

8. **Return Results**
   - Converts the DTO to a dictionary and returns it to the user/UI.
   - Logs all steps for auditing (`save_master_record`, `save_child_records`).
---
## 📦 Key Features

- **Linear and Modular**: Easy-to-follow steps from user question → SQL → results.
- **Few-Shot LLM Assistance**: SQL generation uses previous examples for better accuracy.
- **Validation & Fuzzy Correction**: Ensures table and column names are correct.
- **Auditing**: Logs every step including tokens, execution time, and results.
- **DTO-Centric**: All metadata, tables, columns, SQL, and results are stored in a single `PipelineDTO` object.

---

## 🧠 Memory Hack / Visual Metaphor

Think of the pipeline like **ordering a pizza**:

1. You ask for a pizza → **User Question**
2. Chef clarifies your order → **Rephrase Question + Add Keywords**
3. Chef picks ingredients from pantry → **Select Tables & Columns**
4. Pantry labels are corrected → **Correct Table Names**
5. Chef checks ingredient freshness → **Validate Tables & Columns**
6. Chef prepares the pizza → **Generate SQL + Join Instructions**
7. Chef bakes it → **Execute SQL**
8. Pizza is served → **Return Results + Audit**

---

## ⚡ Setup & Usage

### 1. Installation & Environment Setup
Ensure you have Conda installed, then set up the environment:
```powershell
# Activate the conda environment
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
python ask.py "What is the overdue amount per branch?"
```

### 4. Running the Flask API Server
To start the backend web server:
```powershell
python app_new.py
```
By default, the server runs on `http://127.0.0.1:5000/`.

* **To Login (Retrieve JWT Token)**: Send a `POST` request to `http://127.0.0.1:5000/auth/login` with body:
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
* **To Query via API**: Send a `POST` request to `http://127.0.0.1:5000/user/query` with your JWT Bearer token and body:
  ```json
  {
    "question": "Portfolio outstanding for branch B001?"
  }
  ```

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.
