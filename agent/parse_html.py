from bs4 import BeautifulSoup
import pandas as pd

with open("logs/scraped.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
tables = soup.find_all("table")

for idx, table in enumerate(tables):
    try:
        df = pd.read_html(str(table))[0]
        print(f"✅ Table {idx} shape: {df.shape}")
        print(df.head())
    except Exception as e:
        print(f"❌ Error reading table {idx}: {e}")
