from flask import Blueprint, request, jsonify
from pipeline.pipeline import run_pipeline  

# change blueprint url prefix to /user
query_bp = Blueprint("query", __name__, url_prefix="/user")

# change route to /query (instead of /ask)
@query_bp.route("/query", methods=["POST"])
def ask_question():
    """
    Accepts a JSON body with 'question' and runs the pipeline.
    """
    try:
        data = request.get_json(silent=True)
        print("DEBUG data:", data)

        question = data.get("question")
        print("DEBUG question:", question)

        result = run_pipeline(question)
        return jsonify(result)
    
    except Exception as e:
        import traceback
        print("DEBUG ERROR:", traceback.format_exc())
        return jsonify({"error": str(e)})


# from flask import Blueprint, request, jsonify
# from pipeline.pipeline import run_pipeline  

# # change blueprint url prefix to /user
# query_bp = Blueprint("query", __name__, url_prefix="/user")

# # change route to /query (instead of /ask)
# @query_bp.route("/query", methods=["POST"])
# def ask_question():
#     """
#     Accepts a JSON body with 'question' (single) or 'questions' (batch)
#     and runs the pipeline.
#     """
#     try:
#         data = request.get_json(silent=True)
#         print("DEBUG data:", data)

#         # Check if "questions" list is present
#         if "questions" in data:
#             results = []
#             for q in data["questions"]:
#                 try:
#                     res = run_pipeline(q)
#                     results.append({"question": q, "result": res})
#                 except Exception as e:
#                     results.append({"question": q, "error": str(e)})
#             return jsonify({"results": results})

#         # Otherwise, fall back to single question
#         elif "question" in data:
#             question = data["question"]
#             print("DEBUG question:", question)
#             result = run_pipeline(question)
#             return jsonify({"result": result})

#         else:
#             return jsonify({"error": "Request must include 'question' or 'questions'"}), 400

#     except Exception as e:
#         import traceback
#         print("DEBUG ERROR:", traceback.format_exc())
#         return jsonify({"error": str(e)})
