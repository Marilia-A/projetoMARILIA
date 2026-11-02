import os
import httpx
from dotenv import load_dotenv

load_dotenv()

r = httpx.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
    json={
        "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        "messages": [{"role": "user", "content": "Diga oi em uma frase"}],
    },
    timeout=30,
)
print(r.status_code)
print(r.json())