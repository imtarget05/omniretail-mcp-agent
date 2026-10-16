"""
Database connection pool and helper functions for Retail FastMCP Server
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

NEON_CLOUD_URL = "postgresql://neondb_owner:npg_SEnl7VFHrOC6@ep-spring-lake-ao6ij6s5-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
DATABASE_URL = os.environ.get("DATABASE_URL") or NEON_CLOUD_URL
PG_HOST = os.environ.get("POSTGRES_HOST", "localhost")
PG_PORT = int(os.environ.get("POSTGRES_PORT", "5433"))
PG_USER = os.environ.get("POSTGRES_USER", "retail_admin")
PG_PASS = os.environ.get("POSTGRES_PASSWORD", "retail_password")
PG_DB = os.environ.get("POSTGRES_DB", "retail_ecosystem")

@contextmanager
def get_db_cursor():
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASS,
            dbname=PG_DB,
            cursor_factory=RealDictCursor
        )
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
