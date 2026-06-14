from db_cred import execute_sql

# Example SQL query generated from your pipeline
sql_query = '''-- Check if column exists
SELECT column_name
FROM information_schema.columns
WHERE table_name = '__genai_loans_disbursement_1756049896399611_1756121654'
  AND column_name ILIKE '%product%';
'''

# Execute and get results as a list of dictionaries
result_rows = execute_sql(sql_query)

# Print results
for row in result_rows:
    print(row)

