import pytest
from fastapi.testclient import TestClient
from services.basic_list_operations.main import app, data_list

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_list():
    """Fixture to clear the list before each test"""
    data_list.clear()


def test_add_item():
    response = client.post("/add?item=apple")
    assert response.status_code == 200
    response_message = response.json()["message"]

    assert "Item" in response_message
    assert "apple" in response_message
    assert "added successfully" in response_message


def test_remove_item_success():
    data_list.append("apple")
    response = client.delete("/remove?item=apple")
    assert response.status_code == 200
    assert "Item" in response.json()["message"]
    assert "apple" in response.json()["message"]
    assert "removed successfully" in response.json()["message"]
    assert "apple" not in data_list


def test_remove_item_not_found():
    response = client.delete("/remove?item=banana")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item 'banana' not found."}


def test_search_item_found():
    data_list.extend(["apple", "banana", "orange"])
    response = client.get("/search?item=banana")
    assert response.status_code == 200
    assert response.json() == {"index": 1}


def test_search_item_not_found():
    data_list.append("apple")
    response = client.get("/search?item=banana")
    assert response.status_code == 200
    assert response.json() == {"index": -1}


def test_sort_list():
    data_list.extend(["banana", "apple", "orange"])
    response = client.get("/sort")
    assert response.status_code == 200
    assert response.json() == {"sorted_list": ["apple", "banana", "orange"]}


def test_get_length():
    data_list.extend(["apple", "banana"])
    response = client.get("/length")
    assert response.status_code == 200
    assert response.json() == {"length": 2}


def test_consecutive_operations():
    client.post("/add?item=banana")
    client.post("/add?item=apple")

    response = client.get("/length")
    assert response.json()["length"] == 2

    response = client.get("/sort")
    assert response.json()["sorted_list"] == ["apple", "banana"]

    response = client.get("/search?item=banana")
    assert response.json()["index"] == 1

    client.delete("/remove?item=apple")
    response = client.get("/length")
    assert response.json()["length"] == 1


def test_error_handling():
    response = client.delete("/remove?item=apple")
    assert response.status_code == 404

    response = client.get("/search?item=apple")
    assert response.json()["index"] == -1

    response = client.get("/length")
    assert response.json()["length"] == 0
