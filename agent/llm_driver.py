import os
import requests

AI_PIPE_URL = os.getenv("AI_PIPE_URL", "https://aipipe.org/openrouter/v1/chat/completions")
AI_PIPE_MODEL = os.getenv("AI_PIPE_MODEL", "openai/gpt-4")  # or "google/gemini-2.0-flash-lite-001"
AI_PIPE_API_KEY = os.getenv("AI_PIPE_API_KEY")  # export this in your environment

def ask_llm(prompt: str, model: str = None) -> str:
    headers = {
        "Authorization": f"Bearer {AI_PIPE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model or AI_PIPE_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful data analysis assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(AI_PIPE_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"[LLM Error] {str(e)}"
