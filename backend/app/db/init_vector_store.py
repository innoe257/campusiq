import psycopg2
from app.core.config import get_settings

def init_vector_store():
    settings = get_settings()
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor()
    
    with open('app/db/init_vector_store.sql', 'r') as f:
        sql = f.read()
    
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    print("Vector store initialized successfully")

if __name__ == "__main__":
    init_vector_store()
