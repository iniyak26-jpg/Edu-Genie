"""
=============================================================================
EduGenie - Q&A Module (qna.py)
=============================================================================
Purpose:
    Answers student questions across academic subjects and general topics.
    Connects to Google Gemini AI to return concise, easy-to-understand,
    and structured educational answers.

How it works:
    1. Validates student input.
    2. Reads GEMINI_API_KEY from environment.
    3. Calls Gemini API with a supportive student-focused prompt.
    4. Returns structured JSON containing status and the answer.
=============================================================================
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Candidate Gemini models to ensure compatibility
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
    Helper function to send a prompt to Google Gemini AI.
    Supports both the new google.genai and google.generativeai SDKs.
    """
    api_key = get_gemini_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        return {
            "status": "error",
            "message": (
                "Gemini API key is missing! Please create a .env file with: "
                "GEMINI_API_KEY=your_key_here. Get a free key at https://aistudio.google.com/"
            )
        }

    last_error = None
    # Try Modern google.genai SDK first
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

    # Fallback to google.generativeai SDK if available
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

    error_msg = f"Gemini API Error: {last_error}" if last_error else "Failed to get a response from Gemini API. Please check your API key."
    return {
        "status": "error",
        "message": error_msg
    }


def answer_question(question: str) -> dict:
    """
    Answers an academic or general question for students.

    Args:
        question (str): The question asked by the student.

    Returns:
        dict: Response dictionary containing status and answer or error.
    """
    if not question or not question.strip():
        return {
            "status": "error",
            "message": "Please enter a question to ask EduGenie."
        }

    # Prepare student-friendly educational prompt
    prompt = f"""
You are EduGenie, a friendly, encouraging, and highly knowledgeable AI learning assistant for students.

Please answer the following student question in a clear, concise, and educational manner:

Question:
\"\"\"{question.strip()}\"\"\"

Guidelines for your response:
1. Provide a direct, simple definition or explanation in 1-2 opening sentences.
2. Break down core concepts into easy-to-read bullet points.
3. Include an intuitive real-world example or analogy if relevant.
4. Conclude with a quick summary takeaway.
5. Keep the tone supportive, polite, and student-friendly.
"""

    return call_gemini_api(prompt)
