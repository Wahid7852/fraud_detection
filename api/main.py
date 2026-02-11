import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add the project root and backend directory to sys.path
# This ensures that 'backend.app.main' or 'app.main' can be found at runtime
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_dir)
backend_path = os.path.join(root_path, "backend")

if root_path not in sys.path:
    sys.path.insert(0, root_path)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import the FastAPI app instance
# We use a robust import strategy to handle both Vercel and local environments
try:
    # Try importing from the project root (standard Vercel/local behavior)
    from backend.app.main import app
except ImportError:
    # Fallback for environments where 'backend' is the root or sys.path is different
    # We use a type ignore here because the linter cannot trace the sys.path modification above
    try:
        from app.main import app # type: ignore
    except ImportError as e:
        print(f"Failed to import FastAPI app: {e}")
        raise

# Ensure 'app' is explicitly available for Vercel's handler detection
app = app
