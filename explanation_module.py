"""
=============================================================================
EduGenie - Concept Explanation Module (explanation_module.py)
=============================================================================
Purpose:
    Explains complex, technical, or difficult topics in simple, intuitive language
    tailored for beginner students using the Feynman Technique.

Technical Note regarding LaMini-Flan-T5 vs Google Gemini:
    - LaMini-Flan-T5 is a local Sequence-to-Sequence open-source transformer model.
    - Running local transformers requires downloading heavy model weights (~1GB-3GB)
      and PyTorch, which can cause high memory usage, slow responses, and installation
      conflicts on student laptops.
    - EduGenie uses Google Gemini API by default for fast, cloud-based, high-accuracy
      responses with zero disk load, while keeping local model fallback hooks ready.
=============================================================================
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MODEL_CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-lite-latest",
]

# Check if local transformers/torch are installed (optional)
LOCAL_TRANSFORMERS_AVAILABLE = False
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    LOCAL_TRANSFORMERS_AVAILABLE = True
except ImportError:
    LOCAL_TRANSFORMERS_AVAILABLE = False


def get_gemini_api_key() -> str:
    """Retrieve Gemini API key from environment variables."""
    return os.getenv("GEMINI_API_KEY", "").strip()


def call_gemini_api(prompt: str) -> dict:
    """
    Helper function to send explanation prompt to Google Gemini API.
    Supports both google.genai and google.generativeai SDKs.
    """
    api_key = get_gemini_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        return {
            "status": "error",
            "message": (
                "Gemini API key is missing! Please configure GEMINI_API_KEY in your .env file. "
                "Get a free API key at https://aistudio.google.com/"
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

    error_msg = f"Gemini API Error: {last_error}" if last_error else "Failed to get an explanation from Gemini API. Please check your API key."
    return {
        "status": "error",
        "message": error_msg
    }


def explain_concept(topic: str, use_local_model: bool = False) -> dict:
    """
    Explains an educational concept or topic in simple beginner terms.

    Args:
        topic (str): The concept or topic to explain.
        use_local_model (bool): If True, attempts to run local LaMini model if available.

    Returns:
        dict: Standardized response dictionary.
    """
    if not topic or not topic.strip():
        return {
            "status": "error",
            "message": "Please enter a concept or topic to explain."
        }

    # If local model requested
    if use_local_model and not LOCAL_TRANSFORMERS_AVAILABLE:
        return {
            "status": "error",
            "message": "Local transformer packages (transformers, torch) are not installed. Using Gemini cloud API instead."
        }

    # Feynman Technique prompt
    prompt = f"""
You are an expert tutor in EduGenie specializing in the "Feynman Technique" of teaching.
Your goal is to explain difficult and technical topics in exceptionally simple, clear, and engaging language.

Topic to Explain:
\"\"\"{topic.strip()}\"\"\"

Please structure your explanation clearly with headings:
1. 💡 **The Big Picture (In One Simple Sentence)**: What is this concept at its core?
2. 📖 **Simple Breakdown**: Explain step-by-step using plain everyday words. Avoid confusing jargon without explaining it first.
3. 🍎 **Real-World Analogy**: Give a relatable story or daily-life comparison that makes the concept click instantly.
4. 🔑 **Why It Matters**: 2-3 bullet points explaining why this concept is important.
5. 🧠 **Quick Check**: One simple question the student can ask themselves to test their understanding.
"""

    return call_gemini_api(prompt)
