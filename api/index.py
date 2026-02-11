import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add the backend directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
