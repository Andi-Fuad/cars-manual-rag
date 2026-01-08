# verify_storage.py
from core.db_connection import DatabaseConnection

db = DatabaseConnection()
db.connect()

# Check counts
chunks = db.execute_query("SELECT COUNT(*) FROM document_chunks;", fetch=True)
embeddings = db.execute_query("SELECT COUNT(*) FROM chunk_embeddings;", fetch=True)

print(f"Chunks stored: {chunks[0][0]}")
print(f"Embeddings stored: {embeddings[0][0]}")

# Sample a chunk
sample = db.execute_query("""
    SELECT chunk_text, page_number, section_header 
    FROM document_chunks 
    LIMIT 1;
""", fetch=True)

if sample:
    print(f"\nSample chunk:")
    print(f"  Page: {sample[0][1]}")
    print(f"  Section: {sample[0][2]}")
    print(f"  Text: {sample[0][0][:100]}...")

db.close()