
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import json
from .autogen_helper import generate_study_plan

from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True), name="static")

DB_PATH = os.path.join(os.path.dirname(__file__), 'learning_helper.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        name TEXT NOT NULL,
        FOREIGN KEY(topic_id) REFERENCES topics(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        description TEXT,
        link TEXT,
        step_order INTEGER,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        question TEXT,
        answer TEXT,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )''')
    conn.commit()
    conn.close()


init_db()

class TopicRequest(BaseModel):
    topic: str

class CategoryDetail(BaseModel):
    name: str
    details: List[str]
    links: List[str]

class Quiz(BaseModel):
    question: str
    answer: str

class StudyPlanResponse(BaseModel):
    topic: str
    categories: List[CategoryDetail]
    quizzes: List[Quiz]



@app.post("/generate_plan", response_model=StudyPlanResponse)
def generate_plan(req: TopicRequest):
    try:
        plan_json = generate_study_plan(req.topic)
        plan = json.loads(plan_json)
        categories = []
        quizzes = []
        for cat in plan["categories"]:
            categories.append(
                CategoryDetail(
                    name=cat["name"],
                    details=cat.get("details", []),
                    links=cat.get("links", [])
                )
            )
            for q in cat.get("quizzes", []):
                quizzes.append(Quiz(question=q["question"], answer=q["answer"]))
        # DB 저장 생략 (실제 구현 시 저장)
        return StudyPlanResponse(topic=req.topic, categories=categories, quizzes=quizzes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
