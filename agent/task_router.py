from agent.scraper import handle_wikipedia_task
from agent.analyzer import handle_duckdb_task

async def handle_task(task_description: str):
    task_lower = task_description.lower()

    if "wikipedia.org" in task_lower:
        return handle_wikipedia_task(task_description)  # ✅ removed `await`

    elif "duckdb" in task_lower or "read_parquet" in task_lower:
        return await handle_duckdb_task(task_description)

    else:
        return {
            "error": "Task not recognized as Wikipedia or DuckDB. Add keywords like `wikipedia.org` or `read_parquet`."
        }
