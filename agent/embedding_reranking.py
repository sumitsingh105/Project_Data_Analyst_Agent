import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from sklearn.metrics.pairwise import cosine_similarity
from playwright.async_api import async_playwright
import google.generativeai as genai
import asyncio

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
chat_model = genai.GenerativeModel("gemini-1.5-flash")


async def fetch_html(url, save_path="page.html"):
    from pathlib import Path
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_load_state('networkidle')

        await page.evaluate("""
            () => new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 100;
                const timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if (totalHeight >= document.body.scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        """)

        await page.wait_for_timeout(3000)
        html = await page.content()
        Path(save_path).write_text(html, encoding="utf-8")
        await browser.close()
    return html


def get_table_title(table):
    caption = table.find("caption")
    if caption:
        return caption.get_text(strip=True)
    heading = table.find_previous(["h1", "h2", "h3", "h4", "h5", "h6"])
    if heading:
        return heading.get_text(strip=True)
    prev_tag = table.find_previous()
    while prev_tag and prev_tag.name != "[document]":
        if prev_tag.name in ["b", "strong"] or (
            prev_tag.name == "p" and prev_tag.find(["b", "strong"])
        ):
            return prev_tag.get_text(strip=True)
        prev_tag = prev_tag.find_previous()
    class_name = " ".join(table.get("class", [])) if table.get("class") else ""
    table_id = table.get("id", "") or ""
    parts = []
    if class_name:
        parts.append(f"Class: {class_name}")
    if table_id:
        parts.append(f"ID: {table_id}")
    return " | ".join(parts) if parts else "No caption"


def chunk_text(text, max_chars=3000):
    words = text.split()
    chunks, current_chunk, current_len = [], [], 0
    for w in words:
        if current_len + len(w) + 1 > max_chars:
            chunks.append(" ".join(current_chunk))
            current_chunk = [w]
            current_len = len(w) + 1
        else:
            current_chunk.append(w)
            current_len += len(w) + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def get_embedding(text):
    chunks = chunk_text(text)
    embeddings = []
    for chunk in chunks:
        resp = genai.embed_content(
            model="models/embedding-001",
            content=chunk,
            task_type="semantic_similarity"
        )
        embeddings.append(resp["embedding"])
    avg_embedding = [sum(col) / len(col) for col in zip(*embeddings)]
    return avg_embedding


def pick_best_table(question, top_tables):
    prompt = f"""You are a helpful assistant that selects the most relevant table for a given question.

Question:
\"\"\"\n{question}\n\"\"\"

Here are {len(top_tables)} tables from the webpage:
"""
    for t in top_tables:
        prompt += f"\n--- Table {t['index']} ---\n{t['summary']}\n"
    prompt += "\nWhich table (by index) best answers the question? Return just the index (e.g., 1)."
    response = chat_model.generate_content(prompt)
    text = response.text.strip()
    index_match = re.search(r'\d+', text)
    return int(index_match.group()) if index_match else top_tables[0]['index']


async def extract_best_table_from_url(url: str, question: str) -> pd.DataFrame:
    html = await fetch_html(url)

    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    table_data = []

    for i, table in enumerate(tables):
        try:
            table_soup = BeautifulSoup(str(table), "html.parser")
            for sup in table_soup.find_all("sup"):
                sup.decompose()
            clean_html = str(table_soup)
            dfs = pd.read_html(StringIO(clean_html))
            for df in dfs:
                df = df.dropna(how='all')
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                if df.empty or len(df.columns) < 2:
                    continue
                caption = get_table_title(table)
                preview = df.head(3).astype(str).to_string(index=False)
                summary = f"Caption: {caption}\nColumns: {', '.join(map(str, df.columns))}\nPreview:\n{preview}"
                table_data.append({'index': i, 'df': df, 'summary': summary})
        except Exception:
            continue

    question_embed = get_embedding(question)
    for t in table_data:
        t['embedding'] = get_embedding(t['summary'])

    embeds = [t['embedding'] for t in table_data]
    similarities = cosine_similarity([question_embed], embeds)[0]
    for i, score in enumerate(similarities):
        table_data[i]['score'] = score

    table_data.sort(key=lambda x: x['score'], reverse=True)
    top_tables = table_data[:3]
    best_index = pick_best_table(question, top_tables)
    best_table = next(t for t in table_data if t['index'] == best_index)

    best_table['df'].to_csv("matched_table.csv", index=False)
    return best_table['df']
