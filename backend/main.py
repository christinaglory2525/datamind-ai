from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.agent import process_question

app = FastAPI(
    title="DataMind AI",
    description="Conversational Database Intelligence Agent",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
CHARTS_DIR = FRONTEND_DIR / "charts"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/charts",
    StaticFiles(directory=str(CHARTS_DIR)),
    name="charts"
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/api/health")
def health():
    return {
        "message": "DataMind AI is running!",
        "status": "online"
    }


@app.post("/api/ask")
def ask_database(request: QuestionRequest):

    if not request.question.strip():
        return {
            "success": False,
            "error": "Please enter a question."
        }

    return process_question(request.question)


# IMPORTANT: keep this LAST
# This makes your frontend publicly accessible
app.mount(
    "/",
    StaticFiles(
        directory=str(FRONTEND_DIR),
        html=True
    ),
    name="frontend"
)