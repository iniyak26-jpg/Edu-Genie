# EduGenie – Google Gemini Powered Learning Assistant 🎓✨

EduGenie is an intelligent, student-friendly educational web application built with **FastAPI** and powered by **Google Gemini AI**. It is designed to assist students with their day-to-day academic studies, homework doubts, revision, and concept mastery.

---

## 🌟 1. Features Overview

| Feature | Module | API Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **1. Instant Q&A** | `qna.py` | `POST /qa` | Ask academic and general questions to get clear, structured, and easy-to-understand answers. |
| **2. Concept Explanation** | `explanation_module.py` | `POST /explain` | Demystify difficult or technical topics using simple language, everyday analogies (Feynman technique), and real-world examples. |
| **3. 3-MCQ Interactive Quiz** | `quiz_module.py` | `POST /quiz` | Generate exactly 3 multiple-choice questions (with 4 options each), immediate score tracking, color-coded answers, and detailed explanations. |
| **4. Smart Summarization** | `summary_module.py` | `POST /summarize` | Condense long paragraphs, textbook chapters, or lecture notes into high-yield revision points without losing critical meaning. |
| **5. Learning Path Roadmap** | `learning_path.py` | `POST /learn/recommendations` | Generate structured, step-by-step learning roadmaps (Beginner → Basic → Intermediate → Advanced) with practical project ideas. |

---

## 💡 2. Technical Note on Explanation Module (LaMini-Flan-T5 vs Gemini)

- **LaMini-Flan-T5**: An open-source Seq2Seq transformer model that can run locally. However, running local transformers requires downloading heavy model weights (~1GB–3GB) and PyTorch, which frequently causes memory exhaustion, slow responses, and dependency installation issues on student laptops.
- **EduGenie's Solution**: `explanation_module.py` includes built-in architecture for both. It defaults to the **Google Gemini Cloud API** for lightning-fast, high-quality responses with zero disk overhead, while providing optional hook support for local models if PyTorch/Transformers are installed.

---

## 📁 3. Project Structure

```text
EduGenie/
│
├── main.py                  # FastAPI web server and routing
├── explanation_module.py    # Concept explanation logic (Gemini + Local Fallback)
├── qna.py                   # Educational Q&A module
├── quiz_module.py           # 3-question MCQ quiz generator & JSON parser
├── summary_module.py        # Text summarization module
├── learning_path.py         # Step-by-step learning roadmap generator
│
├── requirements.txt         # Project dependencies
├── .env.example             # Example environment variables template
├── .env                     # Your private API keys (never commit to Git)
├── .gitignore               # Excludes secrets, cache, and virtual environments
├── README.md                # Project documentation and guide
│
├── templates/
│   └── index.html           # Student-friendly interactive UI (Jinja2)
│
└── static/
    └── style.css            # Modern responsive CSS styling & animations
```

---

## 🚀 4. Installation & Setup Guide

### Step 1: Clone or Navigate to the Project Directory
```bash
cd EduGenie
```

### Step 2: Create and Activate a Python Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Your Gemini API Key
1. Get a free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/).
2. Copy `.env.example` to create a new file named `.env`:
   ```bash
   cp .env.example .env
   ```
   *(On Windows PowerShell, use: `copy .env.example .env`)*
3. Open `.env` and paste your API key:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   ```

---

## ▶️ 5. Running the Application

Start the local FastAPI development server:
```bash
uvicorn main:app --reload
```

Once running, open your web browser and visit:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🔄 6. How the Application Works

```
┌──────────────────────────────────────────────────────────────┐
│             Student Web Browser (index.html)                 │
│  - Select task (Explain, Q&A, Quiz, Summary, Learning Path)  │
│  - Enter question / text & click "Generate with EduGenie"    │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP POST (fetch)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Server (main.py)                 │
│  - GET  /                     -> Serves HTML UI              │
│  - POST /qa                   -> Calls qna.py                │
│  - POST /explain              -> Calls explanation_module.py │
│  - POST /quiz                 -> Calls quiz_module.py        │
│  - POST /summarize            -> Calls summary_module.py     │
│  - POST /learn/recommendations-> Calls learning_path.py      │
└──────────────────────────────┬───────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
     [qna.py]        [explanation_module.py] [quiz_module.py]
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    Google Gemini API                         │
│  - Processes prompt with pedagogical educational guidance    │
│  - Returns structured response / validated JSON              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧪 7. Testing & Quality Assurance

You can test all aspects of the application directly from the web interface or via API testing tools (like Postman or curl):

1. **Test Q&A**:
   - Select `Q&A` → Enter `"What is photosynthesis?"` → Click **Generate**.
2. **Test Explanation**:
   - Select `Explain` → Enter `"Explain artificial intelligence"` → Click **Generate**.
3. **Test Practice Quiz**:
   - Select `Quiz` → Enter `"Python Data Structures"` → Click **Generate**.
   - Click each option in the result card to verify instant feedback (green for correct, red for wrong + explanation).
4. **Test Summary**:
   - Select `Summary` → Paste a multi-sentence paragraph → Click **Generate**.
5. **Test Learning Path**:
   - Select `Recommend Path` → Enter `"SQL"` → Click **Generate**.
6. **Edge Case Tests**:
   - **Empty Input**: Clear the text area and click Generate. An alert message `"Input Required"` will appear.
   - **Missing API Key**: If `.env` is empty or invalid, the backend returns a clear guide instead of crashing.
   - **Invalid AI Output**: `quiz_module.py` features regex sanitization and fallback structuring to ensure malformed JSON never crashes the backend.

---

## 👥 8. GitHub Collaboration Guide (For a Team of 4 Students)

To collaborate smoothly without merge conflicts or leaking secrets:

### 1. Repository Setup (Team Leader)
```bash
# Initialize Git
git init
git add .
git commit -m "Initial commit: EduGenie learning assistant"
git branch -M main
git remote add origin https://github.com/your-username/EduGenie.git
git push -u origin main
```

### 2. Recommended Feature Branching Workflow
Each of the 4 team members works on a dedicated feature branch:

- **Member 1 (UI/Frontend)**: `git checkout -b feature/ui-enhancements`
- **Member 2 (Q&A & Explanation)**: `git checkout -b feature/qna-explain`
- **Member 3 (Quiz & Summary)**: `git checkout -b feature/quiz-summary`
- **Member 4 (Learning Path & API)**: `git checkout -b feature/learning-path`

### 3. Daily Collaboration Steps
```bash
# 1. Before starting, pull the latest changes from main
git checkout main
git pull origin main

# 2. Switch to your feature branch and merge latest main
git checkout feature/your-feature
git merge main

# 3. Make your changes and commit
git add .
git commit -m "Add new quiz difficulty option"

# 4. Push your branch to GitHub
git push origin feature/your-feature

# 5. Create a Pull Request (PR) on GitHub for team review before merging into main!
```

> [!CAUTION]
> **API Key Safety Rule**: Never remove `.env` from `.gitignore`. Always share API keys privately through secure channels, never via GitHub commits.

---

## 📜 License & Credits

- Built for academic demonstration and student learning.
- Powered by **Google Gemini API** and **FastAPI**.
