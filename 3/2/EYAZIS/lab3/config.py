import os
from urllib.parse import urlparse
try:
    from dotenv import load_dotenv
    # Explicitly load .env from current directory
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/corpus_db")
url = urlparse(DATABASE_URL)

DATABASE_CONFIG = {
    'host': url.hostname or 'localhost',
    'port': url.port or 5432,
    'user': url.username or 'postgres',
    'password': url.password or 'postgres',
    'database': url.path[1:].split('?')[0] or 'corpus_db'
}
