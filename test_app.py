from fastapi.testclient import TestClient
import os
import pytest

from app import app

client= TestClient(app)
VIDEO_DIR = "videos"
TEST_VIDEO = "test_video.mp4"

@pytest.fixture(scope="function")
def setup():
    """Cleanup function to remove test files after execution."""
    # Create test video file
    os.makedirs(VIDEO_DIR, exist_ok=True)  # Ensure directory exists
    test_file_path = os.path.join(VIDEO_DIR, TEST_VIDEO)

    with open(test_file_path, "wb") as f:
        f.write(b"fake video content")  # Simulate video content

    yield

    #Cleanup test folder
    if os.path.exists(test_file_path):
        os.remove(test_file_path)


def test_upload_video(setup):
    file_content = b"fake video content"
    files ={"file":(TEST_VIDEO,file_content,"video.mp4")}
    response = client.post("/upload/",files =files)

    assert response.status_code==200
    assert response.json() == {
        "filename":TEST_VIDEO,
        "message": "Video uploaded successfully"
    }
    saved_file_path = os.path.join(VIDEO_DIR, TEST_VIDEO)
    assert os.path.exists(saved_file_path)


def test_list_videos(setup):

    test_files = ["test_video1.mp4", "test_video2.mp4"]
    for file in test_files:
        with open(os.path.join(VIDEO_DIR, file), "w") as f:
            f.write("test content")

    response = client.get("/videos/")

    # Assert response
    assert response.status_code == 200
    assert set(response.json()["videos"]).issuperset(set(test_files))

def test_get_video(setup):
    response = client.get(f"/videos/{TEST_VIDEO}")

    # Validate response
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("video/")

    # Ensure content is returned
    assert response.content is not None

def test_delete_video(setup):

    assert os.path.exists(os.path.join(VIDEO_DIR, TEST_VIDEO))

    response = client.delete(f"/videos/{TEST_VIDEO}")

    assert response.status_code == 200
    assert response.json() == {"message": f"'{TEST_VIDEO}' deleted successfully"}
    assert not os.path.exists(os.path.join(VIDEO_DIR, TEST_VIDEO))

def test_delete_not_exist_video(setup):

    response = client.delete("/videos/non_existent.mp4")

    assert response.status_code == 404
    assert response.json() == {"detail": "Video name not found"}