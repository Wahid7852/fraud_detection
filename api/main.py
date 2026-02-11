import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add the project root and backend directory to sys.path
# This ensures that 'backend.app.main' or 'app.main' can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_dir)
backend_path = os.path.join(root_path, "backend")

if root_path not in sys.path:
    sys.path.insert(0, root_path)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import the FastAPI app instance
# We import it here so Vercel's 'api.main:app' entrypoint can find it
try:
    from backend.app.main import app
except ImportError:
    # Fallback for alternative directory structures
    from app.main import app

# Ensure 'app' is available at the module level for Vercel
app = app
