"""Test configuration loading"""

import pytest
from app.core.config import settings


def test_settings_loaded():
    """Test that settings are loaded correctly"""
    assert settings.APP_NAME == "Smart Portfolio Manager"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.DB_HOST is not None
    assert settings.DB_PORT is not None
    assert settings.LLM_API_URL is not None


def test_database_url_construction():
    """Test that database URL is constructed correctly"""
    db_url = settings.DATABASE_URL
    assert "mysql+pymysql://" in db_url
    assert settings.DB_HOST in db_url
    assert str(settings.DB_PORT) in db_url
