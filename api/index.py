import sys
import os

# Ensure root directory is in sys.path for Vercel Serverless Function imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.app.main import app

# Vercel entrypoint handler
handler = app
