def add(client, description="Lunch", amount=10.5, category="food"):
    return client.post("/expenses", json={"description": description, "amount": amount, "category": category})


def test_create_and_get(client):
    r = add(client)
    assert r.status_code == 201
    got = client.get(f"/expenses/{r.json()['id']}")
    assert got.status_code == 200 and got.json()["description"] == "Lunch"


def test_validation_rejects_negative_amount(client):
    assert add(client, amount=-5).status_code == 422


def test_delete_and_404(client):
    eid = add(client).json()["id"]
    assert client.delete(f"/expenses/{eid}").status_code == 204
    assert client.get(f"/expenses/{eid}").status_code == 404


def test_report_by_category(client):
    add(client, amount=10.5, category="food")
    add(client, amount=4.5, category="food")
    add(client, amount=20, category="travel")
    assert client.get("/reports/by-category").json() == [
        {"category": "food", "total": 15.0, "count": 2},
        {"category": "travel", "total": 20.0, "count": 1},
    ]


def test_search_by_description(client):
    add(client, description="Coffee beans")
    add(client, description="Train ticket")
    rows = client.get("/expenses/search", params={"q": "coffee"}).json()
    assert [r["description"] for r in rows] == ["Coffee beans"]


def test_monthly_summary_totals(client):
    add(client, amount=10)
    add(client, amount=30)
    from datetime import date
    body = client.get("/expenses/summary", params={"month": date.today().strftime("%Y-%m")}).json()
    assert body["total"] == 40 and body["count"] == 2
