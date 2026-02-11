import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add the backend directory to the path so we can import the app
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.main import app
except ImportError:
    # Fallback for different environments
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
    from app.main import app
