from . import db


def category_report() -> list[dict]:
    """Per-category totals and counts using a single aggregate query."""
    with db.get_conn() as conn:
        rows = conn.execute(
            """
            SELECT category, SUM(amount) AS total, COUNT(*) AS n
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
            """
        ).fetchall()
    return [{"category": r["category"], "total": r["total"], "count": r["n"]} for r in rows]
