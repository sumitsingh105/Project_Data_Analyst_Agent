import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import GenerativeModel
import requests
import re
import pandas as pd

# Load API key from environment
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = GenerativeModel("gemini-1.5-flash")


def get_task_plan(task_description: str, save_path: str = "logs/task_plan.txt") -> str:
    prompt = f"""
You are a data analyst agent. Your job is to break down the following task into a structured plan of action. Do not solve it—just break it down into clear steps.

The workflow should follow this process:

1. **Extract URL** from the task, if available.
2. **Scrape the webpage** using Playwright to capture all tables, including dynamically loaded content.
3. **Parse tables** using BeautifulSoup and pandas, including hidden ones without captions.
4. **Generate semantic embeddings** of each table summary using Gemini embeddings.
5. **Embed the user query** and compute similarity with each table.
6. **Rerank top-k similar tables** using Gemini Pro, and select the best one.
7. **Save the best-matching table** as `matched_table.csv`.
8. **Extract metadata** from that table (column names, sample rows).
9. **Send table metadata and task description** to Gemini for code generation.
10. **Execute the generated code** and return the result.

Make sure to preserve any URLs, data sources, image references, or user constraints. Avoid making up any steps or external data sources.

Task:
\"\"\"\n{task_description.strip()}\n\"\"\"

Provide the breakdown as a bullet-point list.
"""

    response = model.generate_content(prompt)
    plan = response.text.strip()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w") as f:
        f.write(plan)

    return plan


def clean_generated_code(code: str) -> str:
    # Remove code fences
    code = re.sub(r"^```(?:python)?\s*", "", code.strip())
    code = re.sub(r"\s*```$", "", code.strip())
    
    # Replace invalid escape sequences like \$ with raw string
    code = re.sub(r"([rR]?)'\\\$'", r"r'\$'", code)
    code = re.sub(r'([rR]?)"\\\$"', r'r"\$"', code)

    # Fix pd.read_html on raw HTML with StringIO
    if "pd.read_html(str(" in code:
        code = (
            "from io import StringIO\n" +
            code.replace("pd.read_html(str(", "pd.read_html(StringIO(str(")
        )

    # Remove f-strings for fixed error messages (avoid f"{'...'}")
    code = re.sub(r'f"([^{}]*)"', r'"\1"', code)
    code = re.sub(r"f'([^{}]*)'", r"'\1'", code)

    return code



def generate_code_from_plan(task_description: str, plan: str, csv_path: str = "matched_table.csv", save_path: str = "generated_code.py") -> str:
    dir_path = os.path.dirname(save_path)
    if dir_path:  # Only create if directory path is not empty
        os.makedirs(dir_path, exist_ok=True)

    # rest of your function...

    # Read CSV metadata
    df = pd.read_csv(csv_path)
    columns = df.columns.tolist()
    preview_rows = df.head(3).astype(str).values.tolist()
    preview_text = "\n".join([", ".join(row) for row in preview_rows])

    # Compose code generation prompt with table metadata
    code_prompt = f"""
You are a senior Python data analyst.

You have a CSV file named `matched_table.csv` containing data with the following columns:
{columns}

Here is a preview of the first 3 rows:
{preview_text}

Write Python code that:

1. Loads the CSV using pandas (`pd.read_csv("matched_table.csv")`).
2. Prints basic metadata: shape, column names, and first 3 rows.
3. Cleans numeric columns by first converting to string using `astype(str)`, then removing symbols like $, %, commas using:
   `df[col] = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)`
4. Drops nulls if needed.
5. Then performs the following task:

You will be given a CSV file `matched_table.csv` to analyze using Python and pandas.

**Requirements:**

- For every numeric column, first clean the data by removing all non-numeric symbols such as `$`, `%`, commas, and spaces using a regex replacement like:
  `df[col] = df[col].str.replace(r'[^\d.-]', '', regex=True)`

- Convert these cleaned columns to numeric types with `pd.to_numeric(..., errors='coerce')`.

- After cleaning, drop rows where the relevant numeric columns are NaN before performing any aggregation or calculation.

- When calculating statistics like `idxmax()`, always check if the column is empty after cleaning to avoid errors.

- If the column is empty or all NaN after cleaning, handle gracefully by returning an appropriate message or skipping the calculation.

**Only provide valid Python code without markdown or explanations.**

### TASK:
{task_description}

### PLAN:
{plan}

Do NOT scrape URLs or use BeautifulSoup.

Do NOT include markdown or explanations — provide only valid Python code.

At the end, combine all answers into a dictionary named `result` and print it using:

```python
import json
print(json.dumps(result))
"""

    headers = {
        "Authorization": f"Bearer {os.getenv('AI_PIPE_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful Python code assistant."},
            {"role": "user", "content": code_prompt}
        ]
    }

    response = requests.post(
        "https://aipipe.org/openrouter/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"AI Pipe Error: {response.status_code} - {response.text}")

    raw_code = response.json()["choices"][0]["message"]["content"]
    code = clean_generated_code(raw_code)

    with open(save_path, "w") as f:
        f.write(code)

    return code
