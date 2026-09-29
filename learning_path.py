"""
=============================================================================
EduGenie - Learning Path Module (learning_path.py)
=============================================================================
Purpose:
    Generates a structured, step-by-step roadmap for any subject, skill, or
    academic topic from Beginner to Advanced levels.

Structure Generated:
    1. Level 1: Foundations (Prerequisites & Core Definitions)
    2. Level 2: Basic Concepts (Hands-on beginner topics)
    3. Level 3: Intermediate Concepts (Real-world techniques & tools)
    4. Level 4: Advanced Concepts (Expert mastery & optimization)
    5. Hands-on Project Ideas & Recommended Free Learning Resources
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
    Helper function to send learning roadmap prompt to Google Gemini API.
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

    error_msg = f"Gemini API Error: {last_error}" if last_error else "Failed to generate learning path. Please check your API key."
    return {
        "status": "error",
        "message": error_msg
    }


def generate_learning_path(topic: str) -> dict:
    """
    Creates a comprehensive educational learning path for a given topic.

    Args:
        topic (str): The subject, technology, or academic field (e.g., 'SQL', 'Data Science').

    Returns:
        dict: Standardized response with status and generated markdown roadmap.
    """
    # 1. Validate topic input
    if not topic or not topic.strip():
        return {
            "status": "error",
            "message": "Please enter a topic or skill to generate a learning path (e.g., 'SQL', 'Web Development')."
        }

    # 2. Prepare structured roadmap prompt
    prompt = f"""
You are an expert curriculum designer and career mentor for EduGenie.
Create a structured, step-by-step learning roadmap for a student who wants to master:

🎯 Target Topic: \"\"\"{topic.strip()}\"\"\"

Please follow this clean, structured outline:

### 🌟 1. Overview & Prerequisites
- Brief summary of what this topic is and where it is used.
- Recommended background or prerequisite skills (if any).

---

### 🟢 2. Stage 1: Beginner (Foundations)
- **Core Concepts to Learn**: (Bullet points of foundational topics)
- **Estimated Time**: (e.g., 1-2 weeks)
- **Practice Activity**: A beginner mini-exercise.

---

### 🟡 3. Stage 2: Basic Concepts (Building Confidence)
- **Key Topics**: (Core syntax, basic operations, standard patterns)
- **Estimated Time**: (e.g., 2-3 weeks)
- **Mini-Project Idea**: A starter project to consolidate basics.

---

### 🟠 4. Stage 3: Intermediate (Real-World Applications)
- **Key Topics**: (Optimization, popular frameworks/libraries, design patterns)
- **Estimated Time**: (e.g., 3-4 weeks)
- **Intermediate Project**: A portfolio-worthy project idea.

---

### 🔴 5. Stage 4: Advanced & Mastery
- **Key Topics**: (High-performance concepts, architecture, edge cases, industry best practices)
- **Estimated Time**: (Ongoing / Advanced)
- **Capstone Project**: An end-to-end production-grade project challenge.

---

### 📚 6. Recommended Resources & Next Steps
- Recommended documentation, free courses, or interactive platforms.
- Pro-tips for staying consistent and building a portfolio.
"""

    return call_gemini_api(prompt)
