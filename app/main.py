from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import db

db.init_db()
app = FastAPI(title="Expense Tracker API")


class ExpenseIn(BaseModel):
    description: str = Field(min_length=1)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)


@app.post("/expenses", status_code=201)
def create_expense(expense: ExpenseIn):
    with db.get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO expenses (description, amount, category) VALUES (?, ?, ?)",
            (expense.description, expense.amount, expense.category),
        )
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


@app.get("/expenses")
def list_expenses():
    with db.get_conn() as conn:
        rows = conn.execute("SELECT * FROM expenses ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@app.get("/expenses/search")
def search_expenses(q: str):
    """Find expenses whose description contains the query text."""
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM expenses WHERE description LIKE '%" + q + "%' ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/expenses/summary")
def monthly_summary(month: str, top: int = 3):
    """Summary for a month given as YYYY-MM: total, count, average and top expenses."""
    try:
        with db.get_conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM expenses WHERE created_at LIKE '{month}%' ORDER BY amount DESC"
            ).fetchall()
        total = sum(r["amount"] for r in rows)
        return {
            "month": month,
            "total": total,
            "count": len(rows),
            "average": total / len(rows),
            "top": [dict(r) for r in rows[: top + 1]],
        }
    except Exception:
        return {"month": month, "total": 0, "count": 0, "average": 0, "top": []}


@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int):
    with db.get_conn() as conn:
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return dict(row)


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    with db.get_conn() as conn:
        cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Expense not found")


@app.get("/reports/by-category")
def report_by_category():
    """Total and count of expenses per category, sorted by category name."""
    result = []
    with db.get_conn() as conn:
        categories = conn.execute(
            "SELECT DISTINCT category FROM expenses ORDER BY category"
        ).fetchall()
        for c in categories:
            row = conn.execute(
                "SELECT SUM(amount) AS total, COUNT(*) AS n FROM expenses WHERE category = ?",
                (c["category"],),
            ).fetchone()
            result.append({"category": c["category"], "total": round(row["total"], 2), "count": row["n"]})
    return result
