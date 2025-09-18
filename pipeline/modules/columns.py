#columns.py

import json
import re
from datetime import datetime
import pandas as pd
from pipeline.modules.llm_utils import call_llm   # centralized LLM wrapper
from pipeline.modules.prompt_loader import load_prompt
from pipeline.modules.load_references import load_references


# Load reference data once
metrics_reference, columns_reference, tables_reference= load_references()


def identify_columns(rephrased_question, intent_result, columns_reference, model="gemini-1.5-flash"):
    """
    Identify the intent, metrics, keywords, locations, and time frame from a user question
    using the Gemini model and the YAML-based prompt template.
    Token counting + logging is handled centrally inside call_llm.
    """
    print("Inside column intent****************")
    # Build full prompt directly via load_prompt
    
    # columns_reference = columns_reference.drop(columns=['id','Column_Confidential_Subclass','Table_name'])  # today_change
    columns_reference = columns_reference.copy().drop(columns=['id','Column_Confidential_Subclass','Table_name'])
    
    # Pass new format into prompt
    full_prompt = load_prompt(
        "column.yml",
        rephrased_question=rephrased_question,
        #metrics_reference=metrics_package,
        #tables_reference=tables_reference,
        intent_result=intent_result,
        columns_reference=columns_reference,
        current_date_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    #print("full_prompt*****************:", full_prompt)

    # Centralized LLM call
    column_result, intent_usage = call_llm(
        step_name="identify_columns",
        prompt=full_prompt,
        model_name=model,
        response_format="text"
    )  

    # Clean JSON (strip Markdown fencing if model added it)
    cleaned = re.sub(r"^```json\s*|\s*```$", "", column_result, flags=re.DOTALL).strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON from model:\n{column_result}")
    
    return result, intent_usage
