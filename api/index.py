import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add the root directory to sys.path so we can import from 'backend'
# Vercel structure: /var/task (root)
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Try different pathing strategies for Vercel vs Local
try:
    # Try absolute import from the backend directory
    from backend.app.main import app
except ImportError as e:
    print(f"Primary import failed: {e}")
    try:
        # Try adding the specific app parent to path
        sys.path.insert(0, os.path.join(root_path, "backend"))
        from app.main import app
    except ImportError as e2:
        print(f"Secondary import failed: {e2}")
        raise e2
