from llm import get_llm
from database import save_message, load_recent_history
from langchain_core.messages import HumanMessage, AIMessage
from memory_manager import summarize_if_needed
from database import load_summary



SYSTEM_PROMPT = """
You are a professional financial assistant.

Formatting Rules:
- Always use structured format.
- Use headings with bold text.
- Use bullet points for clarity.
- Break answers into logical sections.
- Keep responses concise and professional.

Content Rules:
- Only answer finance-related topics.
- Provide educational guidance, not guaranteed investment advice.
- Include a short professional disclaimer at the end when relevant.
"""

llm = get_llm()

print("Financial Assistant Ready")

session_id = input("Enter User ID: ")

summarize_if_needed(session_id,llm)
summary=load_summary(session_id)
recent_history=load_recent_history(session_id,limit=15)
messages=[]
if summary:
    messages.append(HumanMessage(content=f"Conversation summary: {summary}"))
messages.append(HumanMessage(content=SYSTEM_PROMPT))

for role, msg in recent_history:
    if role == "user":
        messages.append(HumanMessage(content=msg))
    else:
        messages.append(AIMessage(content=msg))
        
        
        
while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    # Save user message
    save_message(session_id, "user", user_input)

    # Load history
    history_rows = load_recent_history(session_id)

    messages = [HumanMessage(content=SYSTEM_PROMPT)]

    for role, msg in history_rows:
        if role == "user":
            messages.append(HumanMessage(content=msg))
        else:
            messages.append(AIMessage(content=msg))

    response = llm.invoke(messages)

    print("Bot:", response.content)

    save_message(session_id, "bot", response.content)
