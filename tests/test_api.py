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


def test_list_filters_by_category(client):
    add(client, category="food")
    add(client, category="travel")
    rows = client.get("/expenses", params={"category": "travel"}).json()
    assert len(rows) == 1 and rows[0]["category"] == "travel"


def test_list_pagination(client):
    for i in range(5):
        add(client, description=f"e{i}")
    page = client.get("/expenses", params={"limit": 2, "offset": 2}).json()
    assert [r["description"] for r in page] == ["e2", "e3"]


def test_list_rejects_bad_limit(client):
    assert client.get("/expenses", params={"limit": 0}).status_code == 422
    assert client.get("/expenses", params={"limit": 101}).status_code == 422
