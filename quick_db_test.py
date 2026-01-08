# quick_db_test.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    print("✓ Connection successful!")
    print(f"  Host: {os.getenv('DB_HOST')}")
    print(f"  Database: {os.getenv('DB_NAME')}")
    print(f"  User: {os.getenv('DB_USER')}")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✓ PostgreSQL version: {version[0][:50]}...")
    
    cursor.close()
    conn.close()
    print("✓ Connection closed")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print(f"\nEnvironment variables:")
    print(f"  DB_HOST: {os.getenv('DB_HOST')}")
    print(f"  DB_PORT: {os.getenv('DB_PORT')}")
    print(f"  DB_NAME: {os.getenv('DB_NAME')}")
    print(f"  DB_USER: {os.getenv('DB_USER')}")
    print(f"  DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', ''))}")