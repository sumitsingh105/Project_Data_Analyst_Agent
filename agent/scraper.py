import pandas as pd
import requests
from bs4 import BeautifulSoup
from agent.analyzer import analyze_film_data

def handle_wikipedia_task(task_description: str):
    # Extract Wikipedia URL from task description
    url_line = next((line for line in task_description.splitlines() if "wikipedia.org" in line), None)
    if not url_line:
        return {"error": "No Wikipedia URL found in task description."}

    url = url_line.strip()
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table", {"class": "wikitable"})

        # Use the first "wikitable"
        df = pd.read_html(str(tables[0]))[0]
        df.columns = [col.strip() for col in df.columns]

        # Analyze and return response
        return analyze_film_data(df)  # ✅ FIXED

    except Exception as e:
        return {"error": f"Scraping failed: {str(e)}"}
