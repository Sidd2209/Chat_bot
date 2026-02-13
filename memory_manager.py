from langchain_core.messages import HumanMessage
from database import load_recent_history,  save_summary, load_summary

def summarize_if_needed(session_id,llm,threshold=30):
    history = load_recent_history(session_id, limit=100)
    if (len(history)>threshold):
        return
    text_block= "\n".join([f"{r}: {m}" for r, m in history])
    prompt = f"""
    Summarize the following financial conversation clearly.
    Focus on user goals, financial data, and decisions.

    {text_block}
    """
    response=llm.invoke([HumanMessage(content=prompt)])
    save_summary(session_id,response.content)
    