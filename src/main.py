"""
Entry point for AI Translate application.
Run: python -m src.main
"""

import sys
import os

# Ensure the project root is in the Python path
# so that 'from src.xxx import ...' works correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import run

if __name__ == "__main__":
    run()
