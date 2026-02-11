import sys
import os
import traceback
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
    from backend.app.main import app as backend_app
    app = backend_app
except Exception as e:
    print(f"Primary import failed: {e}")
    print(traceback.format_exc())
    try:
        # Fallback for environments where 'backend' is the root or sys.path is different
        from app.main import app as fallback_app # type: ignore
        app = fallback_app
    except Exception as e2:
        print(f"Secondary import failed: {e2}")
        print(traceback.format_exc())
        
        # Create a minimal app as a final fallback to show the error
        from fastapi import FastAPI
        app = FastAPI()
        @app.get("/api/health")
        def health():
            return {"status": "error", "error": str(e2), "traceback": traceback.format_exc()}
        
        @app.get("/api/{full_path:path}")
        def catch_all(full_path: str):
            return {"error": "Backend import failed", "details": str(e2)}

# Ensure 'app' is explicitly available for Vercel's handler detection
app = app
