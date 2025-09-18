import time
from pipeline.modules.llm_utils import LLMCallError
from utils.dto import PipelineDTO
from .modules.rephrase import rephrase_question
from .modules.intent import identify_intent
from pipeline.modules.sql_generator import generate_sql_from_dto
from .modules.columns import identify_columns
from pipeline.modules.load_references import load_references
from utils.db_cred import execute_sql
from utils.audit import save_master_record, save_child_records
from pipeline.modules.joining_instructions import get_joining_instructions
from pipeline.modules.table_utils import correct_tables_and_columns

# Few-Shot imports
from pipeline.modules.fewshot_module import fetch_few_shots,init_index_and_bm25
from pipeline.modules.embedder import Embedder
import pandas as pd

# Load reference metadata once
metrics_reference, columns_reference, tables_reference = load_references()

# ------------------ Load Few-Shot Examples & Embedder ------------------
examples_df = pd.read_csv("fewshot_example.csv")
embedder = Embedder()  # from embedder.py
faiss_index, tokenized_corpus, bm25_model = init_index_and_bm25(examples_df, embedder)

def run_pipeline(question: str, username: str = "default_user", model: str = "gemini-1.5-flash") -> dict:
    # Initialize DTO with proper defaults
    dto = PipelineDTO(input_question=question)

    print("\n🚀 [Pipeline] Starting pipeline execution")
    print(f"👉 Original Question: {dto.input_question}")

    try:
        # ---------------- Step 1: Rephrase ----------------
        step_start = time.time()
        dto.rephrased_question = rephrase_question(dto.input_question)  # no need for add_missing_keywords
        dto.keywords = list(set(dto.keywords))  # Deduplicate keywords
        step_end = time.time()
        dto.steps_usage.append({
            "step": "rephrase_question",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "start_time": step_start,
            "end_time": step_end
        })
        print(f"✅ Rephrased Question: {dto.rephrased_question}")


        # ---------------- Step 2: Intent ----------------
        step_start = time.time()
        try:
            intent_result, intent_usage = identify_intent(
                dto.rephrased_question,
                tables_reference,
                model=model
            )
        except LLMCallError as e:
            # Handle LLM-specific failure
            raise RuntimeError(f"[Pipeline] LLM failed during intent identification: {str(e)}")
        step_end = time.time()
        dto.tables = intent_result.get("tables", [])
        dto.keywords = intent_result.get("keywords", [])
        dto.selected_metric = intent_result
        dto.steps_usage.append({
            "step": "intent_identification",
            "prompt_tokens": intent_usage.get("prompt_tokens", 0),
            "completion_tokens": intent_usage.get("completion_tokens", 0),
            "start_time": step_start,
            "end_time": step_end
        })

        # ---------------- Step 2.1: Columns ----------------
        step_start = time.time()
        column_result, column_usage = identify_columns(
            dto.rephrased_question,
            intent_result, columns_reference,
            model=model
        )
        step_end = time.time()
        dto.columns = column_result.get("columns", {})
        dto.keywords.extend(column_result.get("keywords", []))
        dto.selected_metric = column_result
        dto.steps_usage.append({
            "step": "column_identification",
            "prompt_tokens": column_usage.get("prompt_tokens", 0),
            "completion_tokens": column_usage.get("completion_tokens", 0),
            "start_time": step_start,
            "end_time": step_end
        })

        # ---------------- Step 2.5: Correct tables safely ----------------

        dto.tables, dto.columns, corrections = correct_tables_and_columns(dto.tables, dto.columns, tables_reference)
        if corrections:
            print(f"📌 Fuzzy Corrected Tables: {corrections}")
        print(f"📌 Final Tables to use: {dto.tables}")
        print(f"📌 Final Columns: {dto.columns}")


        # ---------------- Step 4: Generate Join Instructions ----------------
        step_start = time.time()
        dto.joinings = get_joining_instructions(dto.tables)
        print(f"📌 Join Instructions: {dto.joinings}")

        # ---------------- Step 4.5: Run Few-Shot Retrieval ----------------
        retrieval = fetch_few_shots(
            user_question=dto.rephrased_question,
            faiss_index=faiss_index,
            examples_df=examples_df,
            embedder=embedder,
            bm25_model=bm25_model,
            tokenized_corpus=tokenized_corpus,
            top_k=2
        )

        dto.few_shots = retrieval["few_shot_examples"]
        dto.few_shot_matched_indices = retrieval["matched_indices"]

        print(f"🔍 Retrieved {len(dto.few_shots)//2} few-shot examples")
        # print(f"🔍 Matched Indices: {dto.few_shot_matched_indices}")

        # ---------------- Step 5: Generate SQL ----------------
        try:
            dto = generate_sql_from_dto(dto, model=model, top_k=2)
        except LLMCallError as e:
            raise RuntimeError(f"[Pipeline] LLM failed during SQL generation: {str(e)}")

        step_end = time.time()
        dto.steps_usage.append({
            "step": "sql_generation",
            "prompt_tokens": getattr(dto, "sql_usage", {}).get("prompt_tokens", 0),
            "completion_tokens": getattr(dto, "sql_usage", {}).get("completion_tokens", 0),
            "start_time": step_start,
            "end_time": step_end
        })
        print(f"✅ Generated SQL:\n{dto.sql_query}")
        print(f"⏱ Step Time: {step_end - step_start:.3f}s")


        # ---------------- Step 6: Execute SQL ----------------
        step_start = time.time()
        if dto.sql_query.strip():
            dto.response = execute_sql(dto.sql_query)
        else:
            dto.response = []
            print("⚠️ SQL Query was empty; skipping execution")
        step_end = time.time()
        dto.steps_usage.append({
            "step": "sql_execution",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "start_time": step_start,
            "end_time": step_end
        })

        print(f"📊 SQL Execution Result : {dto.response}")

        # ---------------- Step 7: Finalize ----------------
        dto.finalize_timing()
        dto.total_tokens = dto.compute_total_tokens()
        print(f"📝 Total Tokens Across All Steps: {dto.total_tokens}")

        # ---------------- Step 8: Audit ----------------
        master_id = save_master_record(
            username=username,
            question=dto.input_question,
            response=dto.response,
            intent=dto.selected_metric,
            sql_query=dto.sql_query,
            tokens={
                "prompt_tokens": sum(step.get("prompt_tokens", 0) for step in dto.steps_usage),
                "completion_tokens": sum(step.get("completion_tokens", 0) for step in dto.steps_usage),
                "total_tokens": dto.total_tokens
            },
            start_time=dto.start_time,
            end_time=dto.end_time
        )
        save_child_records(master_id, dto.steps_usage)
        print("🎉 [Pipeline] Final Result ready!")

        return dto.to_dict()

    except RuntimeError as e:
        print("❌ [Pipeline] LLM Error caught:", str(e))
        dto.errors.append(str(e))
        dto.finalize_timing()
        return dto.to_dict()

    except Exception as e:
        print("❌ [Pipeline] General Error caught:", str(e))
        dto.errors.append(str(e))
        dto.finalize_timing()
        return dto.to_dict()