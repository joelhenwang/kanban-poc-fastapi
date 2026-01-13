from __future__ import annotations

from typing import Any


def _create_user(client, name: str) -> dict[str, Any]:
    r = client.post("/users", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()


def _create_board(client, name: str) -> dict[str, Any]:
    r = client.post("/boards", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()


def test_create_task_minimal(client):
    """
    Create a task with the minimum required fields.
    """
    payload = {
        "name": "Task 1",
        "description": "First task",
        "status": "todo",
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 200, r.text

    task = r.json()
    assert isinstance(task["id"], int)
    assert task["name"] == payload["name"]
    assert task["description"] == payload["description"]
    assert task["status"] == payload["status"]
    assert "created_at" in task
    assert "updated_at" in task


def test_create_task_with_board_author_assignee(client):
    """
    Create a task associated to a board, with an author + single assignee.
    """
    board = _create_board(client, "Board A")
    author = _create_user(client, "Alice")
    assignee = _create_user(client, "Bob")

    payload = {
        "name": "Task with relations",
        "description": "Has board, author, assignee",
        "status": "in_progress",
        "board_id": board["id"],
        "author_id": author["id"],
        "assignee_id": assignee["id"],
    }

    r = client.post("/tasks", json=payload)
    assert r.status_code == 200, r.text
    task = r.json()

    assert task["board_id"] == board["id"]
    assert task["author_id"] == author["id"]
    assert task["assignee_id"] == assignee["id"]
    assert task["status"] == "in_progress"


def test_get_task_by_id(client):
    """
    Create a task then fetch it by id.
    """
    created = client.post(
        "/tasks",
        json={"name": "Fetch me", "description": "desc", "status": "todo"},
    ).json()

    r = client.get(f"/tasks/{created['id']}")
    assert r.status_code == 200, r.text
    task = r.json()
    assert task["id"] == created["id"]
    assert task["name"] == "Fetch me"


def test_get_task_not_found(client):
    """
    GET /tasks/{id} should return 404 for a missing task.
    """
    r = client.get("/tasks/9999999")
    assert r.status_code == 404


def test_list_tasks_filters_by_board_and_author_and_status(client):
    """
    Exercise GET /tasks filters:
    - board_id
    - author_id
    - status
    """
    board_a = _create_board(client, "Board A")
    board_b = _create_board(client, "Board B")
    alice = _create_user(client, "Alice")
    bob = _create_user(client, "Bob")

    # Task 1: board_a, alice, todo
    client.post(
        "/tasks",
        json={
            "name": "A1",
            "description": "d",
            "status": "todo",
            "board_id": board_a["id"],
            "author_id": alice["id"],
        },
    )
    # Task 2: board_a, bob, done
    client.post(
        "/tasks",
        json={
            "name": "A2",
            "description": "d",
            "status": "done",
            "board_id": board_a["id"],
            "author_id": bob["id"],
        },
    )
    # Task 3: board_b, alice, in_progress
    client.post(
        "/tasks",
        json={
            "name": "B1",
            "description": "d",
            "status": "in_progress",
            "board_id": board_b["id"],
            "author_id": alice["id"],
        },
    )

    # Filter by board_id
    r = client.get("/tasks", params={"board_id": board_a["id"]})
    assert r.status_code == 200, r.text
    tasks = r.json()
    assert all(t["board_id"] == board_a["id"] for t in tasks)

    # Filter by author_id
    r = client.get("/tasks", params={"author_id": alice["id"]})
    assert r.status_code == 200, r.text
    tasks = r.json()
    assert all(t["author_id"] == alice["id"] for t in tasks)

    # Filter by status (note alias is "status" not "status_")
    r = client.get("/tasks", params={"status": "done"})
    assert r.status_code == 200, r.text
    tasks = r.json()
    assert all(t["status"] == "done" for t in tasks)


def test_update_task_fields_and_assignee(client):
    """
    PATCH /tasks/{id} should update mutable fields (name/description/status/board_id/assignee_id).
    """
    board_a = _create_board(client, "Board A")
    board_b = _create_board(client, "Board B")
    assignee = _create_user(client, "Bob")

    task = client.post(
        "/tasks",
        json={
            "name": "Old",
            "description": "Old desc",
            "status": "todo",
            "board_id": board_a["id"],
        },
    ).json()

    r = client.patch(
        f"/tasks/{task['id']}",
        json={
            "name": "New",
            "description": "New desc",
            "status": "done",
            "board_id": board_b["id"],
            "assignee_id": assignee["id"],
        },
    )
    assert r.status_code == 200, r.text
    updated = r.json()

    assert updated["id"] == task["id"]
    assert updated["name"] == "New"
    assert updated["description"] == "New desc"
    assert updated["status"] == "done"
    assert updated["board_id"] == board_b["id"]
    assert updated["assignee_id"] == assignee["id"]


def test_delete_task(client):
    """
    DELETE /tasks/{id} should return 204 and then the task should be gone.
    """
    task = client.post(
        "/tasks",
        json={"name": "To delete", "description": "d", "status": "todo"},
    ).json()

    r = client.delete(f"/tasks/{task['id']}")
    assert r.status_code == 204, r.text

    r = client.get(f"/tasks/{task['id']}")
    assert r.status_code == 404


def test_task_relationship_loader_endpoints(client):
    """
    Smoke-test the relationship loader endpoints:
    - GET /tasks/{id}/author
    - GET /tasks/{id}/board
    """
    board = _create_board(client, "Board A")
    author = _create_user(client, "Alice")

    task = client.post(
        "/tasks",
        json={
            "name": "Rel",
            "description": "d",
            "status": "todo",
            "board_id": board["id"],
            "author_id": author["id"],
        },
    ).json()

    r = client.get(f"/tasks/{task['id']}/author")
    assert r.status_code == 200, r.text
    assert r.json()["id"] == task["id"]

    r = client.get(f"/tasks/{task['id']}/board")
    assert r.status_code == 200, r.text
    assert r.json()["id"] == task["id"]
