# def execute_sql(sql):
#     # Placeholder DB execution
#     return [{"total_disbursement_amount": 123456}]

from db_cred import execute_sql

# Example SQL query generated from your pipeline
sql_query = '''SELECT
  bm."branch_name",
  COUNT(ld."amount") AS disbursement_count,
  SUM(ld."amount") AS disbursement_amount
FROM
  "accessdetails"."__genai_branch_master_1756049768773113_1756052942850" bm
JOIN
  "accessdetails"."__genai_loans_disbursement_1756049896399611_1756121654" ld
  ON bm."branch_id" = ld."branch_id"
WHERE
  UPPER(bm."branch_name") LIKE UPPER('%%mysore%%')
  AND CAST(ld."ln_value_date" AS timestamp) >= DATE_TRUNC('month', NOW()) - INTERVAL '1 month'
  AND CAST(ld."ln_value_date" AS timestamp) < DATE_TRUNC('month', NOW())
GROUP BY
  bm."branch_name"
ORDER BY
  bm."branch_name"
LIMIT 100;
'''

# Execute and get results as a list of dictionaries
result_rows = execute_sql(sql_query)

# Print results
for row in result_rows:
    print(row)

