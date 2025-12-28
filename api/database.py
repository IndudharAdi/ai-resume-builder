import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Use a local SQLite database for development
# In production on Vercel, this should be swapped for a Postgres URL via env var

# Debug logging
print("Checking environment variables for database connection...", flush=True)
for key in ["DATABASE_URL", "POSTGRES_URL", "POSTGRES_URL_NON_POOLING", "POSTGRES_PRISMA_URL"]:
    val = os.getenv(key)
    if val:
        print(f"Found {key}: {val[:15]}... (Length: {len(val)})", flush=True)

# Helper to clean URL
def clean_database_url(url):
    if not url:
        return url
    
    # 1. Start by fixing the scheme for SQLAlchemy
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    # 2. Remove 'supa' query parameter which breaks psycopg2
    if "supa=" in url:
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            if 'supa' in qs:
                print("Removing unsupported 'supa' parameter from URL", flush=True)
                del qs['supa']
                new_query = urlencode(qs, doseq=True)
                url = urlunparse(parsed._replace(query=new_query))
        except Exception as e:
            print(f"Warning: Failed to clean URL parameters: {e}", flush=True)
            
    return url

# Prioritize NON_POOLING (Session mode) for compatibility
raw_url = (
    os.getenv("POSTGRES_URL_NON_POOLING")
    or os.getenv("POSTGRES_URL")
    or os.getenv("DATABASE_URL")
    or os.getenv("POSTGRES_PRISMA_URL")
)

SQLALCHEMY_DATABASE_URL = clean_database_url(raw_url) or "sqlite:///./sql_app.db"

print(f"Selected Database URL (Cleaned): {SQLALCHEMY_DATABASE_URL[:15]}...", flush=True)

check_same_thread = False
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    check_same_thread = {"check_same_thread": False}
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args=check_same_thread
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

