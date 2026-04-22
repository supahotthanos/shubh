"""Pytest config — make `app.*` importable from tests run at the project root."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
