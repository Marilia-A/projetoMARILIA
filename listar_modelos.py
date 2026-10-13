import os
import httpx
from dotenv import load_dotenv

load_dotenv()
r = httpx.get(
    "https://generativelanguage.googleapis.com/v1beta/models",
    headers={"x-goog-api-key": os.getenv("GEMINI_API_KEY")},
    params={"pageSize": 200},
    timeout=30,
)
for m in r.json().get("models", []):
    if "generateContent" in m.get("supportedGenerationMethods", []) and "flash" in m["name"]:
        print(m["name"].replace("models/", ""))