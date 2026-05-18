"""
Pytest configuration for SafeFlow AI tests.
"""

import sys
from pathlib import Path

# Add the project root to sys.path so we can import ai_service
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Verify that ai_service can be imported
try:
    import ai_service
except ImportError:
    raise ImportError(f"Failed to import ai_service from {PROJECT_ROOT}")
