import re
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from playwright.sync_api import sync_playwright

# Step 1: Read the question
with open("question.txt", "r") as f:
    question_text = f.read()

# Step 2: Extract URL from question
url_match = re.search(r"https?://\S+", question_text)
if not url_match:
    raise ValueError("No URL found in question.txt")

url = url_match.group(0)

def fetch_html_with_playwright(url, save_path="page.html"):
    from pathlib import Path
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        # Wait until page is idle (all resources loaded)
        page.wait_for_load_state('networkidle')

        # Scroll to the bottom slowly to trigger lazy-loading content
        page.evaluate("""
            () => {
                return new Promise((resolve) => {
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
            }
        """)
        
        page.wait_for_timeout(3000)  # Give 3s after scroll for final JS

        html = page.content()

        # Save HTML to file
        Path(save_path).write_text(html, encoding="utf-8")

        browser.close()

    return html
html = fetch_html_with_playwright(url, save_path="page.html")

# Then parse it
with open("page.html", "r", encoding="utf-8") as f:
    html = f.read()
for i, table in enumerate(tables):
    caption = table.find('caption')
    caption_text = caption.get_text(strip=True) if caption else "No caption"
    rows = table.find_all("tr")
    print(f"Index: {i} | Caption: {caption_text} | Rows: {len(rows)}")
