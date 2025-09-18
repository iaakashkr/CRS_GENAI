# sql_generator.py

import re
import logging
from .llm_utils import call_llm, LLMCallError   # import exception too
from .prompt_loader import load_prompt

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_sql_from_dto(dto, model="gemini-1.5-flash", top_k=2, faiss_index=None, examples_df=None, embedder=None, bm25_model=None, tokenized_corpus=None):
    """
    Generate SQL query from DTO using LLM, injecting few-shot examples directly from DTO.
    Stores few-shot examples and matched indices in the DTO.
    """

    logger.info("🚀 Starting SQL generation from DTO...")

    # ---------------- Step 0.5: Quote table names safely ----------------
    quoted_tables = []
    for t in dto.tables:
        if '.' in t:
            schema, table = t.split('.', 1)
            quoted_tables.append(f'"{schema}"."{table}"')
        else:
            quoted_tables.append(f'"{t}"')
    # logger.info(f"📌 Quoted Tables: {quoted_tables}")

    # ---------------- Step 0.7: Prepare Few-Shot Examples ----------------
    few_shot_examples = getattr(dto, "few_shots", {})
    matched_indices = getattr(dto, "few_shot_matched_indices", [])

    logger.info(f"Similarity Flag: {bool(few_shot_examples)}")
    logger.info(f"Matched Indices: {matched_indices}")

    # ---------------- Step 1: Format joinings ----------------
    joinings_list = []
    for j in dto.joinings:
        join_str = f"{j['from_table']} -> {j['to_table']}: {j['instruction']}"
        joinings_list.append(join_str)
        logger.info(f"🔗 Adding joining: {join_str}")

    # ---------------- Step 2: Load prompt ----------------
    full_prompt = load_prompt(
        "sql.yml",
        rephrased_question=dto.rephrased_question,
        selected_tables=dto.tables,
        selected_columns=dto.columns,
        joinings=joinings_list,
        few_shot_examples=few_shot_examples  # Inject few-shot examples
    )

    # ---------------- Step 3: Call LLM ----------------
    try:
        sql_query, sql_usage = call_llm(
            step_name="generate_sql",
            prompt=full_prompt,
            model_name=model,
            response_format="text"
        )
    except LLMCallError as e:
        raise RuntimeError(f"[generate_sql] LLM failed: {str(e)}")

    # ---------------- Step 4: Clean SQL ----------------
    sql_query = sql_query.strip()
    sql_query = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", sql_query, flags=re.MULTILINE).strip()
    sql_query = re.sub(r"^(query\s*[:=]\s*)", "", sql_query, flags=re.IGNORECASE).strip()

    # ---------------- Step 5: Update DTO ----------------
    dto.sql_query = sql_query
    dto.sql_usage = sql_usage
    logger.info("✅ DTO Updated with SQL Query, Usage, and Few-Shot info")

    return dto
