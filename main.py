from fastmcp import FastMCP
import os
import sqlite3

# Database path
DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "expenses.db"
)
CATEGORIES_PATH=os.path.join(os.path.dirname(__file__),"categories.json")

# Create MCP server
mcp = FastMCP("ExpenseTracker") #server ka name h - expenses tracker


# -----------------------------
# Initialize Database
# -----------------------------

def init_db(): #kuch bhi name ho sakta , we use init-db coz db initialize karo
    with sqlite3.connect(DB_PATH) as c: #yeh table create katrne ke liye use kiya
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)


# Create database/table when server starts
init_db()


# -----------------------------
# MCP Tool 1: Add Expense
# -----------------------------

@mcp.tool()
def add_expense( #aab data insert karna h isliye db se connection chahiye
    date,
    amount,
    category,
    subcategory="", #means optional parameter h ..agr kuch provide nhi karte to empty str show hoga.
    note=""
):
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """
            INSERT INTO expenses
            (date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (date, amount, category, subcategory, note)
        )

        return {
            "status": "ok",
            "id": cur.lastrowid #Jo row abhi-abhi insert hui hai, uska generated ID kya hai?
        }


# -----------------------------
# MCP Tool 2: List Expenses
# -----------------------------

@mcp.tool()
def list_expenses(start_date,end_date):
    """List expense enteries within an inclusive date range"""
    with sqlite3.connect(DB_PATH) as c:
        #c.execute() khud “show” nahi karta; woh SELECT query execute karta hai. Uske baad fetchall() actual rows nikalta hai.
        cur = c.execute(""" 
            SELECT
                id,
                date,
                amount,
                category,
                subcategory,
                note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
        """,
        (start_date,end_date))
        #cur.description se query ke col names milenge
        cols = [d[0] for d in cur.description]

        return [
            dict(zip(cols, row))
            for row in cur.fetchall()
        ]

@mcp.tool()
def summarize(start_date, end_date, category=None):
    """Summarize expenses by category within an inclusive date range."""

    with sqlite3.connect(DB_PATH) as c:

        query = """
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """

        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"

        cur = c.execute(query, params)

        cols = [d[0] for d in cur.description]

        return [
            dict(zip(cols, row))
            for row in cur.fetchall()
        ]

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


# -----------------------------
# Start MCP Server
# -----------------------------

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )