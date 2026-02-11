import sys
import os

# Add the backend directory to sys.path so 'app.main' can be imported
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import the FastAPI app instance from backend/app/main.py
try:
    from app.main import app
except ImportError as e:
    print(f"Error: Could not import FastAPI app from backend/app/main.py")
    print(f"Current sys.path: {sys.path}")
    raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
