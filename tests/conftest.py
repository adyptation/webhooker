"""
Pytest configurations and fixtures.
"""
import os
import tempfile
import pytest
import app as myapp


@pytest.fixture
def flaskapp():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = myapp.start({"TESTING": True, "DATABASE": db_path})

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(flaskapp):
    """A test client for the app."""
    return flaskapp.test_client()
