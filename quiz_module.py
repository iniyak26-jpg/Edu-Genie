"""
=============================================================================
EduGenie - Quiz Generation Module (quiz_module.py)
=============================================================================
Purpose:
    Generates exactly 3 multiple-choice questions (MCQs) for any given topic
    or educational passage using Google Gemini.

Key Features:
    - Generates 3 MCQs with exactly 4 options each.
    - Identifies correct answer and student-friendly explanation.
    - Robust JSON sanitization and parsing to prevent application crashes.
=============================================================================
"""

import os
import json
import re
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


def get_gemini_api_key() -> str:
    """Retrieve Gemini API key from environment variables."""
    return os.getenv("GEMINI_API_KEY", "").strip()


def clean_json_string(raw_text: str) -> str:
    """
    Strips markdown code blocks, backticks, and extra commentary to extract pure JSON.
    """
    if not raw_text:
        return ""

    text = raw_text.strip()

    # Remove markdown code block fences
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()
        else:
            text = text.replace("```json", "").replace("```", "").strip()

    # Find JSON array [...] or object {...}
    array_match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", text)
    if array_match:
        return array_match.group(0).strip()

    obj_match = re.search(r"\{[\s\S]*\}", text)
    if obj_match:
        return obj_match.group(0).strip()

    return text


def validate_and_format_quiz(quiz_data) -> list:
    """
    Ensures quiz questions adhere strictly to the expected format:
    List of 3 dicts: 'id', 'question', 'options' (list of 4), 'correct_answer', 'explanation'.
    """
    if isinstance(quiz_data, dict):
        for key in ["questions", "quiz", "data", "items"]:
            if key in quiz_data and isinstance(quiz_data[key], list):
                quiz_data = quiz_data[key]
                break

    if not isinstance(quiz_data, list) or len(quiz_data) == 0:
        raise ValueError("Quiz output is not a valid list of questions.")

    formatted = []
    for idx, item in enumerate(quiz_data[:3], start=1):
        if not isinstance(item, dict):
            continue

        question = item.get("question", f"Question {idx}").strip()
        raw_options = item.get("options", [])
        
        # Ensure exactly 4 options as strings
        if isinstance(raw_options, dict):
            options = [f"{k}: {v}" for k, v in raw_options.items()]
        elif isinstance(raw_options, list):
            options = [str(opt).strip() for opt in raw_options]
        else:
            options = ["Option A", "Option B", "Option C", "Option D"]

        while len(options) < 4:
            options.append(f"Option {chr(65 + len(options))}")
        options = options[:4]

        correct_answer = str(item.get("correct_answer", options[0])).strip()
        explanation = str(item.get("explanation", "Great job testing your knowledge!")).strip()

        formatted.append({
            "id": idx,
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation
        })

    if not formatted:
        raise ValueError("Could not extract valid questions from AI output.")

    return formatted


def generate_quiz(topic_or_text: str) -> dict:
    """
    Generates a 3-question MCQ quiz based on topic or input passage.

    Args:
        topic_or_text (str): Topic name or text passage.

    Returns:
        dict: Standard response with status, quiz list, or error details.
    """
    if not topic_or_text or not topic_or_text.strip():
        return {
            "status": "error",
            "message": "Please provide a topic or passage to generate a quiz."
        }

    api_key = get_gemini_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        return {
            "status": "error",
            "message": (
                "Gemini API key is missing! Please set GEMINI_API_KEY in your .env file. "
                "Get a free API key at https://aistudio.google.com/"
            )
        }

    prompt = f"""
You are an expert educational quiz creator for EduGenie.
Generate EXACTLY 3 multiple-choice questions (MCQs) for students based on the following topic or text:

Topic / Content:
\"\"\"{topic_or_text.strip()}\"\"\"

CRITICAL RULES:
1. Generate EXACTLY 3 questions.
2. Each question MUST have EXACTLY 4 distinct, educational options.
3. Clearly identify the correct answer (matching one of the 4 option strings exactly).
4. Provide a brief 1-2 sentence explanation for why the answer is correct.
5. Return ONLY a valid JSON array. Do not include markdown code fences or any conversational text.

Expected JSON Structure:
[
  {{
    "id": 1,
    "question": "What is ...?",
    "options": [
      "Option 1",
      "Option 2",
      "Option 3",
      "Option 4"
    ],
    "correct_answer": "Option 1",
    "explanation": "Because..."
  }},
  {{
    "id": 2,
    "question": "Which of the following ...?",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "correct_answer": "Option B",
    "explanation": "Because..."
  }},
  {{
    "id": 3,
    "question": "Why does ...?",
    "options": [
      "Option 1",
      "Option 2",
      "Option 3",
      "Option 4"
    ],
    "correct_answer": "Option 3",
    "explanation": "Because..."
  }}
]
"""

    last_error = None
    # Try modern google.genai SDK
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
                    cleaned = clean_json_string(response.text)
                    parsed = json.loads(cleaned)
                    formatted_quiz = validate_and_format_quiz(parsed)
                    return {
                        "status": "success",
                        "data": formatted_quiz,
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
                    cleaned = clean_json_string(response.text)
                    parsed = json.loads(cleaned)
                    formatted_quiz = validate_and_format_quiz(parsed)
                    return {
                        "status": "success",
                        "data": formatted_quiz,
                        "model_used": f"Google Gemini ({model_name})"
                    }
            except Exception as e:
                last_error = str(e)
                continue
    except Exception as e:
        last_error = str(e)

    error_msg = f"Quiz generation error: {last_error}" if last_error else "Failed to generate quiz. Please check your Gemini API key."
    return {
        "status": "error",
        "message": error_msg
    }
