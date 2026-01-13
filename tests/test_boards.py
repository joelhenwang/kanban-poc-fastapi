from __future__ import annotations

from typing import Any


def test_create_board(client: Any) -> None:
    """
    Purpose:
    - Ensure POST /boards creates a board and returns the expected shape.

    Expected behavior:
    - Returns HTTP 201
    - Response contains at least: id, name, created_at
    """
    r = client.post("/boards", json={"name": "Board A"})
    assert r.status_code == 201, r.text
    data = r.json()

    assert isinstance(data["id"], int)
    assert data["name"] == "Board A"
    assert "created_at" in data


def test_list_boards_empty_then_populated(client: Any) -> None:
    """
    Purpose:
    - Ensure GET /boards returns a list and that created boards appear in it.

    Expected behavior:
    - Returns HTTP 200
    - Returns [] when empty
    - Returns created boards after insertion
    """
    r = client.get("/boards")
    assert r.status_code == 200, r.text
    assert r.json() == []

    client.post("/boards", json={"name": "Board A"})
    client.post("/boards", json={"name": "Board B"})

    r = client.get("/boards")
    assert r.status_code == 200, r.text
    names = [b["name"] for b in r.json()]
    assert "Board A" in names
    assert "Board B" in names


def test_list_boards_query_filter(client: Any) -> None:
    """
    Purpose:
    - Ensure GET /boards supports substring name filtering using `q`.

    Expected behavior:
    - Returns only boards whose name contains the query substring.
    """
    client.post("/boards", json={"name": "Engineering"})
    client.post("/boards", json={"name": "Marketing"})

    r = client.get("/boards", params={"q": "Eng"})
    assert r.status_code == 200, r.text
    names = [b["name"] for b in r.json()]
    assert "Engineering" in names
    assert "Marketing" not in names


def test_get_board_by_id(client: Any) -> None:
    """
    Purpose:
    - Ensure GET /boards/{board_id} returns the created board.

    Expected behavior:
    - Returns HTTP 200
    - Response matches the created board id/name
    """
    created = client.post("/boards", json={"name": "Board A"}).json()
    board_id = created["id"]

    r = client.get(f"/boards/{board_id}")
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["id"] == board_id
    assert data["name"] == "Board A"


def test_update_board_name(client: Any) -> None:
    """
    Purpose:
    - Ensure PATCH /boards/{board_id} updates the board name.

    Expected behavior:
    - Returns HTTP 200
    - Name is updated
    """
    created = client.post("/boards", json={"name": "Old Name"}).json()
    board_id = created["id"]

    r = client.patch(f"/boards/{board_id}", json={"name": "New Name"})
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["id"] == board_id
    assert data["name"] == "New Name"

    # Verify persistence via GET
    r = client.get(f"/boards/{board_id}")
    assert r.status_code == 200, r.text
    assert r.json()["name"] == "New Name"


def test_delete_board(client: Any) -> None:
    """
    Purpose:
    - Ensure DELETE /boards/{board_id} deletes a board.

    Expected behavior:
    - Returns HTTP 204
    - Subsequent GET returns 404
    """
    created = client.post("/boards", json={"name": "Board A"}).json()
    board_id = created["id"]

    r = client.delete(f"/boards/{board_id}")
    assert r.status_code == 204, r.text

    r = client.get(f"/boards/{board_id}")
    assert r.status_code == 404, r.text


def test_get_board_tasks_empty(client: Any) -> None:
    """
    Purpose:
    - Ensure GET /boards/{board_id}/tasks returns an empty list when the board has no tasks.

    Expected behavior:
    - Returns HTTP 200
    - Returns []
    """
    created = client.post("/boards", json={"name": "Board A"}).json()
    board_id = created["id"]

    r = client.get(f"/boards/{board_id}/tasks")
    assert r.status_code == 200, r.text
    assert r.json() == []
