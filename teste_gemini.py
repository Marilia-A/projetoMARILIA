import os
import httpx
from dotenv import load_dotenv

load_dotenv()
chave = os.getenv("GEMINI_API_KEY")
modelo = os.getenv("GEMINI_MODEL")

r = httpx.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
    headers={"x-goog-api-key": chave},
    json={"contents": [{"parts": [{"text": "Diga oi em uma frase"}]}]},
    timeout=30,
)
print(r.status_code)
print(r.json())