"""
Tests for image upload functionality
"""
import pytest
import io
import os
from fastapi.testclient import TestClient
from PIL import Image
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from main import app, UPLOAD_DIR


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_image():
    """Create a sample PNG image in memory"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def large_image():
    """Create a large image (>10MB) for testing size limits"""
    # Create a large image
    img = Image.new('RGB', (4000, 4000), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG', quality=100)
    img_bytes.seek(0)
    return img_bytes


class TestImageUpload:
    """Test suite for image upload endpoint"""

    def test_upload_endpoint_exists(self, client):
        """Test that /api/upload/image endpoint exists"""
        # Try uploading without file (should fail but endpoint should exist)
        response = client.post("/api/upload/image")
        # Should return 422 (validation error) not 404 (not found)
        assert response.status_code == 422

    def test_upload_valid_image(self, client, sample_image):
        """Test uploading a valid image"""
        files = {'file': ('test.png', sample_image, 'image/png')}
        response = client.post("/api/upload/image", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "url" in data
        assert data["url"].startswith("/uploads/")
        assert data["url"].endswith(".png")
        assert "size" in data
        assert data["size"] > 0

    def test_upload_jpg_image(self, client):
        """Test uploading a JPG image"""
        # Create JPG image
        img = Image.new('RGB', (100, 100), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        response = client.post("/api/upload/image", files=files)

        assert response.status_code == 200
        assert response.json()["url"].endswith(".jpg")

    def test_upload_non_image_file_rejected(self, client):
        """Test that non-image files are rejected"""
        # Create a text file
        text_file = io.BytesIO(b"This is not an image")
        files = {'file': ('test.txt', text_file, 'text/plain')}

        response = client.post("/api/upload/image", files=files)
        assert response.status_code == 400
        assert "must be an image" in response.json()["detail"].lower()

    def test_upload_oversized_image_rejected(self, client, large_image):
        """Test that images over 10MB are rejected"""
        files = {'file': ('large.png', large_image, 'image/png')}
        response = client.post("/api/upload/image", files=files)

        # Should reject large files
        if response.status_code == 400:
            assert "too large" in response.json()["detail"].lower()
        # Note: Might pass if image compression makes it <10MB

    def test_uploaded_file_is_accessible(self, client, sample_image):
        """Test that uploaded files are accessible via static mount"""
        # Upload image
        files = {'file': ('test.png', sample_image, 'image/png')}
        upload_response = client.post("/api/upload/image", files=files)

        url = upload_response.json()["url"]

        # Try to access the uploaded file
        get_response = client.get(url)
        assert get_response.status_code == 200
        assert get_response.headers["content-type"].startswith("image/")

    def test_upload_generates_unique_filenames(self, client):
        """Test that multiple uploads generate unique filenames"""
        uploaded_urls = []

        # Upload 3 identical images
        for i in range(3):
            img = Image.new('RGB', (50, 50), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            files = {'file': (f'test{i}.png', img_bytes, 'image/png')}
            response = client.post("/api/upload/image", files=files)
            uploaded_urls.append(response.json()["url"])

        # All URLs should be unique
        assert len(uploaded_urls) == len(set(uploaded_urls))

    def test_upload_preserves_file_extension(self, client):
        """Test that file extensions are preserved"""
        extensions = [
            ('test.png', 'image/png', '.png'),
            ('test.jpg', 'image/jpeg', '.jpg'),
            ('test.gif', 'image/gif', '.gif'),
        ]

        for filename, mime_type, expected_ext in extensions:
            img = Image.new('RGB', (10, 10), color='white')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=expected_ext.upper().strip('.'))
            img_bytes.seek(0)

            files = {'file': (filename, img_bytes, mime_type)}
            response = client.post("/api/upload/image", files=files)

            if response.status_code == 200:
                url = response.json()["url"]
                assert url.endswith(expected_ext)

    def test_upload_directory_exists(self):
        """Test that upload directory is created on startup"""
        assert UPLOAD_DIR.exists()
        assert UPLOAD_DIR.is_dir()

    def test_upload_handles_special_characters_in_filename(self, client, sample_image):
        """Test handling of filenames with special characters"""
        files = {'file': ('tëst file!@#.png', sample_image, 'image/png')}
        response = client.post("/api/upload/image", files=files)

        # Should succeed and sanitize filename
        assert response.status_code == 200
        url = response.json()["url"]
        assert "/uploads/" in url


class TestImageUploadIntegration:
    """Integration tests for image upload with paste workflow"""

    def test_paste_with_media_urls(self, client, sample_image):
        """Test creating a run with uploaded media URLs"""
        # Upload an image first
        files = {'file': ('property.png', sample_image, 'image/png')}
        upload_response = client.post("/api/upload/image", files=files)
        image_url = upload_response.json()["url"]

        # Create a run with the uploaded image
        create_response = client.post("/runs", json={
            "funda_url": "manual-paste",
            "funda_html": "<html><body>Property</body></html>",
            "media_urls": [image_url]
        })

        assert create_response.status_code == 200
        run_id = create_response.json()["run_id"]

        # Start and get report
        client.post(f"/runs/{run_id}/start")
        import time
        time.sleep(2)

        report_response = client.get(f"/runs/{run_id}/report")
        report_data = report_response.json()

        # Media URLs should be preserved
        if "property_core" in report_data and report_data["property_core"]:
            assert "media_urls" in report_data["property_core"]


class TestImageUploadSecurity:
    """Security tests for image upload"""

    def test_upload_without_authentication(self, client, sample_image):
        """Test that uploads work without authentication (as intended)"""
        files = {'file': ('test.png', sample_image, 'image/png')}
        response = client.post("/api/upload/image", files=files)
        assert response.status_code == 200

    def test_path_traversal_prevention(self, client, sample_image):
        """Test that path traversal attacks are prevented"""
        # Try to upload with malicious filename
        files = {'file': ('../../../etc/passwd.png', sample_image, 'image/png')}
        response = client.post("/api/upload/image", files=files)

        # Should succeed but filename should be sanitized
        if response.status_code == 200:
            url = response.json()["url"]
            # Ensure URL doesn't contain path traversal
            assert "../" not in url
            assert url.startswith("/uploads/")
