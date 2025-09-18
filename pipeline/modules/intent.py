#intent.py

import json
import re
from datetime import datetime
import pandas as pd
from pipeline.modules.llm_utils import call_llm, LLMCallError   # import exception too
from pipeline.modules.prompt_loader import load_prompt
from pipeline.modules.load_references import load_references

# Load reference data once
metrics_reference, columns_reference, tables_reference = load_references()


def identify_intent(rephrased_question, tables_reference, model="gemini-1.5-flash"):
    """
    Identify the intent, metrics, keywords, locations, and time frame from a user question
    using the Gemini model and the YAML-based prompt template.
    Token counting + logging is handled centrally inside call_llm.
    """

    full_prompt = load_prompt(
        "intent.yml",
        rephrased_question=rephrased_question,
        tables_reference=tables_reference,
        current_date_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    try:
        # Centralized LLM call
        intent_result, intent_usage = call_llm(
            step_name="identify_intent",
            prompt=full_prompt,
            model_name=model,
            response_format="text"
        )
    except LLMCallError as e:
        # Bubble up a clear error message
        raise RuntimeError(f"[identify_intent] LLM failed: {str(e)}")

    # Clean JSON (strip Markdown fencing if model added it)
    cleaned = re.sub(r"^```json\s*|\s*```$", "", intent_result, flags=re.DOTALL).strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError(f"[identify_intent] Invalid JSON from model:\n{intent_result}")

    return result, intent_usage
