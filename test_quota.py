import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Force utf-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

api_key = os.getenv("GEMINI_API_KEY")
from google import genai
client = genai.Client(api_key=api_key)

test_models = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-lite-latest",
]

prompt = "Explain in one sentence what gravity is."

for m in test_models:
    try:
        res = client.models.generate_content(model=m, contents=prompt)
        print(f"[SUCCESS] {m}: {res.text.strip()[:80]}...")
    except Exception as e:
        print(f"[FAIL] {m}: {e}")
