"""Entry point для Corpus Manager с автоматической настройкой и запуском."""
import subprocess
import sys
import time
import os
import webbrowser
from urllib.parse import urlparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(SCRIPT_DIR, "frontend")


def install_python_deps():
    print("Checking Python dependencies...")
    try:
        import fastapi
        import psycopg2
        import bs4
        import dotenv
    except ImportError:
        print("Installing required Python packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def setup_database():
    print("Checking PostgreSQL database...")
    # Fix for UnicodeDecodeError on Windows when Postgres returns non-utf8 error messages
    os.environ["PGCLIENTENCODING"] = "utf-8"
    
    db_url = os.getenv("DATABASE_URL")
    print(f"DEBUG: DATABASE_URL from env: {db_url}")
    if not db_url:
        # Check if we should use a default or ask? Let's try default but with better error
        db_url = "postgresql://postgres:postgres@localhost/corpus_db"

    # Add client_encoding to URL if not present
    if "client_encoding" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url += f"{separator}client_encoding=utf8"
    
    from sqlalchemy import create_engine
    from sqlalchemy.exc import OperationalError
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    engine = create_engine(db_url)
    try:
        conn = engine.connect()
        conn.close()
    except (OperationalError, UnicodeDecodeError) as e:
        # If we get a UnicodeDecodeError, it's almost certainly a connection failure 
        # (like wrong password) where the error message is in a local encoding (e.g. CP1251).
        print("-" * 40)
        print("DATABASE CONNECTION FAILED!")
        
        if isinstance(e, UnicodeDecodeError):
            print("Error: Could not decode the error message from PostgreSQL.")
            print("This usually happens when the connection fails (e.g. wrong password) ")
            print("and PostgreSQL sends a localized error message.")
        else:
            print(f"Error: {e}")
            
        print("\nPlease check:")
        print("1. Is PostgreSQL running?")
        print("2. Are the credentials in your connection string correct?")
        print(f"   Current URL: {db_url.split('@')[0]}@...")
        print("3. Does the database exist? (If not, I will try to create it below)")
        print("-" * 40)
        
        # Try to create database if it's potentially a "does not exist" issue
        # We need to connect to 'postgres' to create 'corpus_db'
        print("Attempting to connect to 'postgres' database to ensure 'corpus_db' exists...")
        import config
        
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                host=config.DATABASE_CONFIG['host'],
                port=config.DATABASE_CONFIG['port'],
                user=config.DATABASE_CONFIG['user'],
                password=config.DATABASE_CONFIG['password'],
                client_encoding='utf8'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            # Check if exists first helper
            database = config.DATABASE_CONFIG['database']
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{database}'")
            exists = cur.fetchone()
            if not exists:
                print(f"Creating database '{database}'...")
                cur.execute(f"CREATE DATABASE {database}")
                print(f"Database '{database}' created successfully.")
            else:
                print(f"Database '{database}' already exists. The error might be due to wrong password or permissions.")
            cur.close()
            conn.close()
        except Exception as ce:
            print(f"Failed to connect to PostgreSQL to check/create database: {ce}")
            print("\nSUGGESTION: Please create the database manually or set a valid DATABASE_URL environment variable.")
            print("Example: set DATABASE_URL=postgresql://user:password@localhost:5432/corpus_db")
            sys.exit(1)
            
    # Initialize schema
    from corpus.models import CorpusDB
    print("Initializing database schema...")
    CorpusDB(db_url)
    print("Database is ready.")


def setup_frontend():
    print("Checking frontend setup...")
    node_modules_path = os.path.join(FRONTEND_DIR, "node_modules")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    
    if not os.path.exists(node_modules_path):
        print("Installing frontend dependencies (this might take a minute)...")
        subprocess.check_call([npm_cmd, "install"], cwd=FRONTEND_DIR)
        print("Frontend dependencies installed.")


def main():
    print("=" * 60)
    print("  Corpus Manager — Automated Startup")
    print("=" * 60)
    print()

    install_python_deps()
    
    # Load .env now that dependencies are installed
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(SCRIPT_DIR, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"Loaded environment from: {env_path}")
        else:
            print(f"Warning: .env file not found at {env_path}")
    except ImportError:
        print("Warning: python-dotenv not installed. Environment variables from .env will be ignored.")

    setup_database()
    setup_frontend()

    print("\nStarting servers...")
    
    fastapi_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=SCRIPT_DIR,
    )

    time.sleep(3)

    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    react_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=FRONTEND_DIR,
    )

    print("\n" + "=" * 60)
    print("Project is running!")
    print("Backend API: http://localhost:8000")
    print("Frontend URL: http://localhost:5173")
    print("Press Ctrl+C in this console to shut down both servers.")
    print("=" * 60 + "\n")

    time.sleep(2)
    webbrowser.open("http://localhost:5173")

    try:
        fastapi_proc.wait()
        react_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping servers gracefully...")
        fastapi_proc.terminate()
        react_proc.terminate()
        fastapi_proc.wait()
        react_proc.wait()
        print("Servers stopped.")


if __name__ == "__main__":
    main()
