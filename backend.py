import os
import sqlite3
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# DB path
DB_PATH = "chat_history.db"

# Ensure DB & table exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS chats (
        chat_id TEXT,
        role TEXT,
        message TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# Initialize Groq LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=GROQ_API_KEY,
)

# Prompt template
prompt = ChatPromptTemplate.from_template("""
You are Doctor AI, a medical/healthcare assistant.
- If the user asks about medical/healthcare topics → answer normally.
- If the question is outside medical/healthcare → reply: "I don’t know, I am only trained for medical/healthcare questions."
- If a PDF or image is uploaded but NOT healthcare related → reply: "This file is not healthcare related, so I cannot answer."
Question: {question}
""")

def generate_response(chat_id: str, user_message: str) -> str:
    """Generate response and save to DB"""
    chain = prompt | llm
    response = chain.invoke({"question": user_message}).content

    # Fresh DB connection
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO chats (chat_id, role, message) VALUES (?, ?, ?)", (chat_id, "user", user_message))
    c.execute("INSERT INTO chats (chat_id, role, message) VALUES (?, ?, ?)", (chat_id, "assistant", response))
    conn.commit()
    conn.close()

    return response

def get_chat_history(chat_id: str):
    """Fetch chat history"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role, message FROM chats WHERE chat_id=?", (chat_id,))
    rows = c.fetchall()
    conn.close()
    return rows
