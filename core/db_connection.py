# db_connection.py
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "car_manual_db")
        self.user = os.getenv("DB_USER", "car_manual_user")
        self.password = os.getenv("DB_PASSWORD", "car_manual_password")
        self.connection: Optional[psycopg2.extensions.connection] = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print(f"✓ Connected to database: {self.database}")
            return self.connection
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute a query."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            print(f"✗ Query error: {e}")
            raise
        finally:
            cursor.close()
    
    def enable_pgvector(self):
        """Enable pgvector extension."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            self.connection.commit()
            cursor.close()
            print("✓ pgvector extension enabled")
        except Exception as e:
            print(f"✗ Error enabling pgvector: {e}")
            raise