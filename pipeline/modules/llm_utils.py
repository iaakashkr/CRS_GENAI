# import google.generativeai as genai
# import json
# from token_counter import count_tokens
# from token_tracker import token_tracker
# import re
# import os
# from dotenv import load_dotenv

# load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))



# # Fetch available models once
# # AVAILABLE_MODELS = [m.name for m in genai.list_models()]

# def call_llm(step_name: str, prompt: str, model_name: str = "gemini-1.5-flash", response_format: str = "text"):
#     """
#     Robust wrapper to call Gemini LLM with token counting + logging.
#     Validates model name, counts tokens, and handles JSON/text output.
#     """
    
#     prompt_tokens = count_tokens(prompt, model_name)

    
#     # Create model instance
#     model = genai.GenerativeModel(model_name)

#     # Make LLM call (safe with dict input)
#     try:
#         response = model.generate_content(prompt)
#         output = response.text.strip()
#     except Exception as e:
#         return {"error": f"LLM call failed: {str(e)}"}, {"prompt_tokens": prompt_tokens, "completion_tokens": 0, "total_tokens": prompt_tokens, "step": step_name, "model": model_name}
    
#     print("Output: ", output)
#     # Count output tokens
#     completion_tokens = count_tokens(output, model_name)
    
#     # Log usage
#     usage = {
#         "prompt_tokens": prompt_tokens,
#         "completion_tokens": completion_tokens,
#         "total_tokens": prompt_tokens + completion_tokens,
#         "step": step_name,
#         "model": model_name,
#     }
#     token_tracker.log_step(step_name, prompt_tokens, completion_tokens)
    
#     # Handle JSON response safely
#     if response_format == "json":
#         cleaned = output
#         if output.startswith("```json"):
#             cleaned = output[7:].rstrip("```").strip()
#         try:
#             return json.loads(cleaned), usage
#         except json.JSONDecodeError:
#             return {"error": "Failed to parse JSON", "raw": output}, usage

#     return output, usage



import google.generativeai as genai
import json
from pipeline.modules.token_counter import count_tokens
from pipeline.modules.token_tracker import token_tracker
import re
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class LLMCallError(Exception):
    """Custom exception for LLM call failures."""
    pass


def call_llm(step_name: str, prompt: str, model_name: str = "gemini-1.5-flash", response_format: str = "text"):
    """
    Robust wrapper to call Gemini LLM with token counting + logging.
    Validates model name, counts tokens, and handles JSON/text output.
    """
    prompt_tokens = count_tokens(prompt, model_name)

    # Create model instance
    model = genai.GenerativeModel(model_name)

    try:
        response = model.generate_content(prompt)
        output = response.text.strip() if response.text else ""

    except Exception as e:
        msg = str(e)
        # Specific handling for quota / token exhaustion
        if "ResourceExhausted" in msg or "quota" in msg.lower() or "token" in msg.lower():
            raise LLMCallError(f"[{step_name}] Token exhaustion: {msg}")
        raise LLMCallError(f"[{step_name}] LLM call failed: {msg}")

    print("Output: ", output)

    # Count output tokens
    completion_tokens = count_tokens(output, model_name)

    # Log usage
    usage = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "step": step_name,
        "model": model_name,
    }
    token_tracker.log_step(step_name, prompt_tokens, completion_tokens)

    # Handle JSON response safely
    if response_format == "json":
        cleaned = output
        if output.startswith("```json"):
            cleaned = output[7:].rstrip("```").strip()
        try:
            return json.loads(cleaned), usage
        except json.JSONDecodeError:
            raise LLMCallError(f"[{step_name}] Failed to parse JSON response: {output}")

    return output, usage
