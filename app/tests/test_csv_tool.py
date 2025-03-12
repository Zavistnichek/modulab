from fastapi.testclient import TestClient
from services.csv_tool.main import app
import io

client = TestClient(app)


def test_read_root():
    """
    Test for the root endpoint "/"
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the csv_tool API!"}


def test_upload_csv_valid_file():
    """
    Test for uploading a valid CSV file.
    """
    # Create a sample CSV file in memory
    csv_data = "col1,col2\n1,2\n3,4"
    file = io.BytesIO(csv_data.encode("utf-8"))
    files = {"file": ("test.csv", file, "text/csv")}

    response = client.post("/upload-csv/", files=files)
    assert response.status_code == 200
    assert response.json() == [{"col1": 1, "col2": 2}, {"col1": 3, "col2": 4}]


def test_upload_csv_invalid_file_extension():
    """
    Test for uploading a file with an invalid extension.
    """
    # Create a non-CSV file in memory
    file = io.BytesIO(b"Invalid file content")
    files = {"file": ("test.txt", file, "text/plain")}

    response = client.post("/upload-csv/", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "The file must be a CSV with a valid filename"


def test_upload_csv_empty_file():
    """
    Test for uploading an empty file.
    """
    # Create an empty file in memory
    file = io.BytesIO(b"")
    files = {"file": ("test.csv", file, "text/csv")}

    response = client.post("/upload-csv/", files=files)
    assert response.status_code == 400
    assert "Error reading CSV file" in response.json()["detail"]
