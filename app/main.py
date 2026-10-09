from typing import Optional

from fastapi import FastAPI, HTTPException, Query
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
def list_expenses(
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List expenses, optionally filtered by category, with limit/offset pagination."""
    sql = "SELECT * FROM expenses"
    params: list = []
    if category:
        sql += " WHERE category = ?"
        params.append(category)
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    params += [limit, offset]
    with db.get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


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
