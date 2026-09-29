"""
=============================================================================
EduGenie - Summarization Module (summary_module.py)
=============================================================================
Purpose:
    Summarizes long educational text, articles, or lecture notes into concise,
    structured, and easy-to-digest key points for students.

Key Features:
    - High-level executive summary in 2-3 simple sentences.
    - Bulleted key concepts and critical facts.
    - Preserves core meaning, scientific terms, and context without fluff.
    - Quick Revision Cheat Sheet at the end.
=============================================================================
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MODEL_CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-lite-latest",
]


def get_gemini_api_key() -> str:
    """Retrieve Gemini API key from environment variables."""
    return os.getenv("GEMINI_API_KEY", "").strip()


def call_gemini_api(prompt: str) -> dict:
    """
    Helper function to send summarization prompt to Google Gemini API.
    Supports both google.genai and google.generativeai SDKs.
    """
    api_key = get_gemini_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        return {
            "status": "error",
            "message": (
                "Gemini API key is missing! Please configure GEMINI_API_KEY in your .env file. "
                "Get your key from https://aistudio.google.com/"
            )
        }

    last_error = None
    # Try Modern google.genai SDK
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        for model_name in MODEL_CANDIDATES:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    return {
                        "status": "success",
                        "data": response.text.strip(),
                        "model_used": f"Google Gemini ({model_name})"
                    }
            except Exception as e:
                last_error = str(e)
                continue
    except Exception as e:
        last_error = str(e)

    # Fallback to legacy google.generativeai SDK if available
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        for model_name in MODEL_CANDIDATES:
            try:
                model = legacy_genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return {
                        "status": "success",
                        "data": response.text.strip(),
                        "model_used": f"Google Gemini ({model_name})"
                    }
            except Exception as e:
                last_error = str(e)
                continue
    except Exception as e:
        last_error = str(e)

    error_msg = f"Gemini API Error: {last_error}" if last_error else "Failed to summarize text with Gemini API. Please check your API key."
    return {
        "status": "error",
        "message": error_msg
    }


def summarize_text(text: str) -> dict:
    """
    Summarizes educational text into a concise, high-yield student summary.

    Args:
        text (str): Long educational paragraph, article, or lecture text.

    Returns:
        dict: Standardized response with status, summarized text or error message.
    """
    # 1. Validate input text
    if not text or not text.strip():
        return {
            "status": "error",
            "message": "Please provide educational text to summarize."
        }

    # Minimum length check for quality
    if len(text.strip()) < 30:
        return {
            "status": "error",
            "message": "The text provided is too short. Please provide at least a few sentences to summarize."
        }

    # 2. Craft student-focused summarization prompt
    prompt = f"""
You are an expert academic summarizer for EduGenie.
Summarize the following educational text for a student. Make it crisp, easy to read, and highlight the most important points without losing core meaning.

Original Text:
\"\"\"{text.strip()}\"\"\"

Please structure the summary as follows:
📌 **Core Concept (TL;DR)**:
A 2-3 sentence overview capturing the primary idea.

🔑 **Key Takeaways & Important Points**:
- Bullet points detailing the essential concepts, facts, or mechanisms.
- Bold critical terms for easy scanning.

📝 **Quick Revision Tip**:
One memorable memory aid, formula, or concluding note for quick exam review.
"""

    return call_gemini_api(prompt)
