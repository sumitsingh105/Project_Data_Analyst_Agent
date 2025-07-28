import pandas as pd
import requests
import io
from bs4 import BeautifulSoup
from agent.analyzer import analyze_film_data

def handle_wikipedia_task(task_description: str):
    url_line = next((line for line in task_description.splitlines() if "wikipedia.org" in line), None)
    if not url_line:
        return {"error": "No Wikipedia URL found in task description."}

    url = url_line.strip()

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table", class_="wikitable")

        for i, table in enumerate(tables):
            try:
                df = pd.read_html(io.StringIO(str(table)))[0]
                df.columns = [col.lower().strip() for col in df.columns]

                if all(col in df.columns for col in ['rank', 'title', 'worldwide gross', 'year']):
                    df.columns = [col.capitalize() for col in df.columns]  # Normalize
                    return analyze_film_data(df)
            except Exception as e:
                continue

        return {"error": "Could not find a relevant grossing films table."}

    except Exception as e:
        return {"error": f"Scraping failed: {str(e)}"}


