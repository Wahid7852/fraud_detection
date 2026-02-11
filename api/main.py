import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add the root directory to sys.path so we can import from 'backend'
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Import the app from the backend directory
try:
    from backend.app.main import app
except ImportError:
    # Fallback for different environments
    sys.path.insert(0, os.path.join(root_path, "backend"))
    from app.main import app
