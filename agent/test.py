import os
import google.generativeai as genai

# Set up API key (from env or hardcoded — for testing)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Embed the content using Gemini Embedding API
response = genai.embed_content(
    model="models/embedding-001",
    content="What is the meaning of life?",
    task_type="semantic_similarity"
)

# Print the embedding vector
print(response["embedding"])
