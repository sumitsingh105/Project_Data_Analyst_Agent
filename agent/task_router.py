import re
import traceback
import asyncio
from agent.gemini_planner import get_task_plan, generate_code_from_plan
from agent.embedding_reranking import extract_best_table_from_url



async def handle_task(task_description: str):
    try:
        # Step 1: Extract and fetch table from URL (if any)
        url_match = re.search(r"https?://\S+", task_description)
        if url_match:
            url = url_match.group(0)
            print(f"🌐 Fetching table from: {url}")
            df = await extract_best_table_from_url(url, task_description)
            print("✅ Table extracted. Saved to matched_table.csv")
        else:
            print("⚠️ No URL found in task. Skipping table extraction.")

        # Step 2: Get task plan from Gemini
        plan = get_task_plan(task_description, save_path="logs/last_plan.txt")
        print("✅ Gemini Breakdown saved to logs/last_plan.txt")

        # Step 3: Generate code from plan, passing matched_table.csv path
        code = generate_code_from_plan(task_description, plan, csv_path="matched_table.csv", save_path="generated_code.py")
        print("🧠 Gemini Code generated and saved to generated_code.py")

        # Step 4: Execute generated code safely
        exec_namespace = {}
        try:
            exec(code, exec_namespace)
            output = exec_namespace.get("result")
            if output is None:
                output = {"note": "Code executed but no 'result' variable was found."}
        except Exception as e:
            output = {
                "error": f"Execution failed: {str(e)}",
                "traceback": traceback.format_exc(),
                "note": "Check 'generated_code.py' for the faulty code."
            }

    except Exception as e:
        output = {
            "error": f"Top-level failure: {str(e)}",
            "traceback": traceback.format_exc()
        }

    return output
