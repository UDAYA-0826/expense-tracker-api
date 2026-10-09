# Expense Tracker API

Small FastAPI + SQLite service for tracking expenses.

## Run
```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test
```
pytest
```

## Endpoints
- `POST /expenses`, `GET /expenses`, `GET /expenses/{id}`, `DELETE /expenses/{id}`
- `GET /expenses/search?q=`, `GET /expenses/summary?month=YYYY-MM`
- `GET /reports/by-category`
