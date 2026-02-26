from llm import get_llm
from database import save_message, load_recent_history
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from memory_manager import summarize_if_needed
from database import load_summary
from prompt import SYSTEM_PROMPT

llm = get_llm()

print("Financial Assistant Ready")

session_id = input("Enter User ID: ")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    # Save user message
    save_message(session_id, "user", user_input)

    # ⭐ refresh summary memory
    summarize_if_needed(session_id, llm)
    summary = load_summary(session_id)

    # Load history
    history_rows = load_recent_history(session_id, limit=15)

    # ⭐ Build message stack
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    if summary:
        messages.append(SystemMessage(content=f"Conversation summary: {summary}"))

    for role, msg in history_rows:
        if role == "user":
            messages.append(HumanMessage(content=msg))
        else:
            messages.append(AIMessage(content=msg))

    response = llm.invoke(messages)

    print("Bot:", response.content)

    save_message(session_id, "bot", response.content)