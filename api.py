from fastapi import FastAPI
from pydantic import BaseModel
from database import save_message, load_recent_history
from llm import get_llm
from langchain_core.messages import HumanMessage, AIMessage
from fastapi.middleware.cors import CORSMiddleware
from prompt import SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from memory_manager import summarize_if_needed
from database import load_summary
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://chat-bot-kohl-three.vercel.app",
        "https://chat-bot-frontend-rw1t.onrender.com"],   # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import sys

@app.get("/version")
def version():
    return {"python_version": sys.version}





llm = get_llm()



class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
def chat(request: ChatRequest):

    session_id = request.session_id
    raw_user_input = request.message
    user_input = raw_user_input + "\nRespond in BYRZ tone."

    # save clean message
    save_message(session_id, "user", raw_user_input)

    # refresh memory
    summarize_if_needed(session_id, llm)
    summary = load_summary(session_id)

    history_rows = load_recent_history(session_id, limit=15)

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    if summary:
        messages.append(SystemMessage(content=f"Conversation summary: {summary}"))

    for role, msg in history_rows:
        if role == "user":
            messages.append(HumanMessage(content=msg))
        else:
            messages.append(AIMessage(content=msg))

    # add current user message
    messages.append(HumanMessage(content=user_input))

    response = llm.invoke(messages)

    save_message(session_id, "bot", response.content)

    return {"response": response.content}