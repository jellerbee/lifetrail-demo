"""
Database migration script to add new columns to existing events table
"""
from sqlalchemy import text
from .db import engine

def migrate_database():
    """Add new columns to events table if they don't exist"""
    with engine.connect() as conn:
        # Check if processing_status column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'events' AND column_name = 'processing_status'
        """))
        
        if not result.fetchone():
            print("Adding processing_status column...")
            conn.execute(text("""
                ALTER TABLE events 
                ADD COLUMN processing_status VARCHAR(32) DEFAULT 'completed'
            """))
            conn.commit()
        
        # Check if ai_results column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'events' AND column_name = 'ai_results'
        """))
        
        if not result.fetchone():
            print("Adding ai_results column...")
            conn.execute(text("""
                ALTER TABLE events 
                ADD COLUMN ai_results JSON
            """))
            conn.commit()
        
        print("Database migration completed!")

if __name__ == "__main__":
    migrate_database()