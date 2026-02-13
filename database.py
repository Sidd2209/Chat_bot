import sqlite3
from datetime import datetime

conn = sqlite3.connect("chat_memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    session_id TEXT,
    role TEXT,
    message TEXT,
    timestamp TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS summaries (
    session_id TEXT PRIMARY KEY,
    summary TEXT
)
""")
conn.commit()

def save_summary(session_id, summary):
    cursor.execute("""
                   INSERT into summaries(session_id, summary)
                   values(?,?)
                   ON CONFLICT(session_id) DO UPDATE SET summary=excluded.summary
                   """,(session_id,summary)
                   )
    conn.commit()
    
    
def load_summary(session_id):
    cursor.execute(" select summary from summaries where session_id=?",(session_id,))
    row=cursor.fetchone()
    return row[0] if row else None

def save_message(session_id, role, message):
    cursor.execute(
        "INSERT INTO conversations VALUES (?, ?, ?, ?)",
        (session_id, role, message, str(datetime.now()))
    )
    conn.commit()

def load_recent_history(session_id, limit=20):
    cursor.execute("""
        SELECT role, message FROM conversations
        WHERE session_id=?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (session_id, limit))
    rows = cursor.fetchall()
    return rows[::-1]  # reverse order
