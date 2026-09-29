import os
import traceback
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
from google import genai
client = genai.Client(api_key=api_key)

import explanation_module
prompt = """You are EduGenie, an expert educational tutor who specializes in explaining complex ideas using the Feynman Technique.
Explain the following concept or topic so that a middle school or high school student can easily understand it:
Concept: Gravity
"""

print("Trying gemini-3.6-flash...")
try:
    res = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
    print("gemini-3.6-flash succeeded:", res.text[:100])
except Exception as e:
    traceback.print_exc()

print("\nTrying gemini-3.5-flash-lite...")
try:
    res = client.models.generate_content(model="gemini-3.5-flash-lite", contents=prompt)
    print("gemini-3.5-flash-lite succeeded:", res.text[:100])
except Exception as e:
    traceback.print_exc()
