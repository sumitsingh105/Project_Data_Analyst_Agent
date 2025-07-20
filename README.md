data-analyst-agent/
├── main.py                  # FastAPI entry point
├── agent/
│   ├── __init__.py
│   ├── task_router.py       # Classify and route tasks (scrape, query, analyze, visualize)
│   ├── scraper.py           # Handles web scraping
│   ├── analyzer.py          # Handles pandas/DuckDB analysis
│   ├── visualizer.py        # Creates charts and base64 outputs
│   └── llm_driver.py        # Talks to GPT or other LLM
├── utils/
│   ├── base64_tools.py      # Encode images
│   └── duckdb_client.py     # DuckDB setup for parquet/S3 queries
├── requirements.txt
└── README.md



Project2_Agentic/
├── main.py                    # FastAPI app entry point
├── agent/
│   ├── __init__.py
│   ├── task_router.py         # Routes task to handler based on keywords
│   ├── scraper.py             # Handles Wikipedia scraping
│   ├── analyzer.py            # Data analysis (correlation, filtering, etc.)
│   ├── visualizer.py          # Creates scatterplots and encodes to base64
├── question.txt               # Input task to be POSTed to the API
├── promptfoo.yaml             # Evaluation config for promptfoo
├── requirements.txt           # Python dependencies (optional)
