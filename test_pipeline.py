import sys
from pipeline.pipeline import run_pipeline
import json

def main():
    question = "Portfolio outstanding for branch B001?"
    print(f"\nRunning pipeline for: '{question}'...")
    try:
        result = run_pipeline(question, username="admin")
        
        print("\n" + "="*50)
        print("SQL QUERY GENERATED:")
        print("="*50)
        print(result.get("sql_query", "No SQL generated"))
        
        print("\n" + "="*50)
        print("DATABASE RESULTS:")
        print("="*50)
        response = result.get("response", [])
        if response:
            print(json.dumps(response, indent=2, default=str))
        else:
            print("No data found or empty result.")
            
        if result.get("errors"):
            print("\n" + "!"*50)
            print("ERRORS:")
            print("!"*50)
            for err in result["errors"]:
                print(f"- {err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
