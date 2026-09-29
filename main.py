"""
=============================================================================
EduGenie - Main FastAPI Application (main.py)
=============================================================================
Description:
    EduGenie is an AI-powered learning assistant for students built with FastAPI
    and Google Gemini AI.

Endpoints:
    - GET  /                     : Serves the student-friendly web interface
    - POST /qa                   : Answers student questions
    - POST /explain              : Explains difficult concepts in simple terms
    - POST /quiz                 : Generates a 3-question MCQ quiz with options
    - POST /summarize            : Summarizes long educational text
    - POST /learn/recommendations: Generates a step-by-step learning roadmap
    - GET  /api/health           : Health check & API key status verification
=============================================================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# Import EduGenie AI feature modules
import qna
import explanation_module
import quiz_module
import summary_module
import learning_path

# Load environment variables from .env
load_dotenv()

# Base project directory
BASE_DIR = Path(__file__).resolve().parent

# Initialize FastAPI application
app = FastAPI(
    title="EduGenie – Google Gemini Powered Learning Assistant",
    description="A simple, clean, and powerful educational assistant for students.",
    version="1.0.0"
)

# Enable CORS for cross-origin local testing if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS, assets)
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Configure Jinja2 HTML Templates
templates_dir = BASE_DIR / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))


# =============================================================================
# Request Data Models (Pydantic)
# =============================================================================
class GeneralRequest(BaseModel):
    """
    Flexible request model that accepts either 'input_text', 'question', 'topic', or 'text'.
    This makes frontend integration easy and beginner-friendly.
    """
    input_text: Optional[str] = Field(default=None, description="Main input text for any task")
    question: Optional[str] = Field(default=None, description="Question string for Q&A")
    topic: Optional[str] = Field(default=None, description="Topic name for Explain or Learning Path")
    text: Optional[str] = Field(default=None, description="Passage or text for Summary/Quiz")
    topic_or_text: Optional[str] = Field(default=None, description="Topic or passage for Quiz")

    def get_content(self) -> str:
        """Helper to extract the non-empty text input from any provided field."""
        for field in [self.input_text, self.question, self.topic, self.text, self.topic_or_text]:
            if field and field.strip():
                return field.strip()
        return ""


# =============================================================================
# Routes & Endpoints
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    """
    Serves the main EduGenie web application user interface.
    """
    api_key_configured = bool(
        os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here"
    )
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"api_key_configured": api_key_configured}
    )


@app.get("/api/health")
async def health_check():
    """
    Returns application and API key health status.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    is_configured = bool(api_key and api_key != "your_gemini_api_key_here")
    return {
        "status": "online",
        "app_name": "EduGenie",
        "api_key_configured": is_configured,
        "message": "EduGenie backend is active and ready." if is_configured else "Please add your GEMINI_API_KEY in the .env file."
    }


@app.post("/qa")
async def handle_qna(payload: GeneralRequest):
    """
    Endpoint 1: Q&A - Ask questions and receive concise, educational answers.
    """
    query = payload.get_content()
    if not query:
        raise HTTPException(status_code=400, detail="Please provide a valid question in your request.")

    result = qna.answer_question(query)
    if result.get("status") == "error":
        return JSONResponse(status_code=400, content=result)
    return result


@app.post("/explain")
async def handle_explain(payload: GeneralRequest):
    """
    Endpoint 2: Explanation - Explains difficult concepts in simple, student-friendly language.
    """
    topic = payload.get_content()
    if not topic:
        raise HTTPException(status_code=400, detail="Please provide a concept or topic to explain.")

    result = explanation_module.explain_concept(topic)
    if result.get("status") == "error":
        return JSONResponse(status_code=400, content=result)
    return result


@app.post("/quiz")
async def handle_quiz(payload: GeneralRequest):
    """
    Endpoint 3: Quiz - Generates exactly 3 MCQs with 4 options each and answers.
    """
    topic_or_text = payload.get_content()
    if not topic_or_text:
        raise HTTPException(status_code=400, detail="Please provide a topic or passage for the quiz.")

    result = quiz_module.generate_quiz(topic_or_text)
    if result.get("status") == "error":
        return JSONResponse(status_code=400, content=result)
    return result


@app.post("/summarize")
async def handle_summarize(payload: GeneralRequest):
    """
    Endpoint 4: Summary - Summarizes long educational text into key takeaways.
    """
    text = payload.get_content()
    if not text:
        raise HTTPException(status_code=400, detail="Please provide educational text to summarize.")

    result = summary_module.summarize_text(text)
    if result.get("status") == "error":
        return JSONResponse(status_code=400, content=result)
    return result


@app.post("/learn/recommendations")
async def handle_learning_path(payload: GeneralRequest):
    """
    Endpoint 5: Learning Path - Generates a structured roadmap from beginner to advanced.
    """
    topic = payload.get_content()
    if not topic:
        raise HTTPException(status_code=400, detail="Please provide a topic for the learning roadmap.")

    result = learning_path.generate_learning_path(topic)
    if result.get("status") == "error":
        return JSONResponse(status_code=400, content=result)
    return result


# Run locally if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
