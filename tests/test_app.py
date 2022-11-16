"""
Test app.py
"""
import pytest
from app import subscribe


def test_app_subscribe():
    """
    Test app.subscribe()
    """
    response = subscribe()
    assert response == False
