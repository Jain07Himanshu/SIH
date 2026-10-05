import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import init_db

if __name__ == "__main__":
    print("Initializing database tables...")
    init_db()
    print("Database initialization complete.")
