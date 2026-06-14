#routes_new.py
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

