"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.core.config import Config


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_config(temp_config_dir):
    """Create a test configuration."""
    config = Config(
        username="test_user",
        user_id="test-uuid-1234",
        config_dir=temp_config_dir,
    )
    config.ensure_directories()
    return config
