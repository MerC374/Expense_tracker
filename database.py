import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def get_connection():
    conn = sqlite3.connect('expense.db')
    conn.row_factory = sqlite3.Row # let us access columns by name
    return conn

def create_table():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses(
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Category TEXT NOT NULL,
        Amount REAL NOT NULL,
        Description TEXT,
        Date TEXT NOT NULL
        )
    ''') 
    conn.commit()
    conn.close()

def add_expense(amount, category, description):
    conn = get_connection()
    conn.execute(
        'INSERT INTO Expenses (Amount, Category, Description, Date) VALUES(?, ?, ?, ?)', (amount, category, description, datetime.now().strftime('%Y-%m-%d'))
    )
    conn.commit()
    conn.close()

def get_all_expenses():
    conn = get_connection()
    expenses = conn.execute(
        'SELECT * FROM Expenses ORDER BY Date DESC'
    ).fetchall()
    conn.close()
    return [dict(row) for row in expenses]
  
def get_weekly_summary():
    conn = get_connection()
    summary = conn.execute('''
        SELECT Category as category, SUM(Amount) as total 
        FROM Expenses
        WHERE Date >= Date('now', '-7 days')
        GROUP BY Category
    ''').fetchall()
    conn.close()
    return [dict(row) for row in summary]

def reset_expenses():
    conn = get_connection()
    conn.execute('DELETE FROM Expenses')
    conn.commit()
    conn.close()

def get_ai_insights(summary):
    if not summary:
        return "Add some expeneses this week to get AI insights!"
    
    # Format summary data into readable text for the AI
    summary_text = "\n".join(
        [f'- {row["category"]} : ₹{row["total"]:.2f}' for row in summary]
    )
    total = sum(row["total"] for row in summary)

    prompt = f"""
    A college student's weekly expense summary:
    {summary_text}
    Total spent: ₹{total:.2f}

    Give 2-3 short, friendly, and practical money-saving insights based on this data. Be specific to the categories shown. Keep it under 80 words. No bullet pounts, just plain sentences.
    """

    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI insights unavailable: {str(e)}"