from fastapi import FastAPI
from pydantic import BaseModel
from database import save_message, load_recent_history
from llm import get_llm
from langchain_core.messages import HumanMessage, AIMessage
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
import sys

@app.get("/version")
def version():
    return {"python_version": sys.version}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat-bot-kohl-three.vercel.app"],   # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


llm = get_llm()

SYSTEM_PROMPT = """
You are a professional financial assistant.
Answer ONLY finance-related topics.
Be logical, clear, and professional.
"""

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
def chat(request: ChatRequest):

    session_id = request.session_id
    user_input = request.message

    save_message(session_id, "user", user_input)

    history_rows = load_recent_history(session_id, limit=15)

    messages = [HumanMessage(content=SYSTEM_PROMPT)]

    for role, msg in history_rows:
        if role == "user":
            messages.append(HumanMessage(content=msg))
        else:
            messages.append(AIMessage(content=msg))

    response = llm.invoke(messages)

    save_message(session_id, "bot", response.content)

    return {"response": response.content}
