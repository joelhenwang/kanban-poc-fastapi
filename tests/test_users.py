from __future__ import annotations


def test_create_user_returns_id_and_name(client) -> None:
    # Create a user
    r = client.post("/users", json={"name": "Alice"})
    assert r.status_code == 201, r.text

    payload = r.json()
    assert "id" in payload
    assert isinstance(payload["id"], int)
    assert payload["name"] == "Alice"


def test_list_users_includes_created_user(client) -> None:
    client.post("/users", json={"name": "Alice"})
    client.post("/users", json={"name": "Bob"})

    r = client.get("/users")
    assert r.status_code == 200, r.text

    users = r.json()
    assert isinstance(users, list)
    names = {u["name"] for u in users}
    assert {"Alice", "Bob"}.issubset(names)


def test_list_users_supports_query_filter(client) -> None:
    client.post("/users", json={"name": "Alice"})
    client.post("/users", json={"name": "Bob"})

    r = client.get("/users", params={"q": "Ali"})
    assert r.status_code == 200, r.text
    users = r.json()
    assert all("Ali" in u["name"] for u in users)


def test_get_user_by_id_success(client) -> None:
    created = client.post("/users", json={"name": "Alice"}).json()
    user_id = created["id"]

    r = client.get(f"/users/{user_id}")
    assert r.status_code == 200, r.text
    fetched = r.json()
    assert fetched["id"] == user_id
    assert fetched["name"] == "Alice"


def test_get_user_by_id_404(client) -> None:
    r = client.get("/users/999999")
    assert r.status_code == 404, r.text


def test_update_user_changes_name(client) -> None:
    created = client.post("/users", json={"name": "Alice"}).json()
    user_id = created["id"]

    r = client.patch(f"/users/{user_id}", json={"name": "Alice Updated"})
    assert r.status_code == 200, r.text

    updated = r.json()
    assert updated["id"] == user_id
    assert updated["name"] == "Alice Updated"


def test_delete_user_204_and_then_404(client) -> None:
    created = client.post("/users", json={"name": "Alice"}).json()
    user_id = created["id"]

    r = client.delete(f"/users/{user_id}")
    assert r.status_code == 204, r.text

    r = client.get(f"/users/{user_id}")
    assert r.status_code == 404, r.text


def test_user_tasks_endpoints_empty_lists_when_no_tasks(client) -> None:
    user = client.post("/users", json={"name": "Alice"}).json()
    user_id = user["id"]

    r = client.get(f"/users/{user_id}/tasks/authored")
    assert r.status_code == 200, r.text
    assert r.json() == []

    r = client.get(f"/users/{user_id}/tasks/assigned")
    assert r.status_code == 200, r.text
    assert r.json() == []

    r = client.get(f"/users/{user_id}/tasks")
    assert r.status_code == 200, r.text
    combined = r.json()
    assert combined == {"authored": [], "assigned": []}


def test_user_tasks_endpoints_404_when_user_missing(client) -> None:
    r = client.get("/users/999999/tasks/authored")
    assert r.status_code == 404, r.text

    r = client.get("/users/999999/tasks/assigned")
    assert r.status_code == 404, r.text

    r = client.get("/users/999999/tasks")
    assert r.status_code == 404, r.text
