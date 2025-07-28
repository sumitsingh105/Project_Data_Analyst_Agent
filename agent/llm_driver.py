import aiohttp
import asyncio
import os

AIPIPE_ENDPOINT = "https://aipipe.org/openrouter/v1/chat/completions"
AIPIPE_API_KEY = os.getenv("AIPIPE_API_KEY")  # Set this in your .env or environment

HEADERS = {
    "Authorization": f"Bearer {AIPIPE_API_KEY}",
    "Content-Type": "application/json"
}

MODEL = "google/gemini-2.0-flash-lite-001"  # or any supported model

async def call_ai(user_query: str) -> str:
    """Call LLM via AI Pipe and return response string."""
    if not AIPIPE_API_KEY:
        return {"error": "Missing AIPIPE_API_KEY. Please set it in your environment."}

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Classify the task as 'Wikipedia', 'DuckDB', or 'General'"},
            {"role": "user", "content": user_query}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(AIPIPE_ENDPOINT, headers=HEADERS, json=payload) as resp:
                if resp.status != 200:
                    return {"error": f"LLM call failed: {resp.status} - {await resp.text()}"}
                data = await resp.json()

                # 🛑 Defensive check
                if "choices" not in data or not data["choices"]:
                    return {"error": f"LLM classification failed: {data}"}

                return data["choices"][0]["message"]["content"]

    except Exception as e:
        return {"error": f"LLM request error: {str(e)}"}
